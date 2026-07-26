"""Tests for cjm_capability_primitives.speaker_diarization — the speaker_diarization.result DTO."""
from cjm_capability_primitives.speaker_diarization import (SpeakerDiarizationResult,
                                                           SpeakerTurn)
from cjm_substrate.core.wire import WIRE_KIND_KEY, wire_decode, wire_encode


def test_result_and_minimal():
    result = SpeakerDiarizationResult(
        turns=[SpeakerTurn(start=0.2, end=1.5, speaker="SPEAKER_00"),
               SpeakerTurn(start=1.8, end=3.9, speaker="SPEAKER_01", confidence=0.92)],
        metadata={"speaker_count": 2, "model_id": "pyannote/speaker-diarization-community-1"},
    )
    assert result.turns[0].speaker == "SPEAKER_00"
    assert result.turns[0].confidence is None            # optional — absent when unreported
    assert result.turns[1].confidence == 0.92
    assert result.metadata["speaker_count"] == 2

    minimal = SpeakerDiarizationResult(turns=[])         # silence = no turns
    assert minimal.turns == [] and minimal.metadata == {}


def test_wire_round_trip_retypes_turns():
    """The DTO crosses the worker boundary typed: encode -> decode rebuilds
    SpeakerTurn objects (attribute access, not bare dicts)."""
    result = SpeakerDiarizationResult(
        turns=[SpeakerTurn(start=4.2, end=5.7, speaker="SPEAKER_00")],
        metadata={"speaker_count": 1},
    )
    encoded = wire_encode(result)
    assert encoded[WIRE_KIND_KEY] == "speaker_diarization.result"
    decoded = wire_decode(encoded)
    assert isinstance(decoded, SpeakerDiarizationResult)
    assert isinstance(decoded.turns[0], SpeakerTurn)
    assert decoded.turns[0].end == 5.7 and decoded.turns[0].speaker == "SPEAKER_00"


def test_overlapping_turns_are_legal():
    """Overlapping speech yields overlapping turns — signal, not an error."""
    result = SpeakerDiarizationResult(
        turns=[SpeakerTurn(start=0.0, end=2.0, speaker="SPEAKER_00"),
               SpeakerTurn(start=1.5, end=3.0, speaker="SPEAKER_01")],
    )
    assert result.turns[1].start < result.turns[0].end
