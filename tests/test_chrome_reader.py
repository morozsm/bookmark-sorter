from pathlib import Path
from cbclean.chrome_reader import read_chrome_json, read_bookmarks_html


def test_read_chrome_json_sample():
    p = Path("data/samples/bookmarks.sample.json")
    items = read_chrome_json(p)
    assert any(b.title == "Python Docs" for b in items)


def test_read_bookmarks_html_minimal(tmp_path: Path):
    html = tmp_path / "bookmarks.html"
    html.write_text(
        """
        <!DOCTYPE NETSCAPE-Bookmark-file-1>
        <DL><p>
          <DT><H3>Bar</H3>
          <DL><p>
            <DT><A HREF="https://example.com">Ex</A>
          </DL><p>
        </DL><p>
        """,
        encoding="utf-8",
    )
    items = read_bookmarks_html(html)
    assert any(b.url == "https://example.com" for b in items)


def test_read_bookmarks_html_fallback_flat(tmp_path: Path):
    html = tmp_path / "flat.html"
    html.write_text('<A HREF="https://flat.example">Flat</A>', encoding="utf-8")
    items = read_bookmarks_html(html)
    assert items and items[0].url == "https://flat.example"


def test_read_bookmarks_html_nested_dl_branch(tmp_path: Path):
    # Construct unusual nesting to exercise the 'dl' branch
    html = tmp_path / "nested.html"
    html.write_text(
        """
        <DL><p>
          <DL><p>
            <DT><A HREF="https://nested.example">Nested</A>
          </DL><p>
        </DL><p>
        """,
        encoding="utf-8",
    )
    items = read_bookmarks_html(html)
    assert any(b.url == "https://nested.example" for b in items)
