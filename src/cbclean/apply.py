from __future__ import annotations

from pathlib import Path
from typing import Dict, List
from .utils import Bookmark, ensure_dir


def export_bookmarks_html(bookmarks: List[Bookmark], export_path: Path) -> None:
    ensure_dir(export_path.parent)
    with export_path.open("w", encoding="utf-8") as f:
        f.write("<!DOCTYPE NETSCAPE-Bookmark-file-1>\n")
        f.write('<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">\n')
        f.write("<TITLE>Bookmarks</TITLE>\n<H1>Bookmarks</H1>\n<DL><p>\n")
        # Flat export grouped by folder_path
        by_folder: Dict[str, List[Bookmark]] = {}
        for b in bookmarks:
            by_folder.setdefault(b.folder_path or "Bookmarks", []).append(b)
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
