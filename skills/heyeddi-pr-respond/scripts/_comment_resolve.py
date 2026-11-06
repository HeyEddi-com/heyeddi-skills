"""Resolve any PR comment id to a postable reply target.

Only unresolved pull-request review threads are postable, and only at the
root review-comment id, with no quote. Issue comments (Conversation tab)
are not threads: tests-hold notes, review summaries, and comments written
by the account that is responding are skipped. There is no
``/issues/comments/{id}/replies`` endpoint and this module does not
quote-reply them.
"""
from __future__ import annotations

import importlib.util
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from _skill_cli import run_command


def _load_sibling(module_name: str):
    """Load a script next to this file.

    ``_untrusted_doc`` also exists under heyeddi-pr-review. A full pytest run
    imports that copy first and caches it as ``_untrusted_doc``, which does
    not export ``unwrap_untrusted_text``.
    """
    path = Path(__file__).resolve().parent / f"{module_name}.py"
    spec = importlib.util.spec_from_file_location(
        f"heyeddi_pr_respond.{module_name}",
        path,
    )
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_untrusted_doc = _load_sibling("_untrusted_doc")
is_already_wrapped = _untrusted_doc.is_already_wrapped
unwrap_untrusted_text = _untrusted_doc.unwrap_untrusted_text

Kind = Literal["inline", "discussion", "review", "unknown"]
PostMethod = Literal[
    "review_reply",
    "skip_issue_comment",
    "skip_review",
    "skip_own",
    "skip_answered",
    "unresolved",
]

TESTS_HOLD_RE = re.compile(r"<!--\s*heyeddi:tests-hold\b", re.IGNORECASE)

_GRAPHQL_NODE = re.compile(r"^[A-Za-z0-9_=-]{10,}$")


@dataclass(frozen=True)
class CommentRecord:
    comment_id: str
    kind: Kind
    body: str
    in_reply_to_id: str | None = None
    node_id: str | None = None
    author: str | None = None
    created_at: str | None = None


@dataclass(frozen=True)
class ReplyTarget:
    """How to post a reply for a drafted ``## Comment <id>`` section."""

    input_id: str
    kind: Kind
    post_method: PostMethod
    reply_to_id: str | None
    """Top-level review-comment database id. None when the id is not a review thread."""
    body_snippet: str
    detail: str | None = None
    mcp_tool: str | None = None
    """Cursor GitHub MCP tool to use if gh posting fails."""
    mcp_hint: str | None = None


def _unwrap_body(raw: Any) -> str:
    if isinstance(raw, dict) and "wrapped" in raw:
        return unwrap_untrusted_text(str(raw.get("wrapped") or ""))
    return unwrap_untrusted_text(str(raw or ""))


def comment_plain_body(item: dict[str, Any]) -> str:
    """Plain comment text for classification. Never the untrusted banner."""
    raw = item.get("body_raw")
    if isinstance(raw, str) and raw and not is_already_wrapped(raw):
        return raw
    return _unwrap_body(item.get("body"))


def is_tests_hold(body: str | None) -> bool:
    return bool(TESTS_HOLD_RE.search(body or ""))


def comment_author(item: dict[str, Any]) -> str:
    user = item.get("user") or item.get("author") or {}
    if isinstance(user, dict):
        return str(user.get("login") or "")
    return str(user or "")


def _comment_when(item: dict[str, Any]) -> str:
    for key in ("created_at", "createdAt", "submitted_at", "submittedAt", "updated_at"):
        value = item.get(key)
        if value:
            return str(value)
    return ""


def _same_login(left: str | None, right: str | None) -> bool:
    if not left or not right:
        return False
    return left.strip().lower() == right.strip().lower()


def awaiting_root_ids(
    inline_comments: list[dict[str, Any]],
    responder_login: str | None,
) -> list[str]:
    """Root review-comment ids that still need a reply.

    A thread is awaiting when it is not a tests-hold note and the latest
    comment was not written by ``responder_login``. When the login is unknown,
    every non-hold root is awaiting. Issue comments are never included.
    """
    nodes = [c for c in inline_comments if isinstance(c, dict) and c.get("id") is not None]
    by_id = {str(c["id"]): c for c in nodes}
    parent_of: dict[str, str | None] = {}
    for comment in nodes:
        parent = comment.get("in_reply_to_id")
        parent_of[str(comment["id"])] = str(parent) if parent is not None else None

    def root_of(comment_id: str) -> str:
        seen: set[str] = set()
        current = comment_id
        while current in parent_of and current not in seen:
            seen.add(current)
            parent = parent_of[current]
            if not parent:
                return current
            current = parent
        return current

    groups: dict[str, list[dict[str, Any]]] = {}
    for comment in nodes:
        groups.setdefault(root_of(str(comment["id"])), []).append(comment)

    responder = (responder_login or "").strip().lower()
    awaiting: list[str] = []
    for comment in nodes:
        if parent_of.get(str(comment["id"])):
            continue
        root_id = str(comment["id"])
        if root_id not in by_id:
            continue
        if is_tests_hold(comment_plain_body(by_id[root_id])):
            continue
        thread = groups.get(root_id) or [by_id[root_id]]
        latest = max(thread, key=lambda item: (_comment_when(item), str(item.get("id"))))
        if responder and comment_author(latest).strip().lower() == responder:
            continue
        awaiting.append(root_id)
    return awaiting


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
            body=comment_plain_body(item),
            in_reply_to_id=parent,
            node_id=_as_id(item.get("node_id")),
            author=comment_author(item) or None,
            created_at=_comment_when(item) or None,
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
            body=comment_plain_body(item),
            in_reply_to_id=None,
            node_id=_as_id(item.get("node_id")),
            author=comment_author(item) or None,
            created_at=_comment_when(item) or None,
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
            body=comment_plain_body(item),
            author=comment_author(item) or None,
            created_at=_comment_when(item) or None,
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
        body=comment_plain_body(data),
        in_reply_to_id=_as_id(data.get("in_reply_to_id")),
        node_id=_as_id(data.get("node_id")),
        author=comment_author(data) or None,
        created_at=_comment_when(data) or None,
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
        body=comment_plain_body(data),
        node_id=_as_id(data.get("node_id")),
        author=comment_author(data) or None,
        created_at=_comment_when(data) or None,
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


