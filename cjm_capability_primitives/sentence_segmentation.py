"""Standardized result DTO for the sentence-segmentation task — the data noun sentence-segmentation tool capabilities emit and task adapters / workflow cores consume, wire-registered so results cross the worker boundary typed."""

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List

from cjm_substrate.core.wire import wire_type


@dataclass
class SentenceSpan:
    """One sentence's character span over the ORIGINAL (punctuated) text —
    half-open [start_char, end_char), trimmed to non-whitespace extents."""
    start_char: int  # Span start (inclusive) in the original text
    end_char: int    # Span end (exclusive) in the original text

    def to_dict(self) -> Dict[str, Any]:  # Serialized representation
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@wire_type("sentence_segmentation.result")
@dataclass
class SentenceSegmentationResult:
    """Standardized output for sentence-segmentation capabilities.

    `spans` are ordered, non-overlapping character spans over the ORIGINAL
    text the caller passed to `segment_text` — the caller's offsets stay
    valid (no cleaning/normalization is reflected here; a tool that must
    normalize internally still reports spans over the original input).
    """
    spans: List[SentenceSpan]                               # Ordered sentence spans over the original text
    metadata: Dict[str, Any] = field(default_factory=dict)  # Segmenter stats (sentence_count, language, ...)

    @classmethod
    def from_dict(
        cls,
        d: Dict[str, Any],  # Wire payload (the substrate envelope's "data")
    ) -> "SentenceSegmentationResult":  # Reconstructed result with typed spans
        """Reconstruct from a wire payload, re-typing nested SentenceSpans.

        `spans` holds typed `SentenceSpan` objects, so the substrate's typed
        wire envelope reconstructs them host-side here rather than leaving
        bare dicts (which would break attribute access like `s.start_char`).
        """
        return cls(
            spans=[s if isinstance(s, SentenceSpan) else SentenceSpan(**s)
                   for s in (d.get("spans") or [])],
            metadata=d.get("metadata") or {},
        )
