"""Tests for cjm_capability_primitives.forced_alignment — word-level FA DTOs.

Projected from the forced_alignment notebook's test cells at the c25780e8 flip."""
import json
from dataclasses import asdict

from cjm_capability_primitives.forced_alignment import ForcedAlignItem, ForcedAlignResult
from cjm_substrate.core.wire import WIRE_KIND_KEY, wire_decode, wire_encode


def test_item_round_trip():
    item = ForcedAlignItem(text="November", start_time=1.04, end_time=1.6)
    assert item.text == "November" and item.start_time == 1.04 and item.end_time == 1.6
    d = asdict(item)
    assert d == {"text": "November", "start_time": 1.04, "end_time": 1.6}
    assert ForcedAlignItem(**d) == item


def test_result_and_minimal():
    items = [
        ForcedAlignItem(text="November", start_time=1.04, end_time=1.6),
        ForcedAlignItem(text="the", start_time=1.6, end_time=1.68),
        ForcedAlignItem(text="10th", start_time=1.76, end_time=2.08),
    ]
    result = ForcedAlignResult(items=items,
                               metadata={"model_id": "Qwen/Qwen3-ForcedAligner-0.6B",
                                         "language": "English"})
    assert len(result.items) == 3 and result.items[0].text == "November"
    assert result.metadata["model_id"] == "Qwen/Qwen3-ForcedAligner-0.6B"

    minimal = ForcedAlignResult(items=[])
    assert minimal.items == [] and minimal.metadata == {}


def test_wire_round_trip_retypes_nested_items():
    # The custom from_dict's whole job: items come back TYPED, not as dicts.
    res = ForcedAlignResult(
        items=[ForcedAlignItem(text="one", start_time=0.0, end_time=0.4),
               ForcedAlignItem(text="small", start_time=0.4, end_time=0.9)],
        metadata={"model": "qwen3-fa"},
    )
    envelope = wire_encode(res)
    assert envelope[WIRE_KIND_KEY] == "forced_alignment.result"
    back = wire_decode(json.loads(json.dumps(envelope)))
    assert isinstance(back, ForcedAlignResult) and back == res
    assert all(isinstance(it, ForcedAlignItem) for it in back.items)