def _latest_inline(root_id: str, index: dict[str, CommentRecord]) -> CommentRecord | None:
    members = [
        rec
        for rec in index.values()
        if rec.kind == "inline" and walk_to_root(rec.comment_id, index) == root_id
    ]
    if not members:
        return None
    members.sort(key=lambda rec: (rec.created_at or "", rec.comment_id))
    return members[-1]


def _skip_issue_target(comment_id: str, body: str, *, detail: str) -> ReplyTarget:
    note = "Issue comments are not review threads. Do not quote-reply."
    if is_tests_hold(body):
        note += " Tests-hold notes are status posts."
    return ReplyTarget(
        input_id=comment_id,
        kind="discussion",
        post_method="skip_issue_comment",
        reply_to_id=None,
        body_snippet=body[:240],
        detail=f"{note} {detail}".strip(),
        mcp_tool=None,
        mcp_hint=None,
    )


def _review_thread_target(
    *,
    comment_id: str,
    pr: int,
    index: dict[str, CommentRecord],
    rec: CommentRecord,
    responder_login: str | None,
    detail: str | None,
) -> ReplyTarget:
    """Reply on an unresolved review thread at its root id, with no quote."""
    root_id = walk_to_root(rec.comment_id, index)
    root_rec = index.get(root_id) or rec
    if is_tests_hold(rec.body) or is_tests_hold(root_rec.body):
        return _skip_issue_target(comment_id, root_rec.body or rec.body, detail=detail or "tests-hold")
    if _same_login(rec.author, responder_login):
        return ReplyTarget(
            input_id=comment_id,
            kind="inline",
            post_method="skip_own",
            reply_to_id=None,
            body_snippet=root_rec.body[:240],
            detail="Comment was written by the account that is responding.",
            mcp_tool=None,
            mcp_hint=None,
        )
    latest = _latest_inline(root_id, index)
    if latest and _same_login(latest.author, responder_login):
        return ReplyTarget(
            input_id=comment_id,
            kind="inline",
            post_method="skip_answered",
            reply_to_id=root_id,
            body_snippet=root_rec.body[:240],
            detail=(
                f"Review thread {root_id} already ends with a reply from "
                f"{responder_login}. No further reply."
            ),
            mcp_tool=None,
            mcp_hint=None,
        )
    walked = None if root_id == comment_id else f"Walked child reply {comment_id} → root review comment {root_id}"
    return ReplyTarget(
        input_id=comment_id,
        kind="inline",
        post_method="review_reply",
        reply_to_id=root_id,
        body_snippet=root_rec.body[:240],
        detail=detail or walked,
        mcp_tool="add_reply_to_pull_request_comment",
        mcp_hint=(
            f"MCP add_reply_to_pull_request_comment commentId={root_id} "
            f"pullNumber={pr} (ROOT id, no quote)"
        ),
    )


def resolve_reply_target(
    *,
    root: Path | None,
    repo: str | None,
    pr: int,
    comment_id: str,
    kind_hint: str | None,
    index: dict[str, CommentRecord],
    live: bool = True,
    responder_login: str | None = None,
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
            return _review_thread_target(
                comment_id=cid,
                pr=pr,
                index=index,
                rec=rec,
                responder_login=responder_login,
                detail=None,
            )
        if rec.kind == "discussion":
            own = _same_login(rec.author, responder_login)
            extra = "Written by the responding account." if own else "Cached issue comment."
            return _skip_issue_target(cid, rec.body, detail=extra)

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
                    return _review_thread_target(
                        comment_id=cid,
                        pr=pr,
                        index=index,
                        rec=rec,
                        responder_login=responder_login,
                        detail=f"Live GET pulls/comments/{cid} → root {walk_to_root(rec.comment_id, index)}",
                    )
            if try_kind == "discussion" and (cid.isdigit() or hint == "discussion"):
                # Numeric or unknown discussion: GET issues/comments/{id}
                if cid.isdigit():
                    rec = _live_lookup_issue_comment(root, repo, cid)
                    if rec:
                        return _skip_issue_target(
                            cid,
                            rec.body,
                            detail=f"Live GET issues/comments/{cid}",
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
                    responder_login=responder_login,
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
                    responder_login=responder_login,
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
        return _skip_issue_target(cid, "", detail="Kind hint discussion (no live lookup)")
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
