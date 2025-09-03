from pathlib import Path
from cbclean.apply import export_bookmarks_html
from cbclean.utils import Bookmark


def test_export_creates_file(tmp_path: Path):
    out = tmp_path / "bookmarks.cleaned.html"
    bookmarks = [Bookmark(id="1", title="Ex", url="https://example.com", normalized_url="https://example.com", folder_path="Bookmarks Bar")]
    export_bookmarks_html(bookmarks, out)
    assert out.exists()
    content = out.read_text(encoding="utf-8")
    assert "NETSCAPE-Bookmark-file-1" in content

