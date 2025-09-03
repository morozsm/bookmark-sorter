from __future__ import annotations

from typing import Iterable, List, Optional, Sequence, Set, Tuple
from pathlib import Path
import json
import os

from .utils import Bookmark
from .classify_rules import load_rules


def classify_by_llm(
    bookmarks: List[Bookmark],
    *,
    provider: str = "openai",
    model: str = "gpt-4o-mini",
    api_key_env: str = "OPENAI_API_KEY",
    api_base: Optional[str] = None,
    temperature: float = 0.0,
    labels: Optional[Sequence[str]] = None,
    batch_size: int = 30,
    only_uncertain: bool = True,
    client: Optional[object] = None,
    allow_new_labels: bool = True,
    max_new_labels_per_batch: int = 10,
) -> None:
    """Classify bookmarks into labels using an external LLM.

    Network calls are optional: if the provider SDK isn't installed or no key,
    function exits quietly. Client can be injected for testing.
    """
    # Resolve labels
    label_list = _resolve_labels(labels)
    if not label_list and not allow_new_labels:
        return None

    # Select candidates
    items: List[Bookmark] = []
    for b in bookmarks:
        if only_uncertain and b.tags:
            continue
        items.append(b)
    if not items:
        return None

    # Build client lazily
    if client is None:
        if provider == "openai":
            try:
                from openai import OpenAI  # type: ignore
            except Exception:
                return None
            api_key = os.environ.get(api_key_env)
            if not api_key:
                return None
            client = (
                OpenAI(api_key=api_key, base_url=api_base) if api_base else OpenAI(api_key=api_key)
            )
        else:
            return None

    # Process in batches
    # Maintain evolving allowed label set if dynamic labels are enabled
    allowed_set: Set[str] = set(label_list)

    for chunk in _chunks(items, max(1, batch_size)):
        prompt = _build_prompt(
            chunk,
            sorted(allowed_set),
            allow_new_labels=allow_new_labels,
            max_new=max_new_labels_per_batch,
        )
        content = _chat(client, model, temperature, prompt)
        try:
            data = json.loads(content)
        except Exception:
            # Try to recover JSON enclosed in code fences
            content_stripped = _extract_json(content)
            data = json.loads(content_stripped)
        assignments, new_labels = _parse_result(data)
        if allow_new_labels and new_labels:
            for nl in new_labels[:max_new_labels_per_batch]:
                sl = _sanitize_label(str(nl))
                if sl:
                    allowed_set.add(sl)
        _apply_labels(chunk, assignments, sorted(allowed_set))


def _resolve_labels(labels: Optional[Sequence[str]]) -> List[str]:
    if labels:
        return sorted({str(x) for x in labels})
    rules_path = Path("configs/rules.example.yaml")
    rules = load_rules(rules_path)
    seen = set()
    for section in ("domains", "keywords", "lang"):
        mapping = rules.get(section, {}) or {}
        for tags in mapping.values():
            for t in tags:
                seen.add(str(t))
    return sorted(seen)


def _chunks(xs: Sequence[Bookmark], n: int) -> Iterable[Sequence[Bookmark]]:
    i = 0
    L = len(xs)
    while i < L:
        yield xs[i : i + n]
        i += n


def _build_prompt(
    items: Sequence[Bookmark],
    labels: Sequence[str],
    *,
    allow_new_labels: bool = True,
    max_new: int = 10,
) -> str:
    label_str = ", ".join(labels)
    lines = [
        "You are a bookmark classifier.",
        "Classify each bookmark (title + url) into 1–2 topical labels.",
        "Rules:",
        "- Prefer the allowed labels (exact strings) listed below.",
        "- Do NOT use language or country labels; categorize by topic.",
        "- If hierarchical labels are present (like 'Dev/Linux'), use them directly.",
        f"Allowed labels: [{label_str}]",
    ]
    if allow_new_labels:
        lines += [
            f"- You MAY invent up to {max_new} NEW topical labels when none of the allowed labels fit.",
            "- New labels MUST be concise (1–3 words per segment), topical, and may be hierarchical using '/'.",
            "- Avoid generic buckets like 'Tools' or language labels like 'RU'.",
        ]
    lines += [
        "Output JSON only.",
        "Format:",
        "{",
        '  "assignments": [{index, labels}],',
        '  "new_labels": [string, ...]',
        "}",
        "Input:",
    ]
    for idx, b in enumerate(items):
        title = b.title or ""
        url = b.url or ""
        lines.append(f"- [{idx}] {title} | {url}")
        if getattr(b, "content_snippet", None):
            # Include trimmed context to improve classification
            lines.append(f"  Context: {b.content_snippet}")
    lines.append("Output as JSON object as specified above:")
    return "\n".join(lines)


def _chat(client: object, model: str, temperature: float, prompt: str) -> str:
    # OpenAI SDK client
    if hasattr(client, "chat") and hasattr(client.chat, "completions"):
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Classify bookmarks into provided labels."},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
        )
        return resp.choices[0].message.content or "[]"
    # Fallback: assume client(model, prompt) -> content
    return str(client(model, prompt))


def _extract_json(text: str) -> str:
    import re

    m = re.search(r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```", text, flags=re.S)
    if m:
        return m.group(1)
    return text


def _apply_labels(items: Sequence[Bookmark], result: object, allowed: Sequence[str]) -> None:
    if not isinstance(result, list):
        return
    allowed_set = set(allowed)
    for obj in result:
        if not isinstance(obj, dict):
            continue
        idx = obj.get("index")
        labs = obj.get("labels", [])
        if not isinstance(idx, int) or not isinstance(labs, list):
            continue
        labels: List[str] = []
        for x in labs:
            sx = _sanitize_label(str(x))
            if sx and sx in allowed_set:
                labels.append(sx)
        if 0 <= idx < len(items) and labels:
            b = items[idx]
            b.tags = sorted(set((b.tags or []) + labels))


def _parse_result(data: object) -> Tuple[object, List[str]]:
    if isinstance(data, dict):
        assignments = data.get("assignments", [])
        new_labels = data.get("new_labels", [])
        if not isinstance(assignments, list):
            assignments = []
        if not isinstance(new_labels, list):
            new_labels = []
        return assignments, [str(x) for x in new_labels]
    if isinstance(data, list):
        return data, []
    return [], []


def _sanitize_label(s: str) -> str:
    s = s.strip()
    if not s:
        return ""
    if s.lower() in {"ru", "en", "ua", "de", "lang", "language"}:
        return ""
    parts = [p.strip() for p in s.split("/") if p.strip()]
    if not parts:
        return ""
    clean_parts: List[str] = []
    import re

    for p in parts[:3]:
        q = re.sub(r"[^A-Za-z0-9\- _+]+", "", p)
        q = re.sub(r"\s+", " ", q).strip()
        if not q:
            continue
        if len(q) > 32:
            q = q[:32]
        clean_parts.append(q)
    if not clean_parts:
        return ""
    return "/".join(clean_parts)
