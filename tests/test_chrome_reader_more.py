from pathlib import Path
import json
from cbclean.chrome_reader import read_chrome_json, read_bookmarks_html


def test_read_chrome_json_handles_non_dict_nodes(tmp_path: Path):
    p = tmp_path / "bk.json"
    # roots contains a list instead of a dict to exercise early return
    p.write_text(json.dumps({"roots": {"bookmark_bar": [1, 2, 3]}}), encoding="utf-8")
    items = read_chrome_json(p)
    # Should not crash; no items produced
    assert items == []


def test_read_bookmarks_html_h3_then_sibling_dl(tmp_path: Path):
    html = tmp_path / "bk.html"
    html.write_text(
        """
        <DL><p>
          <DT><H3>Folder</H3></DT>
          <DL><p>
            text
            <DT><A HREF="https://example.com/a">A</A></DT>
          </DL><p>
        </DL><p>
        """,
        encoding="utf-8",
    )
    items = read_bookmarks_html(html)
    assert any(b.url == "https://example.com/a" for b in items)
