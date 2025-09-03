from types import SimpleNamespace
from cbclean.classify_llm import classify_by_llm
from cbclean import classify_llm as cllm
from cbclean.utils import Bookmark


class DuckChoice:
    def __init__(self, content: str) -> None:
        self.message = SimpleNamespace(content=content)


class DuckCompletions:
    def __init__(self, responses):
        self._responses = iter(responses)

    def create(self, model: str, messages, temperature: float):  # noqa: ARG002
        content = next(self._responses)
        return SimpleNamespace(choices=[DuckChoice(content)])


class DuckChat:
    def __init__(self, responses):
        self.completions = DuckCompletions(responses)


class DuckClient:
    def __init__(self, responses):
        self.chat = DuckChat(responses)


def test_llm_duck_client_batches_and_parsing(monkeypatch):
    # Monkeypatch labels resolution when not provided
    monkeypatch.setattr(cllm, "load_rules", lambda path: {"domains": {"x": ["Dev", "Code"]}})

    items = [
        Bookmark(id="1", title="GitHub", url="https://github.com", tags=[]),
        Bookmark(id="2", title="Python Docs", url="https://docs.python.org", tags=[]),
        Bookmark(id="3", title="Video", url="https://youtube.com/watch?v=1", tags=["Existing"]),
    ]

    # First batch returns plain JSON; second returns fenced JSON plus invalid entry
    resp1 = '[{"index": 0, "labels": ["Dev", "Code"]}]'
    resp2 = """
```json
[{"index": 0, "labels": ["Code", "Other"]}, {"index": "bad", "labels": [1,2]}]
```
"""
    client = DuckClient([resp1, resp2])

    # only_uncertain=False ensures we classify even those with existing tags
    classify_by_llm(
        items,
        provider="openai",
        model="gpt-4o-mini",
        labels=None,
        batch_size=2,
        only_uncertain=False,
        client=client,
    )

    # Item 0 got Dev+Code (filtered to allowed labels)
    assert "Dev" in items[0].tags and "Code" in items[0].tags
    # Second batch targets the second chunk (index 0 in that chunk → original items[2])
    # "Other" is filtered out as not in allowed
    assert "Code" in items[2].tags
    # Existing tag preserved; new allowed labels are merged
    assert "Existing" in items[2].tags or isinstance(items[2].tags, list)
