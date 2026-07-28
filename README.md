# cjm-capability-primitives

<!-- generated from the context graph by `cjm-context-graph readme` — do not edit by hand; edit the graph (the urge to hand-edit = move it on-graph) -->

The dep-light primitives library for the cjm capability ecosystem — the shared cross-task result DTOs (data nouns) that tool capabilities emit and task adapters, workflow cores, and the composition layer all consume.

## Modules

- **`cjm_capability_primitives.forced_alignment`** — Standardized word-level forced-alignment DTOs — the data noun forced-alignment tool capabilities emit and task adapters / workflow cores consume, wire-registered so results cross the worker boundary typed.
- **`cjm_capability_primitives.media_processing`** — Standardized result DTOs for the media-processing task — the data nouns media-processing tool capabilities (ffmpeg today) emit and the multi-method task adapter / workflow cores consume, wire-registered so results cross the worker boundary typed.
- **`cjm_capability_primitives.monitoring`** — Standardized telemetry DTOs for the system-monitor capability — the data nouns a monitor tool capability emits (host CPU/RAM + aggregated GPU stats, and per-process GPU usage) and the substrate scheduler consumes for resource-derived admission + GPU subtree attribution.
- **`cjm_capability_primitives.sentence_segmentation`** — Standardized result DTO for the sentence-segmentation task — the data noun sentence-segmentation tool capabilities emit and task adapters / workflow cores consume, wire-registered so results cross the worker boundary typed.
- **`cjm_capability_primitives.source_separation`** — Standardized result DTO for the source-separation (audio-preprocessing) task — the data noun source-separation tool capabilities emit and task adapters / workflow cores consume, wire-registered so results cross the worker boundary typed.
- **`cjm_capability_primitives.speaker_diarization`** — Standardized result DTO for the speaker-diarization task — the data noun diarization tool capabilities emit and task adapters / workflow cores consume, wire-registered so results cross the worker boundary typed. Turns are ANONYMOUS clusters (SPEAKER_00, ...) — mapping clusters to named identities is the correction TUI's assignment lane (human judgment), never this DTO's job (DEC 44afb2df).
- **`cjm_capability_primitives.transcription`** — Standardized result DTO for the transcription task — the data noun tool capabilities emit and task adapters / workflow cores consume, wire-registered so results cross the worker boundary typed.
- **`cjm_capability_primitives.vad`** — Standardized result DTO for the voice-activity-detection task — the data noun VAD tool capabilities emit and task adapters / workflow cores consume, wire-registered so results cross the worker boundary typed.

## API

### `cjm_capability_primitives.forced_alignment`

- `ForcedAlignItem` _class_ — A single word-level alignment result.
- `ForcedAlignResult` _class_ — Standardized output for all forced alignment capabilities.

### `cjm_capability_primitives.media_processing`

- `MediaArtifactResult` _class_ — A single produced audio artifact (the `convert` / `extract_audio` output).
- `MediaMetadata` _class_ — Probed metadata for a media file (the `get_info` result) — inline data, no artifact.
- `MediaSegment` _class_ — One produced segment file from a `segment_audio` batch cut.
- `MediaSegmentationResult` _class_ — A BATCH of produced segment files (the `segment_audio` output).

### `cjm_capability_primitives.monitoring`

- `MonitorToolProtocol` _class_ — The native surface a system-monitor tool capability exposes.
- `ProcessStats` _class_ — Per-process GPU usage, reported by a monitor's `list_processes` (GPU subtree attribution).
- `SystemStats` _class_ — Standardized snapshot of host + GPU resources (the scheduler's admission input).

### `cjm_capability_primitives.sentence_segmentation`

- `SentenceSegmentationResult` _class_ — Standardized output for sentence-segmentation capabilities.
- `SentenceSpan` _class_ — One sentence's character span over the ORIGINAL (punctuated) text —

### `cjm_capability_primitives.source_separation`

- `SourceSeparationResult` _class_ — Standardized output for source-separation (audio-preprocessing) capabilities.

### `cjm_capability_primitives.speaker_diarization`

- `SpeakerDiarizationResult` _class_ — Standardized output for speaker-diarization capabilities.
- `SpeakerTurn` _class_ — One diarized speech turn: a source-coordinate time span bound to an
- `load_turns_artifact` _function_ — Load a source's turns artifact; `None` = no diarization predictions yet.
- `turns_artifact_path` _function_ — Source-keyed artifact path: `<root>/diarization/<algo>-<hexdigest>.json`.
- `write_turns_artifact` _function_ — Persist the source-keyed turns artifact (latest-wins per source).

### `cjm_capability_primitives.transcription`

- `TranscriptionResult` _class_ — Standardized output for all transcription plugins.

### `cjm_capability_primitives.vad`

- `TimeRange` _class_ — A temporal segment within an audio source (the VAD speech/silence span).
- `VADResult` _class_ — Standardized output for voice-activity-detection capabilities.

## Dependencies

**Depends on:** `cjm-substrate`
**Used by:** `cjm-capability-demucs`, `cjm-capability-ffmpeg`, `cjm-capability-monitor-nvidia`, `cjm-capability-pyannote`, `cjm-capability-pysbd`, `cjm-capability-qwen3-forced-aligner`, `cjm-capability-silero-vad`, `cjm-capability-voxtral-hf`, `cjm-capability-whisper`, `cjm-sentence-segmentation-adapter-interface`, `cjm-speaker-diarization-adapter-interface`, `cjm-transcript-correction-tui`, `cjm-transcript-decomp-core`, `cjm-transcription-adapter-interface`, `cjm-transcription-core`
