"""Tests for cjm_capability_primitives.sentence_segmentation — the sentence_segmentation.result DTO."""
import json

from cjm_capability_primitives.sentence_segmentation import (SentenceSegmentationResult,
                                                             SentenceSpan)
from cjm_substrate.core.wire import WIRE_KIND_KEY, wire_decode, wire_encode


def test_result_and_minimal():
    text = "First sentence. Second one?"
    result = SentenceSegmentationResult(
        spans=[SentenceSpan(start_char=0, end_char=15),
               SentenceSpan(start_char=16, end_char=27)],
        metadata={"sentence_count": 2, "language": "en"},
    )
    assert text[result.spans[0].start_char:result.spans[0].end_char] == "First sentence."
    assert text[result.spans[1].start_char:result.spans[1].end_char] == "Second one?"

    minimal = SentenceSegmentationResult(spans=[])  # empty text = no sentences
    assert minimal.spans == [] and minimal.metadata == {}


def test_wire_round_trip_retypes_nested_spans():
    # The custom from_dict re-types the nested SentenceSpans (NOT left as bare dicts).
    res = SentenceSegmentationResult(
        spans=[SentenceSpan(start_char=0, end_char=15),
               SentenceSpan(start_char=16, end_char=27)],
        metadata={"sentence_count": 2},
    )
    envelope = wire_encode(res)
    assert envelope[WIRE_KIND_KEY] == "sentence_segmentation.result"
    back = wire_decode(json.loads(json.dumps(envelope)))
    assert isinstance(back, SentenceSegmentationResult) and back == res
    assert all(isinstance(s, SentenceSpan) for s in back.spans)
