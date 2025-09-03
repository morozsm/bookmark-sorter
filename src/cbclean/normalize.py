from __future__ import annotations

from typing import Iterable, List
from .utils import Bookmark, normalize_url


def normalize_bookmarks(bookmarks: List[Bookmark], *, strip_params: List[str], strip_fragments: bool, strip_www: bool) -> None:
    for b in bookmarks:
        if not b.url:
            continue
        b.normalized_url = normalize_url(b.url, strip_params=strip_params, strip_fragments=strip_fragments, strip_www_flag=strip_www)

