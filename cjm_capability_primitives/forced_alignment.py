"""Standardized word-level forced-alignment DTOs — the data noun forced-alignment tool capabilities emit and task adapters / workflow cores consume, wire-registered so results cross the worker boundary typed.

Relocated here from cjm-forced-alignment-adapter-interface.core (itself
relocated from cjm-transcription-plugin-system at stage 2); the old homes
re-export class-identically (REMOVE-AFTER-OVERHAUL) until the cascade retires
them. NOTE: forced-alignment models typically strip punctuation from the input
text — the CONSUMING service maps stripped words back to the original
punctuated text."""

from dataclasses import dataclass, field
from typing import Any, Dict, List

from cjm_substrate.core.wire import wire_type


@dataclass
class ForcedAlignItem:
    """A single word-level alignment result."""
    text: str        # The aligned word (punctuation typically stripped by model)
    start_time: float  # Start time in seconds
    end_time: float    # End time in seconds


@wire_type("forced_alignment.result")
@dataclass
class ForcedAlignResult:
    """Standardized output for all forced alignment capabilities."""
    items: List[ForcedAlignItem]                          # Word-level alignments
    metadata: Dict[str, Any] = field(default_factory=dict)  # Capability-specific metadata

    @classmethod
    def from_dict(
        cls,
        d: Dict[str, Any],  # Wire payload (the substrate envelope's "data")
    ) -> "ForcedAlignResult":  # Reconstructed result with typed items
        """Reconstruct from a wire payload, re-typing nested items.

        `items` holds typed `ForcedAlignItem` objects, so the substrate's typed
        wire envelope (stage 2) reconstructs them host-side here rather than
        leaving bare dicts (which would break attribute access like `it.text`).
        """
        return cls(
            items=[it if isinstance(it, ForcedAlignItem) else ForcedAlignItem(**it)
                   for it in (d.get("items") or [])],
            metadata=d.get("metadata") or {},
        )
