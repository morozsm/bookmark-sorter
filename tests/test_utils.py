from pathlib import Path
from cbclean.utils import strip_www, filter_query, fnmatch_like, normalize_url, domain_of


def test_strip_www():
    assert strip_www("www.example.com") == "example.com"
    assert strip_www("sub.example.com") == "sub.example.com"


def test_filter_query_with_patterns():
    q = "utm_source=x&id=1&gclid=2&keep=y"
    out = filter_query(q, ["utm_*", "gclid"])
    assert out == "id=1&keep=y"


def test_fnmatch_like():
    assert fnmatch_like("utm_source", "utm_*")
    assert not fnmatch_like("utm_source", "gclid*")
    assert fnmatch_like("ref", "ref")


def test_normalize_url_collapse_and_fragment():
    url = "https://www.ex.com//a//b#frag?id=1"
    out = normalize_url(url, strip_params=[], strip_fragments=True, strip_www_flag=True)
    assert out == "https://ex.com/a/b"


def test_domain_of_invalid():
    assert domain_of("not a url") is None

