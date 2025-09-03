from pathlib import Path
from cbclean.backup import backup_file


def test_backup_file(tmp_path: Path):
    src = tmp_path / "Bookmarks"
    src.write_text("data", encoding="utf-8")
    dst_dir = tmp_path / "bk"
    out = backup_file(src, dst_dir)
    assert out.exists()
    assert out.read_text(encoding="utf-8") == "data"

