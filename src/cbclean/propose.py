from __future__ import annotations

from dataclasses import dataclass
from typing import List
from .utils import Bookmark


@dataclass
class PlanItem:
    action: str
    reason: str
    bookmark_id: str


def propose_changes(
    original: List[Bookmark], deduped: List[Bookmark], duplicates: List[Bookmark]
) -> List[PlanItem]:
    plan: List[PlanItem] = []
    # Duplicates: move to trash
    for b in duplicates:
        plan.append(PlanItem(action="move_to/_Trash", reason="duplicate", bookmark_id=b.id))
    # Normalization changes: indicate update
    for b in deduped:
        if b.url and b.normalized_url and b.url != b.normalized_url:
            plan.append(PlanItem(action="update_url", reason="normalized", bookmark_id=b.id))
    return plan
