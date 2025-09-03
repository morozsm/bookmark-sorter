from cbclean.classify_llm import classify_by_llm
from cbclean.utils import Bookmark


class ClientDynamic:
    def __init__(self):
        self.calls = 0

    def __call__(self, model: str, prompt: str) -> str:  # noqa: ARG002
        self.calls += 1
        # Return JSON object with assignments and new_labels
        if self.calls == 1:
            return (
                '{"assignments": [{"index": 0, "labels": ["Programming/Rust"]}],'
                ' "new_labels": ["Programming/Rust", "Media/Podcasts"]}'
            )
        else:
            return (
                '{"assignments": [{"index": 0, "labels": ["Media/Podcasts", "Dev/Linux"]}],'
                ' "new_labels": ["Dev/Linux", "RU"]}'
            )


def test_llm_dynamic_labels_allowed_and_sanitized():
    items = [Bookmark(id="1", title="Rust Book", url="https://rust-lang.org", tags=[])]
    client = ClientDynamic()
    classify_by_llm(
        items,
        labels=[],  # start with empty allowed set
        only_uncertain=True,
        batch_size=1,
        allow_new_labels=True,
        max_new_labels_per_batch=5,
        client=client,
    )
    # Should include dynamically created hierarchical label and sanitized non-language labels
    assert "Programming/Rust" in items[0].tags or "Media/Podcasts" in items[0].tags


def test_llm_dynamic_labels_disallowed():
    items = [Bookmark(id="1", title="Rust Book", url="https://rust-lang.org", tags=[])]
    client = ClientDynamic()
    classify_by_llm(
        items,
        labels=["Programming/Python"],  # allowed set without Rust
        only_uncertain=True,
        batch_size=1,
        allow_new_labels=False,
        client=client,
    )
    # Without dynamic labels, nothing new should be added
    assert items[0].tags == []
