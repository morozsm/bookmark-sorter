from __future__ import annotations

from typing import Dict, List, Tuple
from rapidfuzz import fuzz
from .utils import Bookmark


def _title_sim(a: str, b: str) -> float:
    # Combine several robust fuzzy measures
    scores = [
        fuzz.token_set_ratio(a, b),
        fuzz.partial_token_set_ratio(a, b),
        fuzz.partial_ratio(a, b),
        fuzz.token_sort_ratio(a, b),
    ]
    return max(scores) / 100.0


def deduplicate(
    bookmarks: List[Bookmark],
    *,
    title_threshold: float,
    prefer_shorter_url: bool,
) -> Tuple[List[Bookmark], List[Bookmark]]:
    by_norm: Dict[str, Bookmark] = {}
    duplicates: List[Bookmark] = []
    for b in bookmarks:
        key = b.normalized_url or b.url or ""
        if not key:
            continue
        existed = by_norm.get(key)
        if existed is None:
            by_norm[key] = b
        else:
            keep, drop = _resolve_dupe(existed, b, prefer_shorter_url)
            by_norm[key] = keep
            duplicates.append(drop)

    # Soft duplicates by similar title in same folder
    remaining = list(by_norm.values())
    remaining.sort(key=lambda x: (x.folder_path, x.title))
    i = 0
    while i < len(remaining) - 1:
        a = remaining[i]
        j = i + 1
        while j < len(remaining) and remaining[j].folder_path == a.folder_path:
            b = remaining[j]
            if a.url and b.url and _title_sim(a.title, b.title) >= title_threshold:
                keep, drop = _resolve_dupe(a, b, prefer_shorter_url)
                remaining[i] = keep
                duplicates.append(drop)
                remaining.pop(j)
                continue
            j += 1
        i += 1

    return remaining, duplicates


def _resolve_dupe(a: Bookmark, b: Bookmark, prefer_shorter_url: bool) -> Tuple[Bookmark, Bookmark]:
    au = (a.normalized_url or a.url or "")
    bu = (b.normalized_url or b.url or "")
    if prefer_shorter_url and au and bu:
        return (a, b) if len(au) <= len(bu) else (b, a)
    # fallback: keep first
    return a, b
