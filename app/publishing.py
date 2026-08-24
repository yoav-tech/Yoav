import json
from pathlib import Path
from .db import connect
from .youtube import upload_video

def upload_job(job_id):
    with connect() as con:
        job = con.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
    if not job:
        raise RuntimeError("Job not found")
    if not job["video_path"] or not Path(job["video_path"]).exists():
        raise RuntimeError("Final video missing. Assemble first.")
    metadata = json.loads(Path(job["metadata_path"]).read_text())
    thumb = job["thumbnail_path"] if job["thumbnail_path"] else None
    # Safety: uploader inherits UPLOAD_PRIVACY_STATUS, whose template default is private.
    video_id = upload_video(job["video_path"], metadata.get("title",job["title"]), metadata.get("description",""), thumb)
    with connect() as con:
        con.execute("UPDATE jobs SET youtube_video_id=?,status='uploaded_private' WHERE id=?", (video_id, job_id))
    print(f"Uploaded YouTube video {video_id} (privacy controlled by UPLOAD_PRIVACY_STATUS; default private)")
    return video_id
