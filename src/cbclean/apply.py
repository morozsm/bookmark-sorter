from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List
from .utils import Bookmark, ensure_dir


def export_bookmarks_html(
    bookmarks: List[Bookmark], export_path: Path, *, group_by: str = "folder"
) -> None:
    ensure_dir(export_path.parent)
    with export_path.open("w", encoding="utf-8") as f:
        f.write("<!DOCTYPE NETSCAPE-Bookmark-file-1>\n")
        f.write('<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">\n')
        f.write("<TITLE>Bookmarks</TITLE>\n<H1>Bookmarks</H1>\n<DL><p>\n")
        if group_by == "tag-hier":
            tree: Dict[str, Any] = {}
            for b in bookmarks:
                for key in _group_keys(b, "tag-all"):
                    parts = [p for p in key.split("/") if p]
                    if not parts:
                        parts = ["Uncategorized"]
                    node = tree
                    for p in parts:
                        node = node.setdefault(p, {})
                    node.setdefault("__items__", []).append(b)
            _write_tree(f, tree)
        else:
            # Flat export grouped by folder_path or simple tag
            by_folder: Dict[str, List[Bookmark]] = {}
            for b in bookmarks:
                keys = list(_group_keys(b, group_by))
                for key in keys:
                    by_folder.setdefault(key, []).append(b)
            for folder, items in sorted(by_folder.items()):
                f.write(f"<DT><H3>{html_escape(folder)}</H3>\n<DL><p>\n")
                for b in items:
                    if not b.url:
                        continue
                    f.write(
                        f'<DT><A HREF="{html_escape(b.normalized_url or b.url)}">{html_escape(b.title)}</A>\n'
                    )
                f.write("</DL><p>\n")
        f.write("</DL><p>\n")


def html_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _group_keys(b: Bookmark, group_by: str) -> Iterable[str]:
    if group_by == "tag":
        yield (b.tags[0] if b.tags else "Uncategorized")
        return
    if group_by == "tag-all":
        tags = b.tags or []
        if tags:
            for t in tags:
                yield t
            return
        yield "Uncategorized"
        return
    # default: folder
    yield (b.folder_path or "Bookmarks")


def _write_tree(f, tree: Dict[str, Any]) -> None:
    for name in sorted(k for k in tree.keys() if k != "__items__"):
        node = tree[name]
        f.write(f"<DT><H3>{html_escape(name)}</H3>\n<DL><p>\n")
        _write_tree(f, node)
        for b in node.get("__items__", []):
            if not b.url:
                continue
            f.write(
                f'<DT><A HREF="{html_escape(b.normalized_url or b.url)}">{html_escape(b.title)}</A>\n'
            )
        f.write("</DL><p>\n")
