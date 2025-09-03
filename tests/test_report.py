from pathlib import Path
from cbclean.report import render_reports
from cbclean.utils import Bookmark


def test_render_reports_creates_files(tmp_path: Path):
    bookmarks = [Bookmark(id="1", title="Ex", url="https://ex.com", folder_path="Bar")]
    dups = []
    plan = [{"bookmark_id": "1", "action": "update_url", "reason": "normalized"}]
    render_reports(
        bookmarks=bookmarks,
        duplicates=dups,
        plan=plan,
        out_dir=tmp_path,
        formats=["html", "md"],
        templates_dir=Path("templates"),
    )
    assert (tmp_path / "report.html").exists()
    assert (tmp_path / "report.md").exists()

