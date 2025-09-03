from cbclean.utils import normalize_url


def test_normalize_basic():
    url = "https://www.example.com//a//b/?utm_source=x&gclid=1&id=42#frag"
    out = normalize_url(url, strip_params=["utm_*", "gclid"], strip_fragments=True, strip_www_flag=True)
    assert out == "https://example.com/a/b/?id=42"
