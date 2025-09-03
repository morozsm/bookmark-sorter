from cbclean.utils import Bookmark
from cbclean.dedup import deduplicate


def test_deduplicate_by_normalized_url():
    a = Bookmark(id="1", title="A", url="https://ex.com/?id=1", normalized_url="https://ex.com/?id=1")
    b = Bookmark(id="2", title="A copy", url="https://ex.com/?id=1", normalized_url="https://ex.com/?id=1")
    keep, dups = deduplicate([a, b], title_threshold=0.9, prefer_shorter_url=True)
    assert len(keep) == 1
    assert len(dups) == 1


def test_deduplicate_soft_by_title():
    a = Bookmark(id="1", title="Python Docs", url="https://docs.python.org/3/")
    b = Bookmark(id="2", title="python documentation", url="https://docs.python.org/3/tutorial/")
    keep, dups = deduplicate([a, b], title_threshold=0.7, prefer_shorter_url=True)
    assert len(keep) == 1
    assert len(dups) == 1


def test_deduplicate_fallback_keep_first_when_no_prefer_shorter():
    a = Bookmark(id="1", title="A", url="https://ex.com/longer/path")
    b = Bookmark(id="2", title="A", url="https://ex.com/longer/path")
    keep, dups = deduplicate([a, b], title_threshold=0.9, prefer_shorter_url=False)
    assert keep[0].id == "1"


def test_deduplicate_skips_items_without_key():
    a = Bookmark(id="1", title="No URL")
    keep, dups = deduplicate([a], title_threshold=0.9, prefer_shorter_url=True)
    assert len(keep) == 0 or keep[0].url is None
