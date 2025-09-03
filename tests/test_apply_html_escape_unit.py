from cbclean.apply import html_escape


def test_html_escape_direct():
    s = '>&"<'
    out = html_escape(s)
    assert out == "&gt;&amp;&quot;&lt;"
