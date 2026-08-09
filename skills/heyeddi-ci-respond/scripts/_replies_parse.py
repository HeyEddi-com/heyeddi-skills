"""Parse tracking tables and structured reply drafts for PR respond."""
from __future__ import annotations

import re
from dataclasses import dataclass


COMMENT_HEADING_RE = re.compile(
    r"^##\s+Comment\s+(\S+)(?:\s+\(([^)]+)\))?\s*$",
    re.IGNORECASE | re.MULTILINE,
)
SUMMARY_HEADING_RE = re.compile(r"^##\s+Summary\s*$", re.IGNORECASE | re.MULTILINE)
TABLE_ROW_RE = re.compile(r"^\|(.+)\|$")


@dataclass(frozen=True)
class ReplySection:
    comment_id: str
    kind: str | None
    body: str
    start: int
    end: int


@dataclass(frozen=True)
class TrackingRow:
    comment_id: str
    kind: str | None
    author: str | None
    status: str | None
    raw: str


def parse_tracking_rows(text: str) -> list[TrackingRow]:
    """Extract data rows from a markdown tracking table."""
    rows: list[TrackingRow] = []
    header_cols: list[str] | None = None
    for line in text.splitlines():
        match = TABLE_ROW_RE.match(line.strip())
        if not match:
            continue
        cells = [c.strip() for c in match.group(1).split("|")]
        if all(set(c) <= {"-", ":", " "} for c in cells):
            continue
        if header_cols is None:
            header_cols = [c.lower() for c in cells]
            continue
        if "comment id" not in header_cols:
            continue
        idx = {name: i for i, name in enumerate(header_cols)}

        def cell(name: str) -> str | None:
            i = idx.get(name)
            if i is None or i >= len(cells):
                return None
            value = cells[i].strip()
            return value or None

        comment_id = cell("comment id")
        if not comment_id or comment_id.lower() == "comment id":
            continue
        rows.append(
            TrackingRow(
                comment_id=comment_id,
                kind=cell("type"),
                author=cell("author"),
                status=cell("status"),
                raw=line,
            )
        )
    return rows


def parse_reply_sections(text: str) -> tuple[list[ReplySection], str | None]:
    """Return (comment sections, summary body). Summary must exist for a valid draft."""
    headings = list(COMMENT_HEADING_RE.finditer(text))
    summary_match = SUMMARY_HEADING_RE.search(text)
    sections: list[ReplySection] = []

    bounds: list[tuple[re.Match[str], str | None]] = [
        (m, "comment") for m in headings
    ]
    if summary_match:
        bounds.append((summary_match, "summary"))
    bounds.sort(key=lambda item: item[0].start())

    summary_body: str | None = None
    for i, (match, kind) in enumerate(bounds):
        end = bounds[i + 1][0].start() if i + 1 < len(bounds) else len(text)
        body = text[match.end() : end].strip()
        if kind == "summary":
            summary_body = body
            continue
        comment_id = match.group(1)
        section_kind = (match.group(2) or "").strip().lower() or None
        sections.append(
            ReplySection(
                comment_id=comment_id,
                kind=section_kind,
                body=body,
                start=match.start(),
                end=end,
            )
        )

    if summary_match and headings and summary_match.start() < headings[-1].start():
        # Summary appears before a comment heading: invalid order.
        summary_body = None if summary_body == "" else summary_body
        # Caller checks order separately via summary_is_last().
        pass

    return sections, summary_body


def summary_is_last(text: str) -> bool:
    headings = list(COMMENT_HEADING_RE.finditer(text))
    summary_match = SUMMARY_HEADING_RE.search(text)
    if not summary_match:
        return False
    if not headings:
        return True
    return summary_match.start() > headings[-1].start()


def infer_reply_kind(comment_id: str, tracking_kind: str | None, section_kind: str | None) -> str:
    """Classify how to post: inline | discussion | review."""
    for candidate in (section_kind, tracking_kind):
        if not candidate:
            continue
        normalized = candidate.strip().lower()
        if normalized in {"inline", "discussion", "review", "reviews"}:
            return "review" if normalized == "reviews" else normalized
    if comment_id.upper().startswith("DC_"):
        return "discussion"
    if comment_id.isdigit():
        # Numeric IDs are usually inline; reviews are also numeric but tracking
        # type should disambiguate. Default inline for /replies endpoint.
        return "inline"
    return "discussion"
