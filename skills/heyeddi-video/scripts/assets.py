#!/usr/bin/env python3
"""A local inventory of reusable assets, each with its licence.

    video.py asset list [words]
    video.py asset get <id> --into <project>/assets
    video.py asset add <https url or file> --id x --licence CC0 --source <page> --into <project>/assets
"""
from __future__ import annotations

import argparse
import contextlib
import fcntl
import hashlib
import json
import os
import shutil
import sys
import tempfile
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

# Licences that allow commercial videos. The second kind asks for a credit.
FREE = {"CC0"}
CREDITED = {"CC-BY-4.0"}
LIMIT = 500 * 1024 * 1024
CATALOG = Path(__file__).resolve().parents[1] / "reference" / "assets.json"


class AssetError(ValueError):
    pass


def inventory_home() -> Path:
    # Point this at a shared folder to give several machines one inventory.
    default = Path.home() / ".cache" / "heyeddi-video" / "assets"
    return Path(os.environ.get("HEYEDDI_VIDEO_ASSETS", default))


def catalog() -> dict:
    return json.loads(CATALOG.read_text(encoding="utf-8"))


def check_licence(licence: str, author: str) -> None:
    if licence not in FREE | CREDITED:
        raise AssetError(f"licence {licence!r} is not one of {sorted(FREE | CREDITED)}")
    if licence in CREDITED and not author:
        raise AssetError(f"{licence} needs the author to credit")


def download(url: str, target: Path) -> None:
    if urllib.parse.urlparse(url).scheme != "https":
        raise AssetError(f"only https downloads: {url}")
    request = urllib.request.Request(url, headers={"User-Agent": "asset-fetch"})
    with urllib.request.urlopen(request, timeout=60) as response, target.open("wb") as out:
        size = 0
        while chunk := response.read(1 << 20):
            size += len(chunk)
            if size > LIMIT:
                raise AssetError(f"download is over {LIMIT} bytes: {url}")
            out.write(chunk)


def unpack(archive: Path, folder: Path) -> list[str]:
    """Extract a downloaded zip, refusing anything that would land outside the folder."""
    folder.mkdir(parents=True, exist_ok=True)
    root = folder.resolve()
    with zipfile.ZipFile(archive) as bundle:
        members = [info for info in bundle.infolist() if not info.is_dir()]
        for info in members:
            if not (root / info.filename).resolve().is_relative_to(root):
                raise AssetError(f"zip entry points outside its folder: {info.filename}")
        if sum(info.file_size for info in members) > LIMIT:
            raise AssetError(f"zip unpacks to over {LIMIT} bytes")
        bundle.extractall(root, members)
    return sorted(info.filename for info in members)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


@contextlib.contextmanager
def locked(home: Path):
    """One writer at a time: several agents share the inventory and may share a project."""
    home.mkdir(parents=True, exist_ok=True)
    with (home / "inventory.lock").open("a") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        yield


def record(home: Path, name: str, entry: dict) -> None:
    index = read_json(home / "inventory.json")
    index[name] = entry
    (home / "inventory.json").write_text(json.dumps(index, indent=1) + "\n")


def deliver(home: Path, name: str, into: Path) -> Path:
    """Verify the inventory copy, put it in the project, and note the credit there."""
    entry = read_json(home / "inventory.json")[name]
    for relative, expected in entry["files"].items():
        source = home / name / relative
        if not source.is_file() or digest(source) != expected:
            raise AssetError(f"{source} changed or is missing since it was recorded; delete {home / name} and get it again")
        (into / name / relative).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, into / name / relative)
    credits = read_json(into / "CREDITS.json")
    credits[name] = {key: entry[key] for key in ("licence", "source", "author")}
    (into / "CREDITS.json").write_text(json.dumps(credits, indent=1) + "\n")
    return into / name


def entry_for(folder: Path, files: list[str], licence: str, source: str, author: str) -> dict:
    return {"licence": licence, "source": source, "author": author,
            "files": {name: digest(folder / name) for name in files}}


def get(item: dict, home: Path, into: Path, fetch=download) -> Path:
    """A catalog item: files pinned to one commit, downloaded once."""
    check_licence(item["licence"], item.get("author", ""))
    name = item["id"]
    folder = home / name
    with locked(home):
        if name not in read_json(home / "inventory.json") or not folder.is_dir():
            folder.mkdir(parents=True, exist_ok=True)
            base = f"https://raw.githubusercontent.com/{item['repo']}/{item['commit']}/"
            for path in item["files"]:
                fetch(base + urllib.parse.quote(path), folder / Path(path).name)
            names = [Path(path).name for path in item["files"]]
            record(home, name, entry_for(folder, names, item["licence"], item["source"], item.get("author", "")))
        return deliver(home, name, into)


def add(location: str, name: str, licence: str, source: str, author: str, home: Path, into: Path) -> Path:
    """Anything else: a file or zip, from an https address or already on disk."""
    check_licence(licence, author)
    if Path(name).name != name or name in ("", ".", ".."):
        raise AssetError(f"--id is a plain folder name: {name!r}")
    with locked(home):
        folder = home / name
        if folder.exists():
            raise AssetError(f"{name} is already in the inventory: `get` it, or pick another id")
        with tempfile.TemporaryDirectory(dir=home) as work:
            local = Path(location)
            if not local.is_file():
                local = Path(work) / (Path(urllib.parse.urlparse(location).path).name or name)
                download(location, local)
            staged = Path(work) / "files"
            if zipfile.is_zipfile(local) and local.suffix.lower() == ".zip":
                files = unpack(local, staged)
            else:
                staged.mkdir()
                shutil.copy2(local, staged / local.name)
                files = [local.name]
            staged.rename(folder)
        record(home, name, entry_for(folder, files, licence, source, author))
        return deliver(home, name, into)


def listing(words: str, home: Path) -> list[dict]:
    rows = [{"id": item["id"], "kind": item["kind"], "licence": item["licence"], "about": item["about"]}
            for item in catalog()["items"]]
    known = {row["id"] for row in rows}
    rows += [{"id": name, "kind": "added", "licence": entry["licence"], "about": entry["source"]}
             for name, entry in read_json(home / "inventory.json").items() if name not in known]
    return [row for row in rows if all(word.lower() in json.dumps(row).lower() for word in words.split())]


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="video.py asset")
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("list").add_argument("words", nargs="*")
    one = sub.add_parser("get")
    one.add_argument("id")
    one.add_argument("--into", type=Path, required=True)
    new = sub.add_parser("add")
    new.add_argument("location")
    new.add_argument("--id", required=True)
    new.add_argument("--licence", required=True)
    new.add_argument("--source", required=True, help="the page that states the licence")
    new.add_argument("--author", default="")
    new.add_argument("--into", type=Path, required=True)
    args = parser.parse_args(argv)
    home = inventory_home()
    try:
        if args.action == "list":
            print(json.dumps({"inventory": str(home), "items": listing(" ".join(args.words), home),
                              "sources": catalog()["sources"]}, indent=1))
            return 0
        if args.action == "add":
            placed = add(args.location, args.id, args.licence, args.source, args.author, home, args.into.resolve())
        else:
            items = {item["id"]: item for item in catalog()["items"]}
            if args.id in items:
                placed = get(items[args.id], home, args.into.resolve())
            elif args.id in read_json(home / "inventory.json"):
                with locked(home):
                    placed = deliver(home, args.id, args.into.resolve())
            else:
                raise AssetError(f"{args.id} is neither in the catalog nor the inventory")
    except (AssetError, OSError, zipfile.BadZipFile) as error:
        print(error, file=sys.stderr)
        return 2
    print(placed)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
