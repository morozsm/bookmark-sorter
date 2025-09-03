from cbclean import classify_llm as cllm
from cbclean.classify_llm import classify_by_llm
from cbclean.utils import Bookmark


def test_llm_no_labels_rules_empty(monkeypatch):
    # No explicit labels and empty rules → no-op
    monkeypatch.setattr(cllm, "load_rules", lambda path: {})
    items = [Bookmark(id="1", title="A", url="https://a")]
    classify_by_llm(items, labels=None, only_uncertain=True)
    assert items[0].tags == []


def test_llm_provider_other_returns_none():
    items = [Bookmark(id="1", title="A", url="https://a")]
    classify_by_llm(items, provider="foo", labels=["X"], only_uncertain=False)
    assert items[0].tags == []


class ClientReturnsObject:
    def __call__(self, model: str, prompt: str) -> str:  # noqa: ARG002
        return "{}"  # not a list


def test_llm_result_not_list_is_ignored():
    items = [Bookmark(id="1", title="A", url="https://a")]
    classify_by_llm(items, labels=["Dev"], only_uncertain=False, client=ClientReturnsObject())
    assert items[0].tags == []
