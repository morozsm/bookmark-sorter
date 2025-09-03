from __future__ import annotations

from pathlib import Path
import typer
from rich import print

from .config import AppConfig
from .chrome_reader import read_bookmarks_html, read_chrome_json
from .backup import backup_file
from .normalize import normalize_bookmarks
from .dedup import deduplicate
from .classify_rules import load_rules, classify_by_rules
from .classify_embed import classify_by_embeddings
from .classify_llm import classify_by_llm
from .fetch import check_liveness, enrich_with_content
from .propose import propose_changes
from .apply import export_bookmarks_html
from .report import render_reports
from .utils import ensure_dir


app = typer.Typer(add_completion=False, help="Chrome bookmarks cleaner and organizer")


@app.command()
def process(
    config: str = typer.Option(
        "configs/config.example.yaml", "--config", "-c", help="Path to YAML config"
    ),
) -> None:
    """Run full pipeline: read -> normalize -> dedup -> classify -> plan -> apply -> report"""
    cfg = _load_config(Path(config))

    # Load input
    bookmarks = _load_input(cfg)
    print(f"Loaded [bold]{len(bookmarks)}[/] bookmarks")

    # Normalize
    normalize_bookmarks(
        bookmarks,
        strip_params=cfg.normalize.strip_query_params,
        strip_fragments=cfg.normalize.strip_fragments,
        strip_www=cfg.normalize.strip_www,
    )

    # Deduplicate
    deduped, duplicates = deduplicate(
        bookmarks,
        title_threshold=cfg.dedup.title_similarity_threshold,
        prefer_shorter_url=cfg.dedup.prefer_shorter_url,
    )
    print(f"Deduplicated to [bold]{len(deduped)}[/] items, duplicates: {len(duplicates)}")

    # Classify
    if cfg.categorize.mode == "rules":
        rules = load_rules(Path(cfg.categorize.rules_file))
        classify_by_rules(deduped, rules)
    elif cfg.categorize.mode == "embeddings":
        classify_by_embeddings(
            deduped,
            model_name=cfg.categorize.embeddings.model,
            labels=cfg.categorize.embeddings.labels,
            top_k=cfg.categorize.embeddings.top_k,
            score_threshold=cfg.categorize.embeddings.score_threshold,
        )
    elif cfg.categorize.mode == "llm":
        if cfg.network.fetch_content:
            enrich_with_content(
                deduped,
                enabled=cfg.network.enabled,
                timeout_sec=cfg.network.timeout_sec,
                concurrent=cfg.network.concurrent,
                user_agent=cfg.network.user_agent,
                max_chars=cfg.network.max_content_chars,
            )
        classify_by_llm(
            deduped,
            provider=cfg.categorize.llm.provider,
            model=cfg.categorize.llm.model,
            api_key_env=cfg.categorize.llm.api_key_env,
            api_base=cfg.categorize.llm.api_base,
            temperature=cfg.categorize.llm.temperature,
            labels=cfg.categorize.llm.labels,
            batch_size=cfg.categorize.llm.batch_size,
            only_uncertain=cfg.categorize.llm.only_uncertain,
            allow_new_labels=cfg.categorize.llm.allow_new_labels,
            max_new_labels_per_batch=cfg.categorize.llm.max_new_labels_per_batch,
        )

    # Liveness (stubbed for MVP)
    check_liveness(deduped, enabled=cfg.network.enabled)

    # Plan
    plan_items = propose_changes(bookmarks, deduped, duplicates)
    plan_dicts = [
        dict(action=p.action, reason=p.reason, bookmark_id=p.bookmark_id) for p in plan_items
    ]

    # Apply
    out_dir = Path(cfg.output.export_dir)
    ensure_dir(out_dir)
    if cfg.apply.mode == "export_html":
        export_bookmarks_html(
            deduped, out_dir / "bookmarks.cleaned.html", group_by=cfg.apply.group_by
        )
        print(f"Exported HTML to {out_dir / 'bookmarks.cleaned.html'}")
    else:
        print("Dry-run: no export performed")

    # Report
    render_reports(
        bookmarks=deduped,
        duplicates=duplicates,
        plan=plan_dicts,
        out_dir=out_dir,
        formats=cfg.output.report_formats,
        templates_dir=Path("templates"),
    )
    print(f"Reports written to {out_dir}")


def _load_config(path: Path) -> AppConfig:
    # Load using ruamel.yaml if available; otherwise use defaults
    try:
        from ruamel.yaml import YAML  # type: ignore

        yaml = YAML(typ="safe")
        data = yaml.load(path.read_text(encoding="utf-8")) if path.exists() else {}
    except Exception:
        data = {}
    return AppConfig.model_validate(data or {})


def _load_input(cfg: AppConfig):
    html = cfg.input.import_html.strip()
    if html:
        src = Path(html).expanduser()
        if src.exists():
            return read_bookmarks_html(src)
    # Fallback to JSON
    json_path = Path(cfg.input.bookmarks_path).expanduser()
    if json_path.exists():
        # optional backup into out dir
        out_dir = Path(cfg.output.export_dir)
        backup_file(json_path, out_dir / "backups")
        return read_chrome_json(json_path, profile="Default")
    return []


if __name__ == "__main__":
    app()
