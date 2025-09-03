from __future__ import annotations

from pathlib import Path
from typing import Dict, List
from .utils import Bookmark, domain_of

try:
    from ruamel.yaml import YAML  # type: ignore
except Exception:  # pragma: no cover - optional at runtime
    YAML = None  # type: ignore


def load_rules(path: Path) -> Dict[str, Dict[str, List[str]]]:
    if not path.exists() or YAML is None:
        return {"domains": {}, "keywords": {}, "lang": {}}
    yaml = YAML(typ="safe")
    data = yaml.load(path.read_text(encoding="utf-8")) or {}
    domains = data.get("domains", {}) or {}
    keywords = data.get("keywords", {}) or {}
    lang = data.get("lang", {}) or {}
    return {"domains": domains, "keywords": keywords, "lang": lang}


def classify_by_rules(bookmarks: List[Bookmark], rules: Dict[str, Dict[str, List[str]]]) -> None:
    domains = rules.get("domains", {})
    keywords = rules.get("keywords", {})
    for b in bookmarks:
        tags: List[str] = []
        if b.url:
            d = domain_of(b.url)
            if d and d in domains:
                tags.extend(domains[d])
            title_l = b.title.lower()
            url_l = b.url.lower()
            for pat, tgs in keywords.items():
                try:
                    import re

                    if re.search(pat, title_l) or re.search(pat, url_l):
                        tags.extend(tgs)
                except re.error:
                    if pat in title_l or pat in url_l:
                        tags.extend(tgs)
        # de-duplicate tags
        b.tags = sorted(set(tags))

