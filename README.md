# bookmark-sorter (cbclean)

Command-line tool to clean and organize Chrome bookmarks. It normalizes URLs, removes duplicates, assigns tags via rules, generates a change plan, and exports “clean” bookmarks to standard HTML with HTML/Markdown reports.

![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)
![Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)
![Lint: Ruff](https://img.shields.io/badge/lint-ruff-46aef7.svg)
[![CI](https://github.com/morozsm/bookmark-sorter/actions/workflows/ci.yml/badge.svg)](https://github.com/morozsm/bookmark-sorter/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/morozsm/bookmark-sorter/branch/main/graph/badge.svg)](https://codecov.io/gh/morozsm/bookmark-sorter)

## Features
- Import from Chrome profile JSON or exported HTML (Netscape format).
- URL normalization: drop tracking params, strip “www”, remove fragments, collapse double slashes.
- Deduplication: hard duplicates by normalized URL and soft duplicates by title similarity.
- Categorization:
  - Rule-based: domains and keywords map to tag lists.
  - AI (optional):
    - Embeddings with `sentence-transformers` to assign tags by semantic similarity.
    - External LLM (OpenAI-compatible) to label bookmarks using a prompt-guided schema.
- Export: generate `bookmarks.cleaned.html` suitable for Chrome import (never writes back to profile files).
- Reports: `report.html` and `report.md` with summary and planned changes.

Note: link liveness checks and embeddings/LLM modes are architected but simplified/stubbed in this version.

## Quick Start
1) Prerequisites: Python 3.11+

2) Install
```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install -e '.[dev]'
```
Using zsh? Quote extras: `pip install -e '.[dev]'`.

Fast alternative with uv
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv .venv
uv pip install -p .venv/bin/python -e '.[dev]'
```

3) Run (demo config)
```bash
cbclean --config configs/config.local.yaml
```
Outputs are written to `out/`: `bookmarks.cleaned.html`, `report.html`, `report.md`.

## Screenshot
- Example report (HTML): open `out/report.html` after a run.
- To include a static image in the repo, save a capture as `docs/screenshot-report.png` and Git will render it in this section.

## Configuration
Primary example: `configs/config.example.yaml`. Key fields:
```yaml
input:
  bookmarks_path: "~/.config/google-chrome/Default/Bookmarks"  # or data/samples/bookmarks.sample.json
  import_html: ""  # path to exported bookmarks HTML (if not reading JSON)
output:
  export_dir: "./out"
  report_formats: ["html", "md"]
normalize:
  strip_query_params: ["utm_*", "gclid", "yclid", "fbclid", "ref", "ref_src"]
  strip_fragments: true
  strip_www: true
dedup:
  title_similarity_threshold: 0.90
categorize:
  mode: "rules"            # rules | embeddings | llm
  rules_file: "./configs/rules.example.yaml"
apply:
  mode: "export_html"       # export_html | dry_run
network:
  enabled: false            # liveness is simplified and performs no requests
```
Rules example: `configs/rules.example.yaml` (domains/keywords → tags).

## Common Workflows
- Import from JSON: set `input.bookmarks_path` to your Chrome profile `Bookmarks` file. The app only exports; it never edits profile files.
- Import from HTML: set `input.import_html` and `apply.mode: export_html`.
- Quick demo: use `configs/config.local.yaml` (points to `data/samples/bookmarks.sample.json`).
- AI categorization: install extras `pip install -e '.[embed]'` (or `uv pip install -p .venv/bin/python -e '.[embed]'`), set `categorize.mode: embeddings`, and `apply.group_by: tag`. The first run will download the model (e.g., `all-MiniLM-L6-v2`).
 - LLM categorization (OpenAI-compatible):
   - Install extras: `pip install -e '.[llm]'` (or with uv).
   - Set API key: `export OPENAI_API_KEY=sk-...` (or configure `categorize.llm.api_key_env`).
   - In config: `categorize.mode: llm`, optionally provide `categorize.llm.labels` to guide categories, and set `apply.group_by: tag-all`.
   - Controls: `categorize.llm.batch_size` (default 30), `temperature` (default 0.0), `only_uncertain` (classify only items without tags).

## Architecture & Modules
Pipeline: import → normalize → dedup → classify → plan → apply → report.
- `chrome_reader.py` — read from JSON/HTML.
- `normalize.py` — URL normalization.
- `dedup.py` — hard and soft duplicates.
- `classify_rules.py` — tag assignment via YAML rules.
- `classify_embed.py` — AI tagging via sentence-transformers (optional dependency). Falls back to no-op if not installed.
- `fetch.py` — liveness stub for MVP.
- `propose.py` — change plan generation.
- `apply.py` — HTML export (no writes to Chrome profile).
- `report.py` — reports via Jinja2 templates (`templates/`).
- `storage.py` — SQLite cache for future network checks.

Repository Layout
- `src/cbclean/` — package and CLI (`cbclean`).
- `configs/` — example configs and tagging rules.
- `data/samples/` — sample inputs.
- `templates/` — report templates.
- `tests/` — pytest suite.

## Development & Quality
- Tests: `pytest -q` (or `uv run pytest -q`); coverage: `pytest --cov=cbclean --cov-report=term-missing`.
- Lint/format: `ruff check .`, `black .` (or `uv run ...`).
- Types: `mypy src/cbclean` (or `uv run mypy src/cbclean`).
- Dev install: `pip install -e '.[dev]'`.
Contributor guidelines: see `AGENTS.md`.

## Safety & Limitations
- The tool never modifies Chrome profile files; changes are exported to `out/`.
- Current version does not perform network liveness checks.
- Fully offline operation is supported (rules, normalization, deduplication, reporting).
- LLM mode sends bookmark titles/URLs to the configured provider; review provider policies and redact sensitive data as needed.

## Troubleshooting & FAQ
- zsh “no matches found: .[dev]”: quote it — `pip install -e '.[dev]'`.
- IDE can’t import `cbclean`: mark `src/` as Sources Root or set `PYTHONPATH=src`. This repo includes `tests/conftest.py` and `.pylintrc` to help IDEs.
- Empty JSON import: verify `input.bookmarks_path` and permissions.

## Roadmap
- Async liveness checks (aiohttp) with SQLite cache.
- Embeddings-based and LLM-assisted categorization.
- Rich dead-link handling (Wayback, move/delete strategies).
- Additional performance metrics and detailed reports.

---

Note about badges:
- Replace `USER_OR_ORG` in the CI and Codecov badge URLs with your actual GitHub org/user once the repo is pushed to GitHub. Codecov badge requires the Codecov app or `CODECOV_TOKEN` secret in the repo settings.

## Comparison With Alternatives
- Chrome Bookmark Manager:
  - Pros: built-in UI, quick manual edits.
  - Cons: no URL normalization, limited dedup, no reproducible rules or reports.
- Browser cleanup/dedup extensions:
  - Pros: convenient, visual.
  - Cons: require browser permissions, may modify profile directly, limited offline reproducibility.
- Cloud services (e.g., online bookmark managers):
  - Pros: sharing, search, rich metadata.
  - Cons: requires account/network, may not preserve Chrome HTML import/export fidelity, not deterministic offline.
- This tool:
  - Pros: offline-first, reproducible configs, exports-only (safe), CLI-friendly automation, HTML/MD reports.
  - Cons: CLI-based; advanced features (liveness, embeddings/LLM) are stubs in MVP.
