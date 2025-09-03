from __future__ import annotations

from pathlib import Path
from typing import Dict, List
from jinja2 import Environment, FileSystemLoader, select_autoescape
from .utils import Bookmark, ensure_dir


def render_reports(
    *,
    bookmarks: List[Bookmark],
    duplicates: List[Bookmark],
    plan: List[Dict],
    out_dir: Path,
    formats: List[str],
    templates_dir: Path,
) -> None:
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    ctx = {
        "total": len(bookmarks),
        "duplicates": len(duplicates),
        "by_folder": _by_folder(bookmarks),
        "plan": plan,
    }
    ensure_dir(out_dir)
    if "html" in formats:
        tmpl = env.get_template("report.html.j2")
        (out_dir / "report.html").write_text(tmpl.render(**ctx), encoding="utf-8")
    if "md" in formats:
        tmpl = env.get_template("report.md.j2")
        (out_dir / "report.md").write_text(tmpl.render(**ctx), encoding="utf-8")


def _by_folder(bookmarks: List[Bookmark]) -> Dict[str, int]:
    m: Dict[str, int] = {}
    for b in bookmarks:
        key = b.folder_path or "Bookmarks"
        m[key] = m.get(key, 0) + 1
    return dict(sorted(m.items(), key=lambda kv: kv[0]))
