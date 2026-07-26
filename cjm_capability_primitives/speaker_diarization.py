"""Standardized result DTO for the speaker-diarization task — the data noun diarization tool capabilities emit and task adapters / workflow cores consume, wire-registered so results cross the worker boundary typed. Turns are ANONYMOUS clusters (SPEAKER_00, ...) — mapping clusters to named identities is the correction TUI's assignment lane (human judgment), never this DTO's job (DEC 44afb2df)."""

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from cjm_substrate.core.wire import wire_type


@dataclass
class SpeakerTurn:
    """One diarized speech turn: a source-coordinate time span bound to an
    ANONYMOUS speaker cluster label (identity is downstream human judgment)."""
    start: float                       # Turn start in source coordinates (seconds)
    end: float                         # Turn end in source coordinates (seconds)
    speaker: str                       # Anonymous cluster label (e.g. "SPEAKER_00") — stable within one result, never an identity
    confidence: Optional[float] = None # Optional model confidence for the turn (None when the pipeline reports none)

    def to_dict(self) -> Dict[str, Any]:  # Serialized representation
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@wire_type("speaker_diarization.result")
@dataclass
class SpeakerDiarizationResult:
    """Standardized output for speaker-diarization capabilities.

    `turns` are time-ordered speech turns over the ORIGINAL audio's
    coordinates; overlapping speech may yield overlapping turns (that is
    signal, not an error). Cluster labels are result-scoped: the same
    physical speaker gets one label WITHIN a result, but labels carry no
    meaning across results — cross-result identity is the assignment lane's
    cluster-name-once verdict (DEC 8a4df244)."""
    turns: List[SpeakerTurn]                                # Time-ordered anonymous speech turns
    metadata: Dict[str, Any] = field(default_factory=dict)  # Pipeline stats (speaker_count, model_id, ...)

    @classmethod
    def from_dict(
        cls,
        d: Dict[str, Any],  # Wire payload (the substrate envelope's "data")
    ) -> "SpeakerDiarizationResult":  # Reconstructed result with typed turns
        """Reconstruct from a wire payload, re-typing nested SpeakerTurns.

        `turns` holds typed `SpeakerTurn` objects, so the substrate's typed
        wire envelope reconstructs them host-side here rather than leaving
        bare dicts (which would break attribute access like `t.start`)."""
        return cls(
            turns=[t if isinstance(t, SpeakerTurn) else SpeakerTurn(**t)
                   for t in (d.get("turns") or [])],
            metadata=d.get("metadata") or {},
        )
