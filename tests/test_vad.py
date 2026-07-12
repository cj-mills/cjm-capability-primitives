"""Tests for cjm_capability_primitives.vad — the vad.result DTO.

Projected from the vad notebook's test cells at the c25780e8 flip."""
import json

from cjm_capability_primitives.vad import TimeRange, VADResult
from cjm_substrate.core.wire import WIRE_KIND_KEY, wire_decode, wire_encode


def test_vad_result_and_minimal():
    result = VADResult(
        ranges=[
            TimeRange(start=0.0, end=2.5, label="speech", confidence=1.0),
            TimeRange(start=3.1, end=5.8, label="speech", confidence=1.0),
        ],
        metadata={"duration": 6.0, "sample_rate": 16000, "total_speech": 5.2,
                  "segment_count": 2},
    )
    assert result.ranges[0].start == 0.0 and result.ranges[1].end == 5.8

    minimal = VADResult(ranges=[])  # empty ranges = silent source
    assert minimal.ranges == [] and minimal.metadata == {}


def test_wire_round_trip_retypes_nested_ranges():
    # The custom from_dict re-types the nested TimeRanges (NOT left as bare dicts).
    res = VADResult(
        ranges=[TimeRange(start=0.0, end=2.5), TimeRange(start=3.1, end=5.8)],
        metadata={"duration": 6.0, "sample_rate": 16000},
    )
    envelope = wire_encode(res)
    assert envelope[WIRE_KIND_KEY] == "vad.result"
    back = wire_decode(json.loads(json.dumps(envelope)))
    assert isinstance(back, VADResult) and back == res
    assert all(isinstance(r, TimeRange) for r in back.ranges)
