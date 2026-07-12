"""Standardized result DTOs for the media-processing task — the data nouns media-processing tool capabilities (ffmpeg today) emit and the multi-method task adapter / workflow cores consume, wire-registered so results cross the worker boundary typed.

media_processing is a MULTI-METHOD task family (one tool, many ops), so it
carries more than one result DTO — artifact (convert/extract_audio),
segmentation (segment_audio batches, nested typed MediaSegments), and
metadata (the get_info probe)."""

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List

from cjm_substrate.core.wire import wire_type


@dataclass
class MediaSegment:
    """One produced segment file from a `segment_audio` batch cut.

    The per-segment entry the fused-era ffmpeg `segment_audio` returned as a
    dict, now a typed noun (the dead `job_id` dropped — born-final; the adapter
    owns persistence). Workflow cores read `index`/`output_path`/`start`/`end`
    to build the per-segment composition."""
    index: int        # 0-based position of this segment within the batch
    output_path: str  # Path to the produced segment file the tool wrote
    start: float      # Segment start time in the source (seconds)
    end: float        # Segment end time in the source (seconds)
    duration: float   # end - start (seconds)

    def to_dict(self) -> Dict[str, Any]:  # Serialized representation
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@wire_type("media_processing.artifact")
@dataclass
class MediaArtifactResult:
    """A single produced audio artifact (the `convert` / `extract_audio` output).

    The artifact-producing shape (cf. `SourceSeparationResult`): `output_path`
    is the file the tool wrote to the adapter-chosen location; `metadata`
    carries the stats the fused-era return dict / row held (codec, duration,
    stream_copy, the effective convert parameters, ...). Flat fields (str +
    dict), so the default wire reconstruction suffices — no custom from_dict."""
    output_path: str                                        # Path to the produced audio file
    metadata: Dict[str, Any] = field(default_factory=dict)  # Stats (codec, duration, parameters, ...)


@wire_type("media_processing.segmentation")
@dataclass
class MediaSegmentationResult:
    """A BATCH of produced segment files (the `segment_audio` output).

    Holds typed `MediaSegment`s plus the batch metadata the fused-era return
    dict carried (`input_path`, `segment_count`, `total_duration`, `batch_key`
    — the label linking the cut files in the run manifest). Because `segments`
    holds typed objects, a custom `from_dict` re-types them on wire-decode (the
    auto flat reconstruct would leave bare dicts, breaking `seg.output_path`
    access) — the `VADResult` precedent."""
    segments: List[MediaSegment]          # The produced segment files, ordered by index
    input_path: str = ""                  # The source audio that was cut
    segment_count: int = 0                # Number of segments produced
    total_duration: float = 0.0           # Sum of segment durations (seconds)
    batch_key: str = ""                   # Label linking this batch's cut files (run-manifest field)

    @classmethod
    def from_dict(
        cls,
        d: Dict[str, Any],  # Wire payload (the substrate envelope's "data")
    ) -> "MediaSegmentationResult":  # Reconstructed result with typed segments
        """Reconstruct from a wire payload, re-typing nested MediaSegments."""
        return cls(
            segments=[s if isinstance(s, MediaSegment) else MediaSegment(**s)
                      for s in (d.get("segments") or [])],
            input_path=d.get("input_path") or "",
            segment_count=int(d.get("segment_count") or 0),
            total_duration=float(d.get("total_duration") or 0.0),
            batch_key=d.get("batch_key") or "",
        )


@wire_type("media_processing.metadata")
@dataclass
class MediaMetadata:
    """Probed metadata for a media file (the `get_info` result) — inline data, no artifact.

    Relocated to `cjm-capability-primitives` from the dissolving
    `cjm-media-plugin-system.core` (the `TranscriptionResult`/`ForcedAlignResult`
    relocation precedent). `get_info` is the media-processing task's UNCACHED
    probe op, so this is a read result, not a produced-artifact pointer. The
    stream lists are plain dicts, so the default wire reconstruction suffices."""
    path: str                                                          # File path probed
    duration: float                                                    # Duration in seconds
    format: str                                                        # Container format (e.g. 'mp4', 'mkv')
    size_bytes: int                                                    # File size in bytes
    video_streams: List[Dict[str, Any]] = field(default_factory=list)  # Per-video-stream info (codec, width, height, fps)
    audio_streams: List[Dict[str, Any]] = field(default_factory=list)  # Per-audio-stream info (codec, sample_rate, channels, duration)

    def to_dict(self) -> Dict[str, Any]:  # Serialized representation
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
