"""Tests for cjm_capability_primitives.monitoring — telemetry DTOs + the native-dispatch protocol.

Projected from the monitoring notebook's test cells at the c25780e8 flip."""
import json

from cjm_capability_primitives.monitoring import (MonitorToolProtocol, ProcessStats,
                                                  SystemStats)
from cjm_substrate.core.wire import WIRE_KIND_KEY, wire_decode, wire_encode


def test_system_stats():
    s = SystemStats(cpu_percent=12.5, memory_used_mb=8000.0, memory_total_mb=32000.0,
                    memory_available_mb=24000.0, gpu_type="NVIDIA", gpu_free_memory_mb=6000.0,
                    gpu_total_memory_mb=24000.0, gpu_used_memory_mb=18000.0,
                    gpu_load_percent=42.0)
    assert s.gpu_type == "NVIDIA" and s.gpu_free_memory_mb == 6000.0
    assert s.to_dict()["cpu_percent"] == 12.5
    # Default (no-GPU) snapshot
    assert SystemStats().gpu_type == "None"


def test_process_stats():
    p = ProcessStats(pid=4242, gpu_index=0, gpu_memory_mb=1536.0, command="python -m worker")
    assert p.pid == 4242 and p.gpu_index == 0
    assert p.to_dict()["command"] == "python -m worker"
    # Empty default for monitors without per-process visibility
    assert ProcessStats().gpu_index == -1


def test_wire_round_trips_and_protocol():
    # Wire registration is forward-consistency (the live monitor transport
    # returns raw to_dict() via bespoke endpoints), verified stable here.
    s = SystemStats(cpu_percent=5.0, gpu_type="NVIDIA", gpu_free_memory_mb=1000.0)
    env_s = wire_encode(s)
    assert env_s[WIRE_KIND_KEY] == "monitoring.system_stats"
    back_s = wire_decode(json.loads(json.dumps(env_s)))
    assert isinstance(back_s, SystemStats) and back_s == s

    p = ProcessStats(pid=99, gpu_index=0, gpu_memory_mb=512.0, command="x")
    env_p = wire_encode(p)
    assert env_p[WIRE_KIND_KEY] == "monitoring.process_stats"
    back_p = wire_decode(json.loads(json.dumps(env_p)))
    assert isinstance(back_p, ProcessStats) and back_p == p

    # MonitorToolProtocol is runtime_checkable: a class with both methods satisfies it.
    class _FakeMonitor:
        def get_system_status(self):
            return SystemStats()

        def list_processes(self):
            return [ProcessStats()]

    assert isinstance(_FakeMonitor(), MonitorToolProtocol)
