from cbclean.classify_llm import classify_by_llm
from cbclean.utils import Bookmark


class FakeClient:
    def __call__(self, model: str, prompt: str) -> str:  # fallback path
        # Always return two labels per item when possible
        return '[{"index": 0, "labels": ["Dev", "Code"]}, {"index": 1, "labels": ["Docs"]}]'


def test_classify_llm_with_fake_client():
    items = [
        Bookmark(id="1", title="GitHub", url="https://github.com", tags=[]),
        Bookmark(id="2", title="Python Docs", url="https://docs.python.org", tags=[]),
    ]
    classify_by_llm(
        items,
        provider="openai",
        model="gpt-4o-mini",
        labels=["Dev", "Code", "Docs"],
        batch_size=10,
        only_uncertain=True,
        client=FakeClient(),
    )
    assert "Dev" in items[0].tags and "Code" in items[0].tags
    assert "Docs" in items[1].tags


def test_classify_llm_no_client_no_sdk():
    items = [Bookmark(id="1", title="X", url="https://ex.com", tags=[])]
    # Without SDK and API key, this should be a no-op
    classify_by_llm(items, labels=["Dev"], only_uncertain=True)
    assert items[0].tags == []
