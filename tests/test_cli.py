from pathlib import Path
import os
from cbclean.cli import process as cli_process


def test_cli_process_end_to_end(tmp_path: Path):
    cfg = tmp_path / "config.yaml"
    rules = tmp_path / "rules.yaml"
    rules.write_text("domains:\n  example.com: [Test]\n", encoding="utf-8")
    # use sample JSON as input
    cfg.write_text(
        f"""
input:
  bookmarks_path: "data/samples/bookmarks.sample.json"
output:
  export_dir: "{tmp_path.as_posix()}"
categorize:
  mode: "rules"
  rules_file: "{rules.as_posix()}"
network:
  enabled: false
apply:
  mode: "export_html"
        """,
        encoding="utf-8",
    )
    # Ensure CWD is project root so templates and sample data resolve
    os.chdir(Path(__file__).resolve().parents[1])
    # Call command function directly to avoid CLI parsing issues in CI
    cli_process(config=str(cfg))
    assert (tmp_path / "bookmarks.cleaned.html").exists()
    assert (tmp_path / "report.html").exists()
    assert (tmp_path / "report.md").exists()
