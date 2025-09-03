from pathlib import Path
from cbclean.apply import export_bookmarks_html
from cbclean.utils import Bookmark


def test_export_escapes_html_chars(tmp_path: Path):
    out = tmp_path / "bookmarks.cleaned.html"
    b = [
        Bookmark(
            id="1",
            title='A&B<>"',
            url='https://ex.com?a=1&b="2"',
            normalized_url='https://ex.com?a=1&b="2"',
            folder_path="F",
        )
    ]
    export_bookmarks_html(b, out)
    text = out.read_text(encoding="utf-8")
    assert "A&amp;B&lt;&gt;&quot;" in text
    assert "a=1&amp;b=&quot;2&quot;" in text
