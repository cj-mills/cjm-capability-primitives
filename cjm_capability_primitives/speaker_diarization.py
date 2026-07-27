"""Standardized result DTO for the speaker-diarization task — the data noun diarization tool capabilities emit and task adapters / workflow cores consume, wire-registered so results cross the worker boundary typed. Turns are ANONYMOUS clusters (SPEAKER_00, ...) — mapping clusters to named identities is the correction TUI's assignment lane (human judgment), never this DTO's job (DEC 44afb2df)."""

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

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


# --- Source-keyed turns artifact (2026-07-26) -------------------------------
# The transcription workflow acquires turns ONCE PER SOURCE (full-source —
# per-chunk labels don't correspond across chunks) and persists them keyed by
# the source's content hash, NOT by run: existing decomposed spines inherit
# the turns with no respine, and the correction workflow's assign lane reads
# them by the same convention. This module is the ONE authority for that
# convention — writer (transcription core) and readers (correction core/TUI)
# both import it. Raw turns are re-derivable machine signal (the capability
# cache memoizes them); the durable ground truth is the assignment layer.

TURNS_DIR_NAME = "diarization"                                    # Artifact dir under the workspace root
TURNS_ARTIFACT_FORMAT = "cjm-transcription-workflow/diarization-turns"  # Format tag
TURNS_ARTIFACT_VERSION = "0.1.0"                                  # Artifact schema version


def turns_artifact_path(
    root: Union[str, Path],  # Artifact root (conventionally the WORKSPACE ROOT; diarization/ is appended)
    content_hash: str,       # Source content hash ("algo:hexdigest")
) -> Path:  # Deterministic artifact path for this source
    """Source-keyed artifact path: `<root>/diarization/<algo>-<hexdigest>.json`."""
    return Path(root) / TURNS_DIR_NAME / f"{str(content_hash).replace(':', '-')}.json"


def write_turns_artifact(
    root: Union[str, Path],       # Artifact root (see turns_artifact_path)
    *,
    source_path: str,             # Original source audio path (provenance)
    content_hash: str,            # Source content hash — the artifact KEY
    result: SpeakerDiarizationResult,  # Typed diarization result to persist
    capability: Optional[Dict[str, Any]] = None,  # Capability identity/provenance (name, version, config_hash, ...)
    rendition: Optional[Dict[str, Any]] = None,   # Decoded-PCM rendition provenance (path, sample_rate, channels)
) -> Path:  # The written artifact path
    """Persist the source-keyed turns artifact (latest-wins per source)."""
    path = turns_artifact_path(root, content_hash)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "format": TURNS_ARTIFACT_FORMAT,
        "version": TURNS_ARTIFACT_VERSION,
        "source_path": str(source_path),
        "content_hash": content_hash,
        "created_at": time.time(),
        "capability": capability or {},
        "rendition": rendition or {},
        "turns": [t.to_dict() for t in result.turns],
        "metadata": result.metadata,
    }, indent=2))
    return path


def load_turns_artifact(
    root: Union[str, Path],  # Artifact root (see turns_artifact_path)
    content_hash: str,       # Source content hash to look up
) -> Optional[Dict[str, Any]]:  # Artifact dict with a typed "result" key, or None when the source has no turns
    """Load a source's turns artifact; `None` = no diarization predictions yet.

    The returned dict is the raw artifact plus `result`: the re-typed
    `SpeakerDiarizationResult` (turns as `SpeakerTurn` objects)."""
    path = turns_artifact_path(root, content_hash)
    if not path.is_file():
        return None
    artifact = json.loads(path.read_text())
    artifact["result"] = SpeakerDiarizationResult.from_dict(artifact)
    return artifact
