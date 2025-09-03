from __future__ import annotations

# Placeholder for embeddings-based classification (optional, offline).
# Intentionally minimal to keep core app working without heavy deps.

from typing import List
from .utils import Bookmark


def classify_by_embeddings(bookmarks: List[Bookmark]) -> None:  # pragma: no cover
    # Not implemented in MVP. Leave tags as-is.
    return None
