"""Standardized result DTO for the transcription task — the data noun tool capabilities emit and task adapters / workflow cores consume, wire-registered so results cross the worker boundary typed.

Relocated here from cjm-transcription-adapter-interface.core (which re-exports
it class-identically as a REMOVE-AFTER-OVERHAUL shim) and, before that, from
cjm-transcription-plugin-system. Field/key + wire-kind parity
("transcription.result") is LOAD-BEARING: existing capability databases and
fused-era plugins must keep working against this class."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from cjm_substrate.core.wire import wire_type


@wire_type("transcription.result")
@dataclass
class TranscriptionResult:
    """Standardized output for all transcription plugins."""
    text: str                                        # The transcribed text
    confidence: Optional[float] = None               # Overall confidence (0.0 to 1.0)
    segments: Optional[List[Dict[str, Any]]] = None  # Timestamped segments
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional metadata
