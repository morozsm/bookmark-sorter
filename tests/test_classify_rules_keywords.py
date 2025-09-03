from pathlib import Path
from cbclean.utils import Bookmark
from cbclean.classify_rules import load_rules, classify_by_rules


def test_keyword_regex_and_invalid_regex(tmp_path: Path):
    rules_path = tmp_path / "rules.yaml"
    rules_path.write_text(
        """
keywords:
  "python|docker": [Dev]
  "[invalid": [Bad]
        """,
        encoding="utf-8",
    )
    rules = load_rules(rules_path)
    bms = [
        Bookmark(id="1", title="Learn Python", url="https://ex.com"),
        Bookmark(id="2", title="text", url="https://ex.com/docker"),
    ]
    classify_by_rules(bms, rules)
    assert "Dev" in bms[0].tags
    assert "Dev" in bms[1].tags
