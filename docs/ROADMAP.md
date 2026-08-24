# Roadmap

## Implemented foundation

- Official YouTube public metadata scanner
- SQLite history/snapshots
- Channel-relative outlier scoring
- Local Ollama opportunity discovery
- Original script/metadata/thumbnail-concept package generation
- Google OAuth flow
- Private-first YouTube uploader
- Basic owned-video feedback snapshots
- FFmpeg assembly hook
- Mac bootstrap script
- Self-hosted GitHub Actions intelligence schedule

## Local modules to validate before enabling full production

### Transcription
Use local Whisper/faster-whisper only for media/captions you are authorized to process. Do not depend on undocumented YouTube caption scraping.

### Narration
Select and install a local TTS model after testing voice quality on the target Mac. The generated job contract expects `narration.wav`.

### Thumbnail image generation
Select a local image model compatible with the Mac's memory. Use generated `thumbnail_concepts` as prompts; add typography/composition locally. Store the approved result as `thumbnail.jpg`.

### Visual generation
Prefer original/generated/public-domain/licensed assets plus motion graphics and FFmpeg over attempting fully generative 10-minute video. The job contract expects `visual.mp4`.

### Analytics upgrade
The current feedback collector captures public statistics for owned uploads. Add YouTube Analytics API queries after OAuth/project configuration if retention, impressions and traffic-source metrics are required.

## Production gates

1. Run scanner for at least 1-2 weeks to establish useful baselines.
2. Validate outlier scoring manually.
3. Generate at least 20 private content packages.
4. Add a fact/source verification stage.
5. Validate rights/licensing for every visual/audio source.
6. Keep uploads private until human QA passes reliably.
7. Only then consider scheduled/public automation.
