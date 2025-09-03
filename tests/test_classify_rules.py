from pathlib import Path
from cbclean.utils import Bookmark
from cbclean.classify_rules import load_rules, classify_by_rules


def test_domain_rules(tmp_path: Path):
    rules_path = tmp_path / "rules.yaml"
    rules_path.write_text("domains:\n  docs.python.org: [Dev, Python]\n", encoding="utf-8")
    rules = load_rules(rules_path)
    bm = [Bookmark(id="1", title="Docs", url="https://docs.python.org/3/")]
    classify_by_rules(bm, rules)
    assert "Python" in bm[0].tags

