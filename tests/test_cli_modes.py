from pathlib import Path
import os
from cbclean.cli import process as cli_process


def test_cli_other_modes(tmp_path: Path):
    # HTML input path
    html = tmp_path / "in.html"
    html.write_text('<DL><p><DT><A HREF="https://example.com">Ex</A></DL><p>', encoding="utf-8")
    # Run embeddings mode with dry-run
    cfg1 = tmp_path / "cfg1.yaml"
    cfg1.write_text(
        f"""
input:
  import_html: "{html.as_posix()}"
output:
  export_dir: "{(tmp_path / 'o1').as_posix()}"
categorize:
  mode: "embeddings"
network:
  enabled: true
apply:
  mode: "dry_run"
        """,
        encoding="utf-8",
    )
    os.chdir(Path(__file__).resolve().parents[1])
    cli_process(config=str(cfg1))
    assert (tmp_path / "o1" / "report.html").exists()

    # LLM mode
    cfg2 = tmp_path / "cfg2.yaml"
    cfg2.write_text(
        f"""
input:
  import_html: "{html.as_posix()}"
output:
  export_dir: "{(tmp_path / 'o2').as_posix()}"
categorize:
  mode: "llm"
network:
  enabled: false
apply:
  mode: "export_html"
        """,
        encoding="utf-8",
    )
    cli_process(config=str(cfg2))
    assert (tmp_path / "o2" / "bookmarks.cleaned.html").exists()

