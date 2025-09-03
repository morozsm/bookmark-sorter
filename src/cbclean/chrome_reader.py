from __future__ import annotations

from pathlib import Path
from typing import List, Optional
import json
from bs4 import BeautifulSoup

from .utils import Bookmark


def read_chrome_json(path: Path, profile: Optional[str] = None) -> List[Bookmark]:
    data = json.loads(path.read_text(encoding="utf-8"))
    roots = data.get("roots", {})
    results: List[Bookmark] = []

    def walk(node: dict, folder_path: str = "Bookmarks Bar") -> None:
        if not isinstance(node, dict):
            return
        ntype = node.get("type")
        if ntype == "url":
            bid = node.get("id", "")
            title = node.get("name", "")
            url = node.get("url", None)
            results.append(Bookmark(id=bid, title=title, url=url, folder_path=folder_path, profile=profile))
        elif ntype == "folder":
            name = node.get("name", "")
            new_path = f"{folder_path}/{name}" if name else folder_path
            for child in node.get("children", []) or []:
                walk(child, new_path)

    for root in roots.values():
        walk(root, folder_path=root.get("name", ""))
    return results


def read_bookmarks_html(path: Path) -> List[Bookmark]:
    soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="ignore"), "html.parser")
    results: List[Bookmark] = []
    folder_stack: List[str] = ["Bookmarks"]

    def walk_dl(dl) -> None:
        # Traverse children in order to respect folder nesting (H3 followed by DL)
        for el in dl.children:
            name = getattr(el, "name", None)
            if name == "dt":
                h3 = el.find("h3", recursive=False)
                if h3 is not None:
                    folder_stack.append(h3.get_text(strip=True))
                    # Find the next sibling DL which contains this folder's entries
                    next_dl = None
                    for sib in el.next_siblings:
                        if getattr(sib, "name", None) == "dl":
                            next_dl = sib
                            break
                    if next_dl is not None:
                        walk_dl(next_dl)
                    folder_stack.pop()
                a = el.find("a", recursive=False)
                if a is not None and a.get("href"):
                    title = a.get_text(strip=True)
                    url = a.get("href")
                    folder_path = "/".join(folder_stack)
                    results.append(Bookmark(id=str(len(results)+1), title=title, url=url, folder_path=folder_path))
            elif name == "dl":
                walk_dl(el)

    top_dl = soup.find("dl")
    if top_dl is not None:
        walk_dl(top_dl)
    # Fallback: collect flat links if structured parse yielded nothing
    if not results:
        for a in soup.find_all("a"):
            href = a.get("href")
            if href:
                results.append(Bookmark(id=str(len(results)+1), title=a.get_text(strip=True), url=href, folder_path="Bookmarks"))
    return results
