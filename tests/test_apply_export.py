from pathlib import Path
from cbclean.apply import export_bookmarks_html
from cbclean.utils import Bookmark


def test_export_creates_file(tmp_path: Path):
    out = tmp_path / "bookmarks.cleaned.html"
    bookmarks = [
        Bookmark(
            id="1",
            title="Ex",
            url="https://example.com",
            normalized_url="https://example.com",
            folder_path="Bookmarks Bar",
        )
    ]
    export_bookmarks_html(bookmarks, out)
    assert out.exists()
    content = out.read_text(encoding="utf-8")
    assert "NETSCAPE-Bookmark-file-1" in content


def test_export_group_by_tag(tmp_path):
    out = tmp_path / "bookmarks.cleaned.html"
    bookmarks = [
        Bookmark(
            id="1",
            title="Ex",
            url="https://example.com",
            normalized_url="https://example.com",
            folder_path="Bookmarks Bar",
            tags=["Dev"],
        ),
        Bookmark(
            id="2",
            title="Py",
            url="https://python.org",
            normalized_url="https://python.org",
            folder_path="Bookmarks Bar",
            tags=["Dev"],
        ),
        Bookmark(
            id="3",
            title="NoTag",
            url="https://no.tag",
            normalized_url="https://no.tag",
            folder_path="Bookmarks Bar",
            tags=[],
        ),
    ]
    export_bookmarks_html(bookmarks, out, group_by="tag")
    text = out.read_text(encoding="utf-8")
    # Expect Dev group and Uncategorized group
    assert "<H3>Dev</H3>" in text
    assert "<H3>Uncategorized</H3>" in text


def test_export_group_by_tag_all(tmp_path):
    out = tmp_path / "bookmarks.cleaned.html"
    bookmarks = [
        Bookmark(
            id="1",
            title="Ex",
            url="https://example.com",
            normalized_url="https://example.com",
            folder_path="Bookmarks Bar",
            tags=["Dev", "Code"],
        ),
    ]
    export_bookmarks_html(bookmarks, out, group_by="tag-all")
    text = out.read_text(encoding="utf-8")
    assert "<H3>Dev</H3>" in text and "<H3>Code</H3>" in text


def test_export_skips_items_without_url(tmp_path):
    out = tmp_path / "bookmarks.cleaned.html"
    bookmarks = [Bookmark(id="1", title="NoUrl", url=None, folder_path="Bar", tags=["Dev"])]
    export_bookmarks_html(bookmarks, out, group_by="tag-all")
    text = out.read_text(encoding="utf-8")
    # Group exists but no anchor link
    assert "<H3>Dev</H3>" in text
    assert "<DT><A" not in text


def test_export_tag_all_uncategorized(tmp_path):
    out = tmp_path / "bookmarks.cleaned.html"
    bookmarks = [
        Bookmark(
            id="1",
            title="X",
            url="https://x",
            normalized_url="https://x",
            folder_path="Bar",
            tags=[],
        )
    ]
    export_bookmarks_html(bookmarks, out, group_by="tag-all")
    text = out.read_text(encoding="utf-8")
    assert "<H3>Uncategorized</H3>" in text


def test_export_group_by_tag_hier(tmp_path):
    out = tmp_path / "bookmarks.cleaned.html"
    bookmarks = [
        Bookmark(
            id="1",
            title="Linux Doc",
            url="https://linux.example",
            normalized_url="https://linux.example",
            tags=["Docs/Reference", "Dev/Linux"],
        ),
        Bookmark(
            id="2",
            title="K8s",
            url="https://k8s.io",
            normalized_url="https://k8s.io",
            tags=["Dev/Kubernetes"],
        ),
    ]
    export_bookmarks_html(bookmarks, out, group_by="tag-hier")
    text = out.read_text(encoding="utf-8")
    # Nested headings should appear
    assert text.count("<H3>Dev</H3>") == 1
    assert "<H3>Linux</H3>" in text
    assert "<H3>Kubernetes</H3>" in text
    assert "<H3>Docs</H3>" in text and "<H3>Reference</H3>" in text
