import json
import re
from datetime import datetime, timezone
from pathlib import Path
import yaml
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from . import settings
from .db import connect

SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.readonly"]

def public_client():
    if not settings.YOUTUBE_API_KEY:
        raise RuntimeError("YOUTUBE_API_KEY is missing from .env")
    return build("youtube", "v3", developerKey=settings.YOUTUBE_API_KEY)

def oauth_credentials():
    token_path = settings.GOOGLE_TOKEN_PATH
    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    if not creds or not creds.valid:
        if not settings.GOOGLE_CLIENT_SECRET.exists():
            raise RuntimeError(f"Missing OAuth client JSON: {settings.GOOGLE_CLIENT_SECRET}")
        flow = InstalledAppFlow.from_client_secrets_file(str(settings.GOOGLE_CLIENT_SECRET), SCOPES)
        creds = flow.run_local_server(port=0)
    token_path.parent.mkdir(parents=True, exist_ok=True)
    token_path.write_text(creds.to_json())
    return creds

def oauth_client():
    return build("youtube", "v3", credentials=oauth_credentials())

def parse_duration(value):
    m = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", value or "")
    if not m:
        return 0
    h, mi, s = (int(x or 0) for x in m.groups())
    return h * 3600 + mi * 60 + s

def load_channels():
    if not settings.CHANNELS_PATH.exists():
        raise RuntimeError("Copy config/channels.example.yaml to config/channels.yaml and configure channels.")
    return yaml.safe_load(settings.CHANNELS_PATH.read_text()).get("channels", [])

def scan_channels():
    yt = public_client()
    configured = [c for c in load_channels() if c.get("enabled", True) and c.get("id")]
    for cfg in configured:
        resp = yt.channels().list(part="snippet,contentDetails,statistics", id=cfg["id"]).execute()
        if not resp.get("items"):
            print(f"Channel not found: {cfg['id']}")
            continue
        ch = resp["items"][0]
        uploads = ch["contentDetails"]["relatedPlaylists"]["uploads"]
        stats = ch.get("statistics", {})
        with connect() as con:
            con.execute("""INSERT INTO channels(channel_id,name,niche,uploads_playlist_id,subscribers,video_count,updated_at)
              VALUES(?,?,?,?,?,?,CURRENT_TIMESTAMP) ON CONFLICT(channel_id) DO UPDATE SET
              name=excluded.name,niche=excluded.niche,uploads_playlist_id=excluded.uploads_playlist_id,
              subscribers=excluded.subscribers,video_count=excluded.video_count,updated_at=CURRENT_TIMESTAMP""",
              (ch["id"], ch["snippet"]["title"], cfg.get("niche"), uploads, int(stats.get("subscriberCount",0)), int(stats.get("videoCount",0))))
        video_ids = []
        token = None
        pages = 0
        while pages < 3:
            pl = yt.playlistItems().list(part="contentDetails", playlistId=uploads, maxResults=50, pageToken=token).execute()
            video_ids.extend(x["contentDetails"]["videoId"] for x in pl.get("items", []))
            token = pl.get("nextPageToken")
            pages += 1
            if not token:
                break
        for i in range(0, len(video_ids), 50):
            vr = yt.videos().list(part="snippet,statistics,contentDetails", id=",".join(video_ids[i:i+50])).execute()
            with connect() as con:
                for v in vr.get("items", []):
                    sn, st, cd = v["snippet"], v.get("statistics", {}), v.get("contentDetails", {})
                    thumb = (sn.get("thumbnails", {}).get("maxres") or sn.get("thumbnails", {}).get("high") or {}).get("url")
                    con.execute("""INSERT INTO videos(video_id,channel_id,title,description,published_at,duration_seconds,thumbnail_url,niche)
                      VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(video_id) DO UPDATE SET title=excluded.title,description=excluded.description,thumbnail_url=excluded.thumbnail_url""",
                      (v["id"], ch["id"], sn["title"], sn.get("description",""), sn.get("publishedAt"), parse_duration(cd.get("duration")), thumb, cfg.get("niche")))
                    con.execute("INSERT INTO snapshots(video_id,views,likes,comments) VALUES(?,?,?,?)",
                      (v["id"], int(st.get("viewCount",0)), int(st.get("likeCount",0)), int(st.get("commentCount",0))))
        print(f"Scanned {ch['snippet']['title']}: {len(video_ids)} videos")

def upload_video(video_path, title, description, thumbnail_path=None, privacy=None):
    from googleapiclient.http import MediaFileUpload
    yt = oauth_client()
    privacy = privacy or settings.UPLOAD_PRIVACY_STATUS
    if privacy not in {"private", "unlisted", "public"}:
        raise ValueError("Invalid privacy status")
    req = yt.videos().insert(part="snippet,status", body={"snippet":{"title":title,"description":description,"categoryId":"24"},"status":{"privacyStatus":privacy}}, media_body=MediaFileUpload(str(video_path), chunksize=-1, resumable=True))
    response = None
    while response is None:
        _, response = req.next_chunk()
    vid = response["id"]
    if thumbnail_path and Path(thumbnail_path).exists():
        yt.thumbnails().set(videoId=vid, media_body=str(thumbnail_path)).execute()
    return vid
