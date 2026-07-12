"""Tests for cjm_capability_primitives.source_separation — the source_separation.result DTO.

Projected from the source_separation notebook's test cells at the c25780e8 flip."""
import json

from cjm_capability_primitives.source_separation import SourceSeparationResult
from cjm_substrate.core.wire import WIRE_KIND_KEY, wire_decode, wire_encode


def test_source_separation_result_and_minimal():
    result = SourceSeparationResult(
        output_path="/data/cjm-media-plugin-demucs/separations/ab12cd_0f1e2d3c4b5a/vocals.wav",
        metadata={"duration": 300.0, "sample_rate": 44100, "model": "htdemucs",
                  "stems_available": ["vocals", "drums", "bass", "other"]},
    )
    assert result.output_path.endswith("vocals.wav")
    assert result.metadata["model"] == "htdemucs"

    minimal = SourceSeparationResult(output_path="/tmp/vocals.wav")
    assert minimal.output_path == "/tmp/vocals.wav" and minimal.metadata == {}


def test_wire_round_trip():
    # Flat fields (str + dict): the default reconstruction rebuilds the typed
    # object — no custom from_dict needed (cf. vad.result's nested TimeRanges).
    res = SourceSeparationResult(
        output_path="/data/sep/vocals.wav",
        metadata={"duration": 300.0, "sample_rate": 44100, "model": "htdemucs"},
    )
    envelope = wire_encode(res)
    assert envelope[WIRE_KIND_KEY] == "source_separation.result"
    back = wire_decode(json.loads(json.dumps(envelope)))
    assert isinstance(back, SourceSeparationResult) and back == res
