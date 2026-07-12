"""Standardized telemetry DTOs for the system-monitor capability — the data nouns a monitor tool capability emits (host CPU/RAM + aggregated GPU stats, and per-process GPU usage) and the substrate scheduler consumes for resource-derived admission + GPU subtree attribution.

The monitor is the one migrated capability with NO task adapter — live
telemetry has no cacheable, content-addressable result — so it is consumed
through the substrate NATIVE-DISPATCH channel (see MonitorToolProtocol), not
the task channel. Wire registration here is FORWARD-CONSISTENCY, not an active
path: the live transport returns raw to_dict() via bespoke endpoints; the
@wire_type registration keeps every cjm-capability-primitives noun uniformly
wire-serializable for a future unification onto the typed wire layer."""

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Protocol, runtime_checkable

from cjm_substrate.core.wire import wire_type


@wire_type("monitoring.system_stats")
@dataclass
class SystemStats:
    """Standardized snapshot of host + GPU resources (the scheduler's admission input)."""
    # CPU
    cpu_percent: float = 0.0           # Overall CPU utilization percentage
    # Memory (RAM admission checks)
    memory_used_mb: float = 0.0        # Currently used system RAM in MB
    memory_total_mb: float = 0.0       # Total system RAM in MB
    memory_available_mb: float = 0.0   # Available system RAM in MB
    # GPU (VRAM admission checks; aggregated across all visible devices)
    gpu_type: str = "None"             # GPU vendor: 'NVIDIA', 'AMD', 'Intel', 'None'
    gpu_free_memory_mb: float = 0.0    # Free GPU memory in MB
    gpu_total_memory_mb: float = 0.0   # Total GPU memory in MB
    gpu_used_memory_mb: float = 0.0    # Used GPU memory in MB
    gpu_load_percent: float = 0.0      # GPU compute utilization percentage

    def to_dict(self) -> Dict[str, Any]:  # Serialized representation
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@wire_type("monitoring.process_stats")
@dataclass
class ProcessStats:
    """Per-process GPU usage, reported by a monitor's `list_processes` (GPU subtree attribution)."""
    pid: int = 0                # OS process ID
    gpu_index: int = -1         # GPU index (0-based); -1 if not GPU-bound or unknown
    gpu_memory_mb: float = 0.0  # GPU memory attributable to this process, in MB
    command: str = ""           # Process command line (or short name)

    def to_dict(self) -> Dict[str, Any]:  # Serialized representation
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@runtime_checkable
class MonitorToolProtocol(Protocol):
    """The native surface a system-monitor tool capability exposes.

    The substrate consumes a monitor through this surface by NAME (duck-typed,
    host-no-imports per CR-1) — `get_system_status` feeds resource-derived
    admission; `list_processes` feeds per-worker GPU subtree attribution. There
    is no task adapter: this is the native-dispatch contract, and the manifest's
    `structural_surface` is what a future auto-detect could match against. Platform
    monitors (NVIDIA today; Intel / AMD / Apple Silicon later) each implement it.
    """
    def get_system_status(self) -> SystemStats: ...      # Current host + aggregated GPU telemetry
    def list_processes(self) -> List[ProcessStats]: ...  # Per-process GPU usage ([] if no per-process visibility)
