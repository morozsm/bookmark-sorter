from cbclean.classify_embed import classify_by_embeddings
from cbclean.classify_llm import classify_by_llm
from cbclean.cluster import cluster_bookmarks
from cbclean.utils import Bookmark


def test_classify_and_cluster_stubs_noop():
    b = [Bookmark(id="1", title="t", url="https://ex.com")]
    assert classify_by_embeddings(b) is None
    assert classify_by_llm(b) is None
    assert cluster_bookmarks(b) is None
