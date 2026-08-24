import json
from pathlib import Path
from .db import connect
from .ai import ollama_json

ROOT = Path(__file__).resolve().parents[1]

def generate_job(video_id=None, opportunity_id=None):
    with connect() as con:
        if opportunity_id:
            opp = con.execute("SELECT * FROM opportunities WHERE id=?", (opportunity_id,)).fetchone()
        elif video_id:
            opp = con.execute("SELECT * FROM opportunities WHERE source_video_id=? ORDER BY opportunity_score DESC,id DESC LIMIT 1", (video_id,)).fetchone()
        else:
            opp = con.execute("SELECT * FROM opportunities WHERE status='new' ORDER BY opportunity_score DESC,id DESC LIMIT 1").fetchone()
    if not opp:
        raise RuntimeError("No matching opportunity. Run opportunities first.")
    result = ollama_json(
      f"""Create an ORIGINAL long-form YouTube commentary package from this opportunity. Do not invent factual claims; mark claims requiring external verification as [VERIFY]. Audience is general/adult. Target 8-12 minutes.\nTITLE IDEA: {opp['title']}\nBRIEF: {opp['brief']}\nReturn a compelling original script, metadata and 5 thumbnail concepts. Do not imitate a specific creator.""",
      '{"title":"...","description":"...","script":"...","thumbnail_concepts":[{"concept":"...","visual_prompt":"...","overlay_text":"..."}],"verification_notes":["..."]}'
    )
    out = ROOT / "output"
    out.mkdir(exist_ok=True)
    with connect() as con:
        cur = con.execute("INSERT INTO jobs(opportunity_id,status,title) VALUES(?,?,?)", (opp["id"], "generated", result.get("title", opp["title"])))
        job_id = cur.lastrowid
        con.execute("UPDATE opportunities SET status='generated' WHERE id=?", (opp["id"],))
    job_dir = out / f"job-{job_id}"
    job_dir.mkdir(parents=True, exist_ok=True)
    script_path = job_dir / "script.txt"
    metadata_path = job_dir / "metadata.json"
    script_path.write_text(result.get("script", ""))
    metadata_path.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    with connect() as con:
        con.execute("UPDATE jobs SET script_path=?,metadata_path=? WHERE id=?", (str(script_path), str(metadata_path), job_id))
    print(f"Generated job {job_id} at {job_dir}")
    return job_id
