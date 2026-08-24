import argparse
import shutil
from pathlib import Path
from .db import init_db

def doctor():
    from . import settings
    print(f"Database: {settings.DATABASE_PATH}")
    print(f"YouTube API key: {'OK' if settings.YOUTUBE_API_KEY else 'MISSING'}")
    print(f"OAuth client: {'OK' if settings.GOOGLE_CLIENT_SECRET.exists() else 'MISSING'}")
    print(f"FFmpeg: {'OK' if shutil.which('ffmpeg') else 'MISSING'}")
    try:
        from .ai import healthcheck
        models = healthcheck()
        print(f"Ollama: OK ({', '.join(models) if models else 'no models pulled'})")
    except Exception as e:
        print(f"Ollama: MISSING/UNREACHABLE ({e})")

def main():
    p = argparse.ArgumentParser(description="Yoav YouTube Intelligence Agent")
    sub = p.add_subparsers(dest="cmd", required=True)
    for c in ["init-db","doctor","scan","score","opportunities","auth-youtube","analytics","pipeline"]:
        sub.add_parser(c)
    g = sub.add_parser("generate"); g.add_argument("--video-id"); g.add_argument("--opportunity-id", type=int)
    a = sub.add_parser("assemble"); a.add_argument("--job-id", type=int, required=True)
    u = sub.add_parser("upload"); u.add_argument("--job-id", type=int, required=True)
    args = p.parse_args()
    if args.cmd == "init-db": init_db(); print("Database initialized")
    elif args.cmd == "doctor": doctor()
    elif args.cmd == "scan":
        init_db(); from .youtube import scan_channels; scan_channels()
    elif args.cmd == "score":
        init_db(); from .scoring import score_videos; score_videos()
    elif args.cmd == "opportunities":
        init_db(); from .opportunities import generate_opportunities; generate_opportunities()
    elif args.cmd == "auth-youtube":
        from .youtube import oauth_credentials; oauth_credentials(); print("YouTube OAuth authorized")
    elif args.cmd == "generate":
        init_db(); from .generation import generate_job; generate_job(args.video_id,args.opportunity_id)
    elif args.cmd == "assemble":
        from .media import assemble; assemble(args.job_id)
    elif args.cmd == "upload":
        from .publishing import upload_job; upload_job(args.job_id)
    elif args.cmd == "analytics":
        from .analytics import collect_owned_analytics; collect_owned_analytics()
    elif args.cmd == "pipeline":
        init_db(); from .youtube import scan_channels; from .scoring import score_videos; from .opportunities import generate_opportunities
        scan_channels(); score_videos(); generate_opportunities()

if __name__ == "__main__": main()
