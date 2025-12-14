import os
from psycopg2 import connect
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DSN = os.getenv('DATABASE_URL')
conn = None

TEMPLATES = {
    "T1": (
        "SELECT COUNT(*) AS value FROM videos;",
        []
    ),
    "T2": (
        "SELECT COUNT(*) AS value FROM videos WHERE creator_id = %s AND video_created_at BETWEEN %s AND %s;",
        ["creator_id", "date_from", "date_to"]
    ),
    "T3_more": (
        "SELECT COUNT(*) AS value FROM videos WHERE views_count > %s;",
        ["threshold"]
    ),
    "T3_less": (
        "SELECT COUNT(*) AS value FROM videos WHERE views_count < %s;",
        ["threshold"]
    ),
    "T3_likes": (
        "SELECT COUNT(*) AS value FROM videos WHERE likes_count > %s;",
        ["threshold"]
    ),
    "T3_comments": (
        "SELECT COUNT(*) AS value FROM videos WHERE comments_count > %s;",
        ["threshold"]
    ),
    "T3_reports": (
        "SELECT COUNT(*) AS value FROM videos WHERE reports_count > %s;",
        ["threshold"]
    ),
    "T4": (
        "SELECT COALESCE(SUM(delta_views_count), 0) AS value FROM video_snapshots WHERE created_at::date = %s;",
        ["date"]
    ),
    "T4_period": (
        "SELECT COALESCE(SUM(delta_views_count), 0) AS value FROM video_snapshots WHERE created_at BETWEEN %s AND %s;",
        ["date_from", "date_to"]
    ),
    "T5": (
        "SELECT COUNT(DISTINCT video_id) AS value FROM video_snapshots WHERE created_at::date = %s AND delta_views_count > 0;",
        ["date"]
    ),
    "T5_period": (
        "SELECT COUNT(DISTINCT video_id) AS value FROM video_snapshots WHERE created_at BETWEEN %s AND %s AND delta_views_count > 0;",
        ["date_from", "date_to"]
    ),
    "T1_period": (
        "SELECT COUNT(*) AS value FROM videos WHERE video_created_at BETWEEN %s AND %s;",
        ["date_from", "date_to"]
    ),
}


def get_conn():
    global conn
    if conn is None or conn.closed:
        conn = connect(DSN)
    return conn

def create_database_structure():
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS videos (
        id TEXT PRIMARY KEY,
        creator_id TEXT NOT NULL,
        video_created_at VARCHAR,
        views_count BIGINT,
        likes_count BIGINT,
        comments_count BIGINT,
        reports_count BIGINT,
        created_at VARCHAR,
        updated_at VARCHAR
    );
    """
    )

    cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS video_snapshots (
        id TEXT PRIMARY KEY,
        video_id TEXT NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
        views_count BIGINT,
        likes_count BIGINT,
        comments_count BIGINT,
        reports_count BIGINT,
        delta_views_count BIGINT,
        delta_likes_count BIGINT,
        delta_comments_count BIGINT,
        delta_reports_count BIGINT,
        created_at VARCHAR,
        updated_at VARCHAR
    );
    """,
    )
    conn.commit()
    conn.close()
    cursor.close()


def safe_execute(template_id, params):
    if template_id not in TEMPLATES:
        raise ValueError('Бот не может ответить на такой запрос')

    sql_text, param_names = TEMPLATES[template_id]

    if len(param_names) != len(params):
        raise ValueError('несовпадение количества параметров')

    c = get_conn().cursor(cursor_factory=RealDictCursor)
    c.execute(sql_text, params)
    row = c.fetchone()
    c.close()

    return int(row['value']) if row and row['value'] is not None else 0

if __name__ == "__main__":
    create_database_structure()