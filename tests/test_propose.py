from cbclean.propose import propose_changes
from cbclean.utils import Bookmark


def test_propose_includes_duplicates_and_normalized_updates():
    orig = [Bookmark(id="1", title="A", url="https://ex.com/a?id=1"), Bookmark(id="2", title="A", url="https://ex.com/a?id=1")]
    # deduped keeps first, and url normalized
    kept = [Bookmark(id="1", title="A", url="https://www.ex.com/a?id=1", normalized_url="https://ex.com/a?id=1")] 
    dups = [Bookmark(id="2", title="A", url="https://ex.com/a?id=1")]
    plan = propose_changes(orig, kept, dups)
    actions = [p.action for p in plan]
    assert "move_to/_Trash" in actions
    assert "update_url" in actions
