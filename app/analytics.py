from .db import connect
from .youtube import oauth_client

def collect_owned_analytics():
    yt = oauth_client()
    with connect() as con:
        ids = [r[0] for r in con.execute("SELECT youtube_video_id FROM jobs WHERE youtube_video_id IS NOT NULL").fetchall()]
    if not ids:
        print("No uploaded videos to measure")
        return
    captured = 0
    for i in range(0, len(ids), 50):
        resp = yt.videos().list(part="statistics", id=",".join(ids[i:i+50])).execute()
        with connect() as con:
            for item in resp.get("items", []):
                st = item.get("statistics", {})
                con.execute("INSERT INTO owned_analytics(youtube_video_id,views,likes,comments) VALUES(?,?,?,?)",
                  (item["id"], int(st.get("viewCount",0)), int(st.get("likeCount",0)), int(st.get("commentCount",0))))
                captured += 1
    print(f"Captured analytics for {captured} owned videos")
