"""Resolve any PR comment id to a postable reply target.

Agents often pass numeric discussion ids, GraphQL node ids, or *child* reply
ids. GitHub's REST ``/pulls/.../comments/{id}/replies`` only accepts a
**top-level** review-comment id, and there is **no**
``/issues/comments/{id}/replies`` endpoint. This module classifies the id and
returns the correct post strategy so replies never fail with a vague
"thread not found".
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from _skill_cli import run_command

Kind = Literal["inline", "discussion", "review", "unknown"]
PostMethod = Literal["review_reply", "discussion_quote", "skip_review", "unresolved"]

_GRAPHQL_NODE = re.compile(r"^[A-Za-z0-9_=-]{10,}$")


@dataclass(frozen=True)
class CommentRecord:
    comment_id: str
    kind: Kind
    body: str
    in_reply_to_id: str | None = None
    node_id: str | None = None


@dataclass(frozen=True)
class ReplyTarget:
    """How to post a reply for a drafted ``## Comment <id>`` section."""

    input_id: str
    kind: Kind
    post_method: PostMethod
    reply_to_id: str | None
    """Top-level review-comment database id (inline) or discussion id."""
    body_snippet: str
    detail: str | None = None
    mcp_tool: str | None = None
    """Cursor GitHub MCP tool to use if gh posting fails."""
    mcp_hint: str | None = None


def _unwrap_body(raw: Any) -> str:
    if isinstance(raw, dict) and "wrapped" in raw:
        return str(raw.get("wrapped") or "")
    return str(raw or "")


