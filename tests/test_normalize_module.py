from cbclean.normalize import normalize_bookmarks
from cbclean.utils import Bookmark


def test_normalize_bookmarks_applies_to_each():
    b = [Bookmark(id="1", title="t", url="https://www.ex.com/?utm_source=x&id=1")]
    normalize_bookmarks(b, strip_params=["utm_*"], strip_fragments=True, strip_www=True)
    assert b[0].normalized_url == "https://ex.com/?id=1"


def test_normalize_bookmarks_skips_missing_url():
    b = [Bookmark(id="1", title="t", url=None)]
    normalize_bookmarks(b, strip_params=["utm_*"], strip_fragments=True, strip_www=True)
    assert b[0].normalized_url is None
