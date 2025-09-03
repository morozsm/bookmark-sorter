from pathlib import Path
from cbclean.storage import Storage


def test_storage_initializes_table(tmp_path: Path):
    db = tmp_path / "cache.sqlite"
    with Storage(db) as st:
        # verify table exists by simple pragma
        cur = st.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='fetch_cache'"
        )
        row = cur.fetchone()
        assert row and row[0] == "fetch_cache"
