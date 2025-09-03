# Repository Guidelines

## Project Structure & Modules
- `src/cbclean/`: Python package (CLI, core logic). Example modules: `cli.py`, `normalize.py`, `dedup.py`, `report.py`.
- `tests/`: Pytest suite (e.g., `test_normalize.py`, `test_dedup.py`).
- `configs/`: Sample and user configs (e.g., `config.example.yaml`, `rules.example.yaml`).
- `templates/`: Jinja2 templates for `report.html` and `report.md`.
- `data/`: Sample inputs and fixtures; not for secrets.
- `out/`: Generated exports and reports (git‑ignored).

## Build, Test, and Dev Commands
- Create venv: `python -m venv .venv && source .venv/bin/activate` (Windows: `Scripts\activate`).
- Install (dev): `python -m pip install -U pip && pip install -e '.[dev]'`.
- Run CLI: `cbclean --config configs/config.example.yaml` (single-root command; no subcommands). For a demo, use `configs/config.local.yaml`.
- Lint: `ruff check .`  • Format: `black .`  • Types: `mypy src/cbclean`.
- Tests: `pytest -q`  • With coverage: `pytest --cov=cbclean --cov-report=term-missing`.
- Pre-commit: `pre-commit install` then `pre-commit run -a` before commits.

## Coding Style & Naming
- Python 3.11+, 4‑space indentation, type hints required in core modules.
- Naming: packages `snake_case`, classes `PascalCase`, functions/vars `snake_case`.
- Keep modules focused (e.g., URL logic in `normalize.py`, storage in `storage.py`).
- Use Black (format), Ruff (lint), Mypy strict on core; fix warnings or justify with comments.

## Testing Guidelines
- Framework: Pytest. Place tests under `tests/`, name `test_*.py` and mirror module names.
- Aim for high coverage of normalization, deduplication, and classification paths (≥80% suggested).
- Use small, deterministic fixtures under `data/` and `tests/fixtures/`.
- CI runs lint, type‑check, and tests; ensure local parity before PRs.

## Commit & PR Guidelines
- Commits: Prefer Conventional Commits (e.g., `feat: normalize URLs`, `fix: handle soft 404`).
- PRs: clear description, linked issue, repro steps, and scope. Include:
  - Config used and sample input (if applicable).
  - Dry‑run plan excerpt and, when relevant, links to generated `out/report.*`.
  - Notes on performance/async changes and any migration steps.

## Security & Config Tips
- Do not write to Chrome profile files; export only to `out/`.
- Keep API keys and private data out of the repo; use local env/config overrides.
- Defaults live in code; validate configs with pydantic and document any breaking changes.
