from __future__ import annotations

from typing import List
from .utils import Bookmark


def check_liveness(bookmarks: List[Bookmark], *, enabled: bool) -> None:
    # MVP: mark as 'unknown' if disabled; skip network operations.
    status = "unknown" if not enabled else "unchecked"
    for b in bookmarks:
        if b.url:
            b.liveness = status
