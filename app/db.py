import sqlite3
from contextlib import contextmanager
from .settings import DATABASE_PATH

SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS channels (
  channel_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  niche TEXT,
  uploads_playlist_id TEXT,
  subscribers INTEGER,
  video_count INTEGER,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS videos (
  video_id TEXT PRIMARY KEY,
  channel_id TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  published_at TEXT,
  duration_seconds INTEGER,
  thumbnail_url TEXT,
  niche TEXT,
  FOREIGN KEY(channel_id) REFERENCES channels(channel_id)
);
CREATE TABLE IF NOT EXISTS snapshots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  video_id TEXT NOT NULL,
  captured_at TEXT DEFAULT CURRENT_TIMESTAMP,
  views INTEGER DEFAULT 0,
  likes INTEGER DEFAULT 0,
  comments INTEGER DEFAULT 0,
  UNIQUE(video_id, captured_at),
  FOREIGN KEY(video_id) REFERENCES videos(video_id)
);
CREATE TABLE IF NOT EXISTS scores (
  video_id TEXT PRIMARY KEY,
  scored_at TEXT DEFAULT CURRENT_TIMESTAMP,
  age_hours REAL,
  channel_median_views REAL,
  outlier_multiple REAL,
  views_per_hour REAL,
  engagement_rate REAL,
  score REAL,
  FOREIGN KEY(video_id) REFERENCES videos(video_id)
);
CREATE TABLE IF NOT EXISTS opportunities (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  source_video_id TEXT,
  niche TEXT,
  title TEXT,
  opportunity_score REAL,
  brief TEXT,
  status TEXT DEFAULT 'new'
);
CREATE TABLE IF NOT EXISTS jobs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  opportunity_id INTEGER,
  status TEXT DEFAULT 'draft',
  title TEXT,
  script_path TEXT,
  metadata_path TEXT,
  thumbnail_path TEXT,
  video_path TEXT,
  youtube_video_id TEXT,
  FOREIGN KEY(opportunity_id) REFERENCES opportunities(id)
);
CREATE TABLE IF NOT EXISTS owned_analytics (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  youtube_video_id TEXT,
  captured_at TEXT DEFAULT CURRENT_TIMESTAMP,
  views INTEGER,
  likes INTEGER,
  comments INTEGER
);
"""

@contextmanager
def connect():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DATABASE_PATH)
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    finally:
        con.close()

def init_db():
    with connect() as con:
        con.executescript(SCHEMA)
