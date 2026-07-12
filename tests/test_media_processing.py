"""Tests for cjm_capability_primitives.media_processing — the multi-method task family's DTOs.

Projected from the media_processing notebook's test cells at the c25780e8 flip."""
import json

from cjm_capability_primitives.media_processing import (MediaArtifactResult, MediaMetadata,
                                                        MediaSegment, MediaSegmentationResult)
from cjm_substrate.core.wire import WIRE_KIND_KEY, wire_decode, wire_encode


def test_media_artifact_result():
    result = MediaArtifactResult(
        output_path="/data/cjm-media-plugin-ffmpeg/convert/ab12cd_0f1e2d3c4b5a/episode.wav",
        metadata={"output_format": "wav", "sample_rate": 16000, "channels": 1,
                  "resampler": "soxr", "duration": 300.0},
    )
    assert result.output_path.endswith("episode.wav")
    assert result.metadata["sample_rate"] == 16000

    minimal = MediaArtifactResult(output_path="/tmp/out.wav")
    assert minimal.output_path == "/tmp/out.wav" and minimal.metadata == {}


def test_media_segmentation_result_and_metadata():
    seg_result = MediaSegmentationResult(
        segments=[
            MediaSegment(index=0, output_path="/tmp/seg/segment_000.wav", start=0.0, end=2.5, duration=2.5),
            MediaSegment(index=1, output_path="/tmp/seg/segment_001.wav", start=2.5, end=6.0, duration=3.5),
        ],
        input_path="/data/episode.mp3", segment_count=2, total_duration=6.0, batch_key="batch-abc",
    )
    assert seg_result.segments[0].index == 0
    assert seg_result.segments[1].output_path.endswith("segment_001.wav")
    assert seg_result.segment_count == 2 and seg_result.batch_key == "batch-abc"

    empty = MediaSegmentationResult(segments=[])
    assert empty.segments == [] and empty.segment_count == 0 and empty.batch_key == ""

    meta = MediaMetadata(path="/data/episode.mp3", duration=300.0, format="mp3",
                         size_bytes=4_800_000,
                         audio_streams=[{"codec": "mp3", "sample_rate": 44100, "channels": 2}])
    assert meta.duration == 300.0 and meta.format == "mp3"
    assert meta.audio_streams[0]["channels"] == 2 and meta.video_streams == []


def test_wire_round_trips():
    # media_processing.artifact — flat fields, default reconstruction
    art = MediaArtifactResult(output_path="/data/convert/out.wav",
                              metadata={"output_format": "wav", "sample_rate": 16000})
    env = wire_encode(art)
    assert env[WIRE_KIND_KEY] == "media_processing.artifact"
    back = wire_decode(json.loads(json.dumps(env)))
    assert isinstance(back, MediaArtifactResult) and back == art

    # media_processing.segmentation — nested MediaSegments must come back TYPED
    seg = MediaSegmentationResult(
        segments=[MediaSegment(index=0, output_path="/tmp/s0.wav", start=0.0, end=2.5, duration=2.5)],
        input_path="/data/episode.mp3", segment_count=1, total_duration=2.5, batch_key="b1",
    )
    env2 = wire_encode(seg)
    assert env2[WIRE_KIND_KEY] == "media_processing.segmentation"
    back2 = wire_decode(json.loads(json.dumps(env2)))
    assert isinstance(back2, MediaSegmentationResult) and back2 == seg
    assert all(isinstance(s, MediaSegment) for s in back2.segments)

    # media_processing.metadata — flat, default reconstruction
    meta = MediaMetadata(path="/data/episode.mp3", duration=300.0, format="mp3",
                         size_bytes=4_800_000)
    env3 = wire_encode(meta)
    assert env3[WIRE_KIND_KEY] == "media_processing.metadata"
    back3 = wire_decode(json.loads(json.dumps(env3)))
    assert isinstance(back3, MediaMetadata) and back3 == meta
