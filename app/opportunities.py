import json
from .db import connect
from .ai import ollama_json
from . import settings

def generate_opportunities():
    with connect() as con:
        rows = con.execute("""SELECT v.video_id,v.title,v.niche,c.name channel_name,s.score,s.outlier_multiple,s.views_per_hour
          FROM scores s JOIN videos v ON v.video_id=s.video_id JOIN channels c ON c.channel_id=v.channel_id
          WHERE s.score>=? ORDER BY s.score DESC LIMIT ?""", (settings.MIN_OUTLIER_SCORE, settings.MAX_DEEP_ANALYSIS_PER_RUN)).fetchall()
    if not rows:
        print("No high-scoring videos yet. Add channels, scan, then score.")
        return
    evidence = [dict(r) for r in rows]
    data = ollama_json(
      "Analyze these breakout signals. Infer patterns, then propose 5 ORIGINAL adjacent opportunities. Do not copy titles or scripts. Each opportunity needs a researchable thesis and explanation. Evidence:\n" + json.dumps(evidence, ensure_ascii=False),
      '{"opportunities":[{"source_video_id":"...","niche":"...","title":"...","opportunity_score":0,"brief":"..."}]}'
    )
    created = 0
    with connect() as con:
        for o in data.get("opportunities", []):
            con.execute("INSERT INTO opportunities(source_video_id,niche,title,opportunity_score,brief) VALUES(?,?,?,?,?)",
              (o.get("source_video_id"), o.get("niche"), o.get("title"), float(o.get("opportunity_score",0)), o.get("brief","")))
            created += 1
    print(f"Created {created} original opportunities")
