import json
import shutil
import subprocess
from pathlib import Path
from .db import connect

ROOT = Path(__file__).resolve().parents[1]

def assemble(job_id):
    with connect() as con:
        job = con.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
    if not job:
        raise RuntimeError("Job not found")
    job_dir = ROOT / "output" / f"job-{job_id}"
    narration = job_dir / "narration.wav"
    visual = job_dir / "visual.mp4"
    if not narration.exists() or not visual.exists():
        raise RuntimeError(f"Assembly expects {narration.name} and {visual.name} in {job_dir}. Generate/provide them first. See docs/MAC_SETUP.md.")
    final = job_dir / "final.mp4"
    cmd = ["ffmpeg","-y","-i",str(visual),"-i",str(narration),"-c:v","libx264","-c:a","aac","-shortest","-movflags","+faststart",str(final)]
    subprocess.run(cmd, check=True)
    with connect() as con:
        con.execute("UPDATE jobs SET video_path=?,status='assembled' WHERE id=?", (str(final), job_id))
    print(f"Assembled {final}")
    return final
