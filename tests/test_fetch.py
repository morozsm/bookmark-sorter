from cbclean.fetch import check_liveness, extract_text_from_html
from cbclean.utils import Bookmark


def test_check_liveness_disabled_marks_unknown():
    b = [Bookmark(id="1", title="t", url="https://ex.com")]
    check_liveness(b, enabled=False)
    assert b[0].liveness == "unknown"


def test_check_liveness_enabled_marks_unchecked():
    b = [Bookmark(id="1", title="t", url="https://ex.com")]
    check_liveness(b, enabled=True)
    assert b[0].liveness == "unchecked"


def test_extract_text_from_html_basic():
    html = """
    <html><head><title>X</title><style>body{}</style><script>var x=1</script></head>
    <body><h1>Header</h1><p>Hello <b>world</b>!    </p></body></html>
    """
    text = extract_text_from_html(html, max_chars=50)
    assert "Header" in text and "Hello world" in text
