# Mac launch checklist

## 1. Clone and bootstrap

```bash
git clone https://github.com/yoav-tech/Yoav.git
cd Yoav
chmod +x scripts/*.sh
./scripts/setup-mac.sh
source .venv/bin/activate
```

## 2. Google / YouTube credentials

In Google Cloud Console:

1. Create/select a project.
2. Enable **YouTube Data API v3**.
3. Create an API key for public metadata reads and put it in `.env` as `YOUTUBE_API_KEY`.
4. Configure the OAuth consent screen.
5. Create OAuth credentials of type **Desktop app**.
6. Download the client JSON and save it as `secrets/client_secret.json`.
7. Run `python -m app.cli auth-youtube` and approve access in the browser.

Never commit the API key, client secret JSON, or generated OAuth token. `.gitignore` excludes them.

## 3. Configure intelligence inputs

Edit `config/channels.yaml`. Set `enabled: true` for real channel IDs. Assign each a niche matching `config/niches.yaml`.

Start with 20-50 reference channels across several niches rather than committing to one niche immediately.

## 4. Verify

```bash
python -m app.cli doctor
python -m app.cli scan
python -m app.cli score
python -m app.cli opportunities
```

## 5. Generate a package

```bash
python -m app.cli generate
```

The generated job appears under `output/job-N/` with a script and metadata package. Factual claims marked `[VERIFY]` should be researched/verified before production.

## 6. Media production

The repo intentionally keeps media generation modular because local image/TTS/video model choices depend heavily on Mac RAM/GPU capability.

For each generated job, create/provide:

- `output/job-N/narration.wav`
- `output/job-N/visual.mp4`
- optionally `output/job-N/thumbnail.jpg`

Then run:

```bash
python -m app.cli assemble --job-id N
```

This uses FFmpeg to produce `final.mp4`.

## 7. Upload safely

Keep this in `.env` during testing:

```text
UPLOAD_PRIVACY_STATUS=private
```

Then:

```bash
python -m app.cli upload --job-id N
```

Review the result in YouTube Studio before making anything public.

## 8. Automation

The simplest reliable Mac scheduler is `launchd`. You can also register your Mac as a GitHub Actions self-hosted runner and use the included workflow. The workflow is intentionally manual/scheduled only and does not publish videos.

## 9. Before public autonomous publishing

Do not switch to public automation until you have validated at least:

- source/fact verification workflow
- narration quality
- visual rights/licensing
- thumbnail quality
- audience classification
- YouTube monetization/reused-content compliance
- failure handling
- duplicate-topic prevention
- 20+ private/test generations with acceptable QA
