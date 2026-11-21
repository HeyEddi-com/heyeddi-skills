"""Firestore read detector: usage-based cost that never shows up in Terraform.

Looks for listeners and queries with no limit(), reads inside loops (N+1), polled
queries, and write triggers that write back. Each finding carries `reads_per_day`,
which the budget gate compares to `firestore_reads_per_day_limit`.
"""
from __future__ import annotations

import re

from _cost_common import CODE_EXT, _finding, _skip, poll_intervals_ms

LISTEN = re.compile(r"\b(onSnapshot|addSnapshotListener|useCollection|useDocument)\s*\(|\.snapshots\s*\(")
QUERY = re.compile(r"\b(getDocs|collectionGroup)\s*\(|\.stream\s*\(\)|\.get\s*\(\)")
SINGLE = re.compile(r"\bgetDoc\s*\(|\.doc\([^)]*\)\.get\s*\(")
LOOP = re.compile(r"\bfor\s*[\(a-zA-Z]|\.map\s*\(|\.forEach\s*\(|\bwhile\s*\(|Promise\.all\s*\(")
LIMIT = re.compile(r"\blimit(?:ToLast)?\s*\(\s*(\d+)?|\.limit\s*\(\s*(\d+)?|\blimit\s*:\s*(\d+)")
FIRESTORE_HINT = re.compile(
    r"firestore|collection\s*\(|getFirestore|FirebaseFirestore|cloud_firestore|\bgetDocs?\s*\(|\bonSnapshot\s*\(", re.I
)
TRIGGER = re.compile(r"onDocument(Written|Created|Updated)|functions\.firestore|\bonWrite\b|on_document_(written|created|updated)")
WRITE = re.compile(r"\.(set|update|add)\s*\(|\b(setDoc|updateDoc|addDoc)\s*\(|batch\.commit")
WINDOW = 6
LOOKBACK = 3

CHEAPER = (
    "add limit() and paginate; listen to one small summary doc, not the collection; "
    "unsubscribe when the view closes; fetch many docs in one query (where in) instead of a loop; "
    "cache or aggregate server-side (count())"
)


def _bound(window: str, assumptions: dict) -> tuple[int | None, bool]:
    m = LIMIT.search(window)
    if not m:
        return None, False
    n = next((g for g in m.groups() if g), None)
    return (int(n) if n else 50), True


def _scan(lines: list[str], assumptions: dict) -> list[tuple[str, int, int, str]]:
    """Return (kind, line_no, reads_per_day, text) for each read site."""
    a = assumptions
    sessions, clients = a["firestore_sessions_per_day"], a["concurrent_clients"]
    docs_default = a["firestore_docs_per_query"]
    text = "\n".join(lines)
    polled_ms = next((ms for ms in poll_intervals_ms(text) if 0 < ms < 60000), None)
    sites: list[tuple[str, int, int, str]] = []
    for i, line in enumerate(lines):
        window = "\n".join(lines[max(0, i - LOOKBACK):i + WINDOW])
        single_doc = bool(SINGLE.search(line) and not QUERY.search(line)) or (
            bool(re.search(r"\bdoc\s*\(", window))
            and not re.search(r"\b(collection|query|collectionGroup)\s*\(", window)
        )
        n, bounded = _bound(window, a)
        docs = 1 if single_doc else (n if bounded else docs_default)
        in_loop = any(LOOP.search(x) for x in lines[max(0, i - 3):i + 1])
        if LISTEN.search(line):
            reads = sessions * docs + clients * a["firestore_doc_changes_per_day"]
            kind = "listener" + ("" if bounded or single_doc else " with no limit")
        elif SINGLE.search(line) or QUERY.search(line):
            if QUERY.search(line) and not FIRESTORE_HINT.search(window):
                continue
            per_run = docs if QUERY.search(line) else 1
            runs = sessions
            kind = "query" + ("" if bounded or single_doc else " with no limit")
            if polled_ms:
                runs = clients * 86_400_000 // polled_ms
                kind += f" polled every {polled_ms} ms"
            if in_loop:
                runs *= a["firestore_loop_iterations"]
                kind += " inside a loop"
            reads = runs * per_run
        else:
            continue
        sites.append((kind, i + 1, int(reads), line.strip()[:70]))
    return sites


def firestore_usage(path: str, added: list[str], removed: list[str], rates: dict, a: dict) -> list[dict]:
    if _skip(path) or not path.endswith(CODE_EXT):
        return []
    fs = rates.get("firestore", {})
    price = fs.get("read_per_100k", {"low": 0.03, "high": 0.06})
    out: list[dict] = []
    for lines, sign, verb in ((added, 1, "adds"), (removed, -1, "removes")):
        if not FIRESTORE_HINT.search("\n".join(lines)) and not any(LISTEN.search(x) for x in lines):
            continue
        for kind, _n, reads, snippet in _scan(lines, a):
            monthly = reads * 30 / 100_000
            f = _finding(
                "firestore", path,
                f"{verb} {kind}: about {reads:,} reads/day (`{snippet}`)",
                low=sign * monthly * price["low"], high=sign * monthly * price["high"],
                confidence="low", cheaper=CHEAPER if sign > 0 else "",
                severity="warn" if sign > 0 and reads >= a["firestore_reads_per_day_warn"] else "info",
            )
            f["reads_per_day"] = sign * reads
            out.append(f)
    joined_added = "\n".join(added)
    if sum(1 for _ in TRIGGER.finditer(joined_added)) and WRITE.search(joined_added):
        f = _finding(
            "firestore", path,
            "adds a Firestore trigger that also writes to Firestore: a write can retrigger it and loop. "
            "Guard on changed fields and never write the document that fired it",
            confidence="low", cheaper="compare before/after and return early; write to a different collection",
        )
        f["reads_per_day"] = 0
        out.append(f)
    return out
