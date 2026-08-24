from datetime import datetime, timezone
from statistics import median
from .db import connect

def _iso(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))

def score_videos():
    now = datetime.now(timezone.utc)
    with connect() as con:
        rows = con.execute("""SELECT v.video_id,v.channel_id,v.published_at,
          (SELECT s.views FROM snapshots s WHERE s.video_id=v.video_id ORDER BY s.id DESC LIMIT 1) views,
          (SELECT s.likes FROM snapshots s WHERE s.video_id=v.video_id ORDER BY s.id DESC LIMIT 1) likes,
          (SELECT s.comments FROM snapshots s WHERE s.video_id=v.video_id ORDER BY s.id DESC LIMIT 1) comments
          FROM videos v WHERE v.published_at IS NOT NULL""").fetchall()
        by_channel = {}
        for r in rows:
            by_channel.setdefault(r["channel_id"], []).append(r)
        count = 0
        for channel_rows in by_channel.values():
            mature = [max(0, r["views"] or 0) for r in channel_rows if (now-_iso(r["published_at"])).total_seconds() >= 7*86400]
            baseline = median(mature) if mature else median([max(0,r["views"] or 0) for r in channel_rows]) if channel_rows else 1
            baseline = max(float(baseline), 1.0)
            for r in channel_rows:
                age_h = max((now-_iso(r["published_at"])).total_seconds()/3600, 1.0)
                views = float(r["views"] or 0)
                likes = float(r["likes"] or 0)
                comments = float(r["comments"] or 0)
                multiple = views / baseline
                velocity = views / age_h
                engagement = (likes + comments) / max(views, 1)
                # Transparent 0-100 heuristic. Tune later using owned-channel outcomes.
                outlier_component = min(multiple / 5.0, 1.0) * 50
                velocity_component = min(velocity / max(baseline/168.0, 1.0), 3.0) / 3.0 * 30
                engagement_component = min(engagement / 0.08, 1.0) * 20
                score = round(outlier_component + velocity_component + engagement_component, 2)
                con.execute("""INSERT INTO scores(video_id,scored_at,age_hours,channel_median_views,outlier_multiple,views_per_hour,engagement_rate,score)
                  VALUES(?,CURRENT_TIMESTAMP,?,?,?,?,?,?) ON CONFLICT(video_id) DO UPDATE SET
                  scored_at=CURRENT_TIMESTAMP,age_hours=excluded.age_hours,channel_median_views=excluded.channel_median_views,
                  outlier_multiple=excluded.outlier_multiple,views_per_hour=excluded.views_per_hour,engagement_rate=excluded.engagement_rate,score=excluded.score""",
                  (r["video_id"], age_h, baseline, multiple, velocity, engagement, score))
                count += 1
    print(f"Scored {count} videos")
