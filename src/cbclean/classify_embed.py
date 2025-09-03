from __future__ import annotations

from typing import Iterable, List, Set
from pathlib import Path
from .utils import Bookmark
from .classify_rules import load_rules


def classify_by_embeddings(bookmarks: List[Bookmark], *, model_name: str = "all-MiniLM-L6-v2", labels: Iterable[str] | None = None, top_k: int = 2, score_threshold: float = 0.35) -> None:  # pragma: no cover
    """Assign tags via semantic similarity to label candidates using sentence-transformers.

    If sentence-transformers isn't available, this function leaves tags unchanged.
    """
    try:
        from sentence_transformers import SentenceTransformer, util  # type: ignore
        import numpy as np  # type: ignore
    except Exception:
        return None

    # Label candidates: passed-in labels or unique tags derived from rules file if available
    label_list: List[str] = sorted(set(labels or _default_labels_from_rules()))
    if not label_list:
        return None

    # Build texts to encode
    texts = [make_text(b) for b in bookmarks]
    model = SentenceTransformer(model_name)
    emb_labels = model.encode(label_list, normalize_embeddings=True, convert_to_tensor=True)
    emb_texts = model.encode(texts, normalize_embeddings=True, convert_to_tensor=True)

    # Cosine similarity and selection
    sims = util.cos_sim(emb_texts, emb_labels)  # shape: [N, L]
    for i, b in enumerate(bookmarks):
        # select top_k labels above threshold
        row = sims[i]
        # Convert to plain list of (score, idx)
        pairs = [(float(row[j]), j) for j in range(len(label_list))]
        pairs.sort(reverse=True)
        chosen: List[str] = []
        for score, j in pairs[: top_k * 3]:  # small buffer then filter by threshold
            if score >= score_threshold:
                chosen.append(label_list[j])
            if len(chosen) >= top_k:
                break
        if chosen:
            b.tags = sorted(set((b.tags or []) + chosen))


def make_text(b: Bookmark) -> str:
    parts = [b.title]
    if b.url:
        parts.append(b.url)
    return " \n".join([p for p in parts if p])


def _default_labels_from_rules() -> List[str]:
    # derive labels from rules.example.yaml if present
    rules_path = Path("configs/rules.example.yaml")
    rules = load_rules(rules_path)
    seen: Set[str] = set()
    for section in ("domains", "keywords", "lang"):
        mapping = rules.get(section, {}) or {}
        for tags in mapping.values():
            for t in tags:
                seen.add(str(t))
    return sorted(seen)
