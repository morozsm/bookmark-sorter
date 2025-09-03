# bookmark-sorter

CLI to clean and organize Chrome bookmarks. See AGENTS.md for contributor guidelines and configs/config.example.yaml for running the pipeline:

```
python -m venv .venv && source .venv/bin/activate
pip install -e .[dev]
cbclean process --config configs/config.example.yaml
```
