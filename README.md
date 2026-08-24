# Yoav YouTube Intelligence & Production Agent

Local-first YouTube research and production system designed to run on a Mac with minimal recurring software cost.

## What this repo does

1. Monitors configured competitor/reference channels using the official YouTube Data API.
2. Stores video/channel snapshots in SQLite.
3. Detects breakout videos using channel-relative outlier and velocity scoring.
4. Sends high-value patterns to a local Ollama model for niche/opportunity analysis.
5. Generates original research briefs, outlines, scripts, metadata, and thumbnail concepts.
6. Supports local narration/media assembly hooks and FFmpeg video assembly.
7. Uploads completed videos to your own YouTube channel through Google OAuth, **private by default**.
8. Stores post-publish analytics snapshots for a feedback loop.

## Safety defaults

- No credentials are committed to Git.
- Publishing defaults to `private`.
- Competitor analysis uses official public metadata APIs.
- Transcript ingestion is limited to captions/audio you are authorized to process; the project does not scrape undocumented caption endpoints.
- Generation prompts explicitly require original analysis rather than rewriting competitor scripts.
- A human approval gate is enabled before public scheduling.

## Mac quick start

```bash
./scripts/setup-mac.sh
cp .env.example .env
cp config/channels.example.yaml config/channels.yaml
cp config/niches.example.yaml config/niches.yaml
```

Then add your Google OAuth desktop client JSON at:

```text
secrets/client_secret.json
```

Initialize and test:

```bash
source .venv/bin/activate
python -m app.cli init-db
python -m app.cli doctor
python -m app.cli scan
python -m app.cli score
python -m app.cli opportunities
```

## Required one-time setup on your Mac

1. Run `./scripts/setup-mac.sh`.
2. Create a Google Cloud project and enable YouTube Data API v3.
3. Create an OAuth Desktop App credential and save its JSON as `secrets/client_secret.json`.
4. Add your YouTube API key to `.env` as `YOUTUBE_API_KEY=...` for public metadata reads.
5. Run `python -m app.cli auth-youtube` once to authorize uploads/analytics.
6. Configure competitor channels in `config/channels.yaml`.
7. Optionally register the Mac as a GitHub self-hosted runner if you want GitHub Actions to trigger local jobs.

## Core commands

```bash
python -m app.cli init-db
python -m app.cli scan
python -m app.cli score
python -m app.cli opportunities
python -m app.cli generate --video-id VIDEO_ID
python -m app.cli assemble --job-id JOB_ID
python -m app.cli upload --job-id JOB_ID
python -m app.cli analytics
python -m app.cli pipeline
```

`pipeline` runs scan -> score -> opportunity generation. It intentionally does **not** auto-publish.

## Architecture

```text
YouTube API -> SQLite -> Outlier Engine -> Ollama -> Opportunity Brief
                                                  -> Script/Metadata
                                                  -> Thumbnail Concepts
Local assets/TTS -> FFmpeg -> private YouTube upload -> analytics feedback
```

## Important monetization note

The system is built to identify patterns and create original commentary/research. Do not use it to mass-rewrite competitor transcripts or publish minimally transformed content. YouTube monetization decisions depend on originality, audience value, and policy compliance.
