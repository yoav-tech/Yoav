#!/usr/bin/env bash
set -euo pipefail

if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew is required. Install it from https://brew.sh and rerun this script."
  exit 1
fi

brew install python git ffmpeg || true
if ! command -v ollama >/dev/null 2>&1; then
  brew install ollama
fi

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

mkdir -p data output media secrets config
[ -f config/channels.yaml ] || cp config/channels.example.yaml config/channels.yaml
[ -f config/niches.yaml ] || cp config/niches.example.yaml config/niches.yaml
[ -f .env ] || cp .env.example .env

echo "Starting Ollama service if needed..."
if ! curl -fsS http://localhost:11434/api/tags >/dev/null 2>&1; then
  nohup ollama serve > /tmp/yoav-ollama.log 2>&1 &
  sleep 3
fi

MODEL=$(grep '^OLLAMA_MODEL=' .env | cut -d= -f2- || true)
MODEL=${MODEL:-qwen3:8b}
ollama pull "$MODEL"
python -m app.cli init-db

echo
echo "Local setup complete."
echo "NEXT: edit .env, configure config/channels.yaml, add secrets/client_secret.json, then run:"
echo "source .venv/bin/activate && python -m app.cli doctor"
