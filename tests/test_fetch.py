from cbclean.fetch import check_liveness
from cbclean.utils import Bookmark


def test_check_liveness_disabled_marks_unknown():
    b = [Bookmark(id="1", title="t", url="https://ex.com")]
    check_liveness(b, enabled=False)
    assert b[0].liveness == "unknown"


def test_check_liveness_enabled_marks_unchecked():
    b = [Bookmark(id="1", title="t", url="https://ex.com")]
    check_liveness(b, enabled=True)
    assert b[0].liveness == "unchecked"
