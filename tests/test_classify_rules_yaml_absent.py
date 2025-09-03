from pathlib import Path
import importlib
from cbclean import classify_rules as cr
from cbclean.utils import Bookmark


def test_load_rules_without_yaml_dependency(tmp_path: Path, monkeypatch):
    # Simulate ruamel.yaml not available
    monkeypatch.setattr(cr, "YAML", None)
    rules = cr.load_rules(tmp_path / "missing.yaml")
    assert rules == {"domains": {}, "keywords": {}, "lang": {}}
    b = [Bookmark(id="1", title="t", url="https://ex.com")]
    cr.classify_by_rules(b, rules)
    assert b[0].tags == []

