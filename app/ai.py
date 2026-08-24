import json
import requests
from . import settings

SYSTEM = """You are a YouTube market-intelligence strategist. Identify reusable audience patterns without copying creators. Propose original, researchable video opportunities with a distinct thesis. Favor general/adult audiences and meaningful commentary. Never rewrite a competitor transcript. Return valid JSON only."""

def ollama_json(prompt, schema_hint=""):
    full = SYSTEM + "\n\n" + prompt
    if schema_hint:
        full += "\n\nRequired JSON shape:\n" + schema_hint
    r = requests.post(f"{settings.OLLAMA_URL}/api/generate", json={"model":settings.OLLAMA_MODEL,"prompt":full,"stream":False,"format":"json"}, timeout=300)
    r.raise_for_status()
    raw = r.json().get("response", "{}")
    return json.loads(raw)

def healthcheck():
    r = requests.get(f"{settings.OLLAMA_URL}/api/tags", timeout=5)
    r.raise_for_status()
    return [m.get("name") for m in r.json().get("models", [])]
