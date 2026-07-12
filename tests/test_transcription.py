"""Tests for cjm_capability_primitives.transcription — the transcription.result DTO.

Projected from the transcription notebook's test cells at the c25780e8 flip."""
import json

from cjm_capability_primitives.transcription import TranscriptionResult
from cjm_substrate.core.wire import WIRE_KIND_KEY, wire_decode, wire_encode


def test_transcription_result_fields():
    result = TranscriptionResult(
        text="Hello world",
        confidence=0.95,
        segments=[
            {"start": 0.0, "end": 0.5, "text": "Hello"},
            {"start": 0.5, "end": 1.0, "text": "world"},
        ],
        metadata={"model": "whisper-large-v3", "language": "en"},
    )
    assert result.text == "Hello world" and result.confidence == 0.95
    assert result.segments[1]["text"] == "world"
    assert result.metadata["language"] == "en"

    minimal = TranscriptionResult(text="Just the text")
    assert minimal.text == "Just the text"
    # segments defaults to None (fused-era field parity is load-bearing), metadata to {}
    assert minimal.confidence is None and minimal.segments is None and minimal.metadata == {}


def test_wire_round_trip():
    # The result round-trips TYPED through the simulated worker boundary
    # (encode -> json -> decode); @wire_type's flat from_dict reconstructs it.
    res = TranscriptionResult(
        text="It's one small step for man,",
        confidence=None,
        segments=[{"start": 0.0, "end": 2.5, "text": "It's one small step for man,"}],
        metadata={"model": "whisper-base", "language": "en"},
    )
    envelope = wire_encode(res)
    assert envelope[WIRE_KIND_KEY] == "transcription.result"
    back = wire_decode(json.loads(json.dumps(envelope)))
    assert isinstance(back, TranscriptionResult) and back == res
