from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlsplit, urlunsplit
import re
import time


def now_ts() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def strip_www(host: str) -> str:
    return host[4:] if host.lower().startswith("www.") else host


def filter_query(query: str, patterns: List[str]) -> str:
    if not query:
        return ""
    # Query is the part after '?', may include '&' items.
    items = [p for p in query.split("&") if p]
    kept: List[str] = []
    for item in items:
        key = item.split("=", 1)[0]
        if any(fnmatch_like(key, pat) for pat in patterns):
            continue
        kept.append(item)
    return "&".join(kept)


def fnmatch_like(text: str, pattern: str) -> bool:
    # Very small subset: support trailing '*' wildcard
    if pattern.endswith("*"):
        return text.startswith(pattern[:-1])
    return text == pattern


@dataclass
class Bookmark:
    id: str
    title: str
    url: Optional[str] = None
    parent_id: Optional[str] = None
    folder_path: str = ""
    profile: Optional[str] = None
    normalized_url: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    liveness: Optional[str] = None


def normalize_url(
    url: str,
    *,
    strip_params: List[str],
    strip_fragments: bool,
    strip_www_flag: bool,
) -> str:
    try:
        parts = urlsplit(url)
    except Exception:
        return url
    scheme = parts.scheme.lower()
    netloc = parts.netloc
    if strip_www_flag:
        netloc = strip_www(netloc)
    path = re.sub(r"//+", "/", parts.path) or "/"
    query = filter_query(parts.query, strip_params)
    fragment = "" if strip_fragments else parts.fragment
    return urlunsplit((scheme, netloc, path, query, fragment))


def domain_of(url: str) -> Optional[str]:
    try:
        netloc = urlsplit(url).netloc.lower()
        return netloc or None
    except Exception:
        return None
