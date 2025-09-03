from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional
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
    # Netscape format stores links in <A> tags often inside <DT> tags; use folder stacks via <H3>
    folder_stack: List[str] = ["Bookmarks"]

    def walk_ul(ul) -> None:
        for el in ul.children:
            if getattr(el, "name", None) == "dt":
                h3 = el.find("h3")
                if h3:
                    folder_stack.append(h3.get_text(strip=True))
                    next_dl = el.find_next_sibling("dl")
                    if next_dl:
                        inner_ul = next_dl
                        walk_ul(inner_ul)
                    folder_stack.pop()
                a = el.find("a")
                if a and a.get("href"):
                    title = a.get_text(strip=True)
                    url = a.get("href")
                    folder_path = "/".join(folder_stack)
                    results.append(Bookmark(id=str(len(results)+1), title=title, url=url, folder_path=folder_path))

    top_dl = soup.find("dl")
    if top_dl:
        walk_ul(top_dl)
    return results