def _as_id(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def build_comment_index(cache: dict[str, Any] | None) -> dict[str, CommentRecord]:
    """Index inline + discussion comments from fetch_pr_comments cache."""
    index: dict[str, CommentRecord] = {}
    if not isinstance(cache, dict):
        return index

    for item in cache.get("inline") or []:
        if not isinstance(item, dict):
            continue
        cid = _as_id(item.get("id"))
        if not cid:
            continue
        parent = _as_id(item.get("in_reply_to_id"))
        index[cid] = CommentRecord(
            comment_id=cid,
            kind="inline",
            body=_unwrap_body(item.get("body")),
            in_reply_to_id=parent,
            node_id=_as_id(item.get("node_id")),
        )

    discussion = cache.get("discussion") or {}
    disc_list = (
        discussion.get("comments")
        if isinstance(discussion, dict)
        else discussion
        if isinstance(discussion, list)
        else []
    )
    for item in disc_list or []:
        if not isinstance(item, dict):
            continue
        cid = _as_id(item.get("id"))
        if not cid:
            continue
        index[cid] = CommentRecord(
            comment_id=cid,
            kind="discussion",
            body=_unwrap_body(item.get("body")),
            in_reply_to_id=None,
            node_id=_as_id(item.get("node_id")),
        )

    for item in cache.get("reviews") or []:
        if not isinstance(item, dict):
            continue
        cid = _as_id(item.get("id"))
        if not cid:
            continue
        # Do not overwrite an inline/discussion id if somehow shared.
        if cid in index:
            continue
        index[cid] = CommentRecord(
            comment_id=cid,
            kind="review",
            body=_unwrap_body(item.get("body")),
        )
    return index


def walk_to_root(comment_id: str, index: dict[str, CommentRecord]) -> str:
    """Follow in_reply_to_id until the top-level review comment."""
    seen: set[str] = set()
    current = comment_id
    while current in index and current not in seen:
        seen.add(current)
        parent = index[current].in_reply_to_id
        if not parent:
            return current
        current = parent
    return current


def ensure_quote_reply(body: str, parent_snippet: str) -> str:
    """Discussion IssueComments have no nest API — quote the parent."""
    stripped = body.strip()
    if stripped.startswith(">"):
        return stripped
    snippet = parent_snippet.strip() or "(original discussion comment)"
    # Keep quote short so the reply stays readable.
    lines = [ln.rstrip() for ln in snippet.splitlines() if ln.strip()][:6]
    quoted = "\n".join(f"> {ln}" if ln else ">" for ln in lines) or "> (original)"
    return f"{quoted}\n\n{stripped}"


def _gh_get_json(root: Path, endpoint: str) -> tuple[dict[str, Any] | None, str | None]:
    raw = run_command(["gh", "api", endpoint, "-H", "Accept: application/vnd.github+json"], root)
    if raw.startswith("[exit") or raw.startswith("[error]"):
        return None, raw[:400]
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None, "non-JSON response"
    if not isinstance(data, dict):
        return None, "unexpected JSON shape"
    if data.get("message") and data.get("status") in {"404", 404}:
        return None, str(data.get("message"))
    return data, None


def _live_lookup_review_comment(
    root: Path, repo: str, comment_id: str
) -> CommentRecord | None:
    data, err = _gh_get_json(root, f"repos/{repo}/pulls/comments/{comment_id}")
    if err or not data:
        return None
    return CommentRecord(
        comment_id=str(data.get("id") or comment_id),
        kind="inline",
        body=str(data.get("body") or ""),
        in_reply_to_id=_as_id(data.get("in_reply_to_id")),
        node_id=_as_id(data.get("node_id")),
    )


def _live_lookup_issue_comment(
    root: Path, repo: str, comment_id: str
) -> CommentRecord | None:
    data, err = _gh_get_json(root, f"repos/{repo}/issues/comments/{comment_id}")
    if err or not data:
        return None
    return CommentRecord(
        comment_id=str(data.get("id") or comment_id),
        kind="discussion",
        body=str(data.get("body") or ""),
        node_id=_as_id(data.get("node_id")),
    )


def _resolve_graphql_node(
    root: Path, node_id: str
) -> tuple[str | None, str | None, str | None]:
    """Return (typename, database_id, error)."""
    query = (
        "query($id:ID!){ node(id:$id){ __typename "
        "... on PullRequestReviewComment { databaseId body replyTo { databaseId } } "
        "... on IssueComment { databaseId body } "
        "... on PullRequestReview { databaseId } } }"
    )
    raw = run_command(
        ["gh", "api", "graphql", "-f", f"query={query}", "-f", f"id={node_id}"],
        root,
    )
    if raw.startswith("[exit") or raw.startswith("[error]"):
        return None, None, raw[:200]
    try:
        data = json.loads(raw)
        node = (data.get("data") or {}).get("node") or {}
        typename = node.get("__typename")
        db = node.get("databaseId")
        if db is None:
            return typename, None, f"no databaseId for {typename or node_id}"
        return str(typename), str(db), None
    except json.JSONDecodeError:
        return None, None, "graphql non-JSON"


def find_review_thread_id(
    root: Path, repo: str, pr: int, review_comment_id: str
) -> str | None:
    """Locate GraphQL PullRequestReviewThread id containing ``review_comment_id``."""
    if "/" not in repo:
        return None
    owner, name = repo.split("/", 1)
    query = """
    query($owner:String!,$name:String!,$number:Int!,$cursor:String){
      repository(owner:$owner,name:$name){
        pullRequest(number:$number){
          reviewThreads(first:100, after:$cursor){
            pageInfo{ hasNextPage endCursor }
            nodes{
              id
              comments(first:100){ nodes{ databaseId } }
            }
          }
        }
      }
    }
    """
    cursor: str | None = None
    target = str(review_comment_id)
    for _ in range(20):  # hard cap pages
        args = [
            "gh",
            "api",
            "graphql",
            "-f",
            f"query={query}",
            "-F",
            f"owner={owner}",
            "-F",
            f"name={name}",
            "-F",
            f"number={pr}",
        ]
        if cursor:
            args.extend(["-F", f"cursor={cursor}"])
        else:
            args.extend(["-F", "cursor=null"])
        raw = run_command(args, root)
        if raw.startswith("[exit") or raw.startswith("[error]"):
            return None
        try:
            data = json.loads(raw)
            threads = (
                (((data.get("data") or {}).get("repository") or {}).get("pullRequest") or {})
                .get("reviewThreads")
                or {}
            )
            for node in threads.get("nodes") or []:
                if not isinstance(node, dict):
                    continue
                for c in ((node.get("comments") or {}).get("nodes") or []):
                    if str((c or {}).get("databaseId")) == target:
                        return str(node.get("id") or "") or None
            page = threads.get("pageInfo") or {}
            if not page.get("hasNextPage"):
                return None
            cursor = page.get("endCursor")
            if not cursor:
                return None
        except (json.JSONDecodeError, TypeError, AttributeError):
            return None
    return None


def resolve_reply_target(
    *,
    root: Path | None,
    repo: str | None,
    pr: int,
    comment_id: str,
    kind_hint: str | None,
    index: dict[str, CommentRecord],
    live: bool = True,
) -> ReplyTarget:
    """Classify ``comment_id`` and return the postable target (never guess)."""
    cid = comment_id.strip()
    hint = (kind_hint or "").strip().lower() or None
    if hint == "reviews":
        hint = "review"

    if hint == "review" or (cid in index and index[cid].kind == "review"):
        return ReplyTarget(
            input_id=cid,
            kind="review",
            post_method="skip_review",
            reply_to_id=None,
            body_snippet=(index[cid].body if cid in index else "")[:200],
            detail="Review submission bodies are not reply threads.",
            mcp_tool=None,
            mcp_hint=None,
        )

    # Cache hit
    if cid in index:
        rec = index[cid]
        if rec.kind == "inline":
            root_id = walk_to_root(cid, index)
            root_body = index[root_id].body if root_id in index else rec.body
            return ReplyTarget(
                input_id=cid,
                kind="inline",
                post_method="review_reply",
                reply_to_id=root_id,
                body_snippet=root_body[:240],
                detail=(
                    None
                    if root_id == cid
                    else f"Walked child reply {cid} → root review comment {root_id}"
                ),
                mcp_tool="add_reply_to_pull_request_comment",
                mcp_hint=(
                    f"MCP add_reply_to_pull_request_comment commentId={root_id} "
                    f"pullNumber={pr} (use ROOT id, never a child reply id)"
                ),
            )
        if rec.kind == "discussion":
            return ReplyTarget(
                input_id=cid,
                kind="discussion",
                post_method="discussion_quote",
                reply_to_id=cid,
                body_snippet=rec.body[:240],
                detail="Discussion IssueComment → quote-reply on PR conversation",
                mcp_tool="add_issue_comment",
                mcp_hint=(
                    f"MCP add_issue_comment issue_number={pr} with quote of parent "
                    f"comment {cid} (no nest API for IssueComments)"
                ),
            )

    # Live classify when cache misses
    if live and root is not None and repo:
        # Prefer hint order; otherwise try review comment then issue comment.
        order: list[str]
        if hint == "discussion":
            order = ["discussion", "inline"]
        elif hint == "inline":
            order = ["inline", "discussion"]
        else:
            order = ["inline", "discussion"]

        for try_kind in order:
            if try_kind == "inline" and cid.isdigit():
                rec = _live_lookup_review_comment(root, repo, cid)
                if rec:
                    # Enrich index for root walk if parent missing
                    index[rec.comment_id] = rec
                    parent = rec.in_reply_to_id
                    hops = 0
                    while parent and parent not in index and hops < 10:
                        parent_rec = _live_lookup_review_comment(root, repo, parent)
                        if not parent_rec:
                            break
                        index[parent_rec.comment_id] = parent_rec
                        parent = parent_rec.in_reply_to_id
                        hops += 1
                    root_id = walk_to_root(rec.comment_id, index)
                    return ReplyTarget(
                        input_id=cid,
                        kind="inline",
                        post_method="review_reply",
                        reply_to_id=root_id,
                        body_snippet=(index.get(root_id) or rec).body[:240],
                        detail=f"Live GET pulls/comments/{cid} → root {root_id}",
                        mcp_tool="add_reply_to_pull_request_comment",
                        mcp_hint=(
                            f"MCP add_reply_to_pull_request_comment commentId={root_id} "
                            f"pullNumber={pr}"
                        ),
                    )
            if try_kind == "discussion" and (cid.isdigit() or hint == "discussion"):
                # Numeric or unknown discussion: GET issues/comments/{id}
                if cid.isdigit():
                    rec = _live_lookup_issue_comment(root, repo, cid)
                    if rec:
                        return ReplyTarget(
                            input_id=cid,
                            kind="discussion",
                            post_method="discussion_quote",
                            reply_to_id=cid,
                            body_snippet=rec.body[:240],
                            detail=f"Live GET issues/comments/{cid}",
                            mcp_tool="add_issue_comment",
                            mcp_hint=(
                                f"MCP add_issue_comment issue_number={pr} with quote of {cid}"
                            ),
                        )

        if _GRAPHQL_NODE.match(cid) and not cid.isdigit():
            typename, db_id, err = _resolve_graphql_node(root, cid)
            if err or not db_id:
                return ReplyTarget(
                    input_id=cid,
                    kind="unknown",
                    post_method="unresolved",
                    reply_to_id=None,
                    body_snippet="",
                    detail=err or f"Cannot resolve GraphQL node {cid}",
                    mcp_tool="pull_request_read",
                    mcp_hint=(
                        "MCP pull_request_read method=get_review_comments then "
                        "add_reply_to_pull_request_comment with numeric databaseId"
                    ),
                )
            if typename == "PullRequestReviewComment":
                return resolve_reply_target(
                    root=root,
                    repo=repo,
                    pr=pr,
                    comment_id=db_id,
                    kind_hint="inline",
                    index=index,
                    live=True,
                )
            if typename == "IssueComment":
                return resolve_reply_target(
                    root=root,
                    repo=repo,
                    pr=pr,
                    comment_id=db_id,
                    kind_hint="discussion",
                    index=index,
                    live=True,
                )
            if typename == "PullRequestReview":
                return ReplyTarget(
                    input_id=cid,
                    kind="review",
                    post_method="skip_review",
                    reply_to_id=None,
                    body_snippet="",
                    detail="GraphQL PullRequestReview is not a reply thread",
                )

    # Offline / dry-run with hint only
    if hint == "discussion":
        return ReplyTarget(
            input_id=cid,
            kind="discussion",
            post_method="discussion_quote",
            reply_to_id=cid,
            body_snippet="",
            detail="Kind hint discussion (no live lookup)",
            mcp_tool="add_issue_comment",
            mcp_hint=f"MCP add_issue_comment issue_number={pr} with quote of {cid}",
        )
    if hint == "inline" or cid.isdigit():
        return ReplyTarget(
            input_id=cid,
            kind="inline",
            post_method="review_reply",
            reply_to_id=cid,
            body_snippet="",
            detail=(
                "Assumed inline from digit/hint — live lookup unavailable; "
                "if POST fails, walk in_reply_to_id to root or use MCP"
            ),
            mcp_tool="add_reply_to_pull_request_comment",
            mcp_hint=(
                f"MCP add_reply_to_pull_request_comment commentId={cid} pullNumber={pr}"
            ),
        )

    return ReplyTarget(
        input_id=cid,
        kind="unknown",
        post_method="unresolved",
        reply_to_id=None,
        body_snippet="",
        detail=(
            f"Cannot resolve {cid} to a threadable comment. "
            "Re-fetch comments, use numeric review-comment id, or MCP "
            "pull_request_read get_review_comments."
        ),
        mcp_tool="pull_request_read",
        mcp_hint="MCP pull_request_read method=get_review_comments + get_comments",
    )
