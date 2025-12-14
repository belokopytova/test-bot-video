import os
import json
import psycopg2
from psycopg2.extras import execute_batch
from dotenv import load_dotenv

load_dotenv()

DSN = os.getenv('DATABASE_URL')

def load_json_to_db(json_file, dsn):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    conn = psycopg2.connect(dsn)
    cursor = conn.cursor()

    videos_data = []
    for video in data['videos']:
        videos_data.append((
            video['id'],
            video['creator_id'],
            video['video_created_at'],
            video['views_count'],
            video['likes_count'],
            video['comments_count'],
            video['reports_count'],
            video['created_at'],
            video['updated_at']
        ))

    execute_batch(cursor, """
        INSERT INTO videos (
            id, creator_id, video_created_at, views_count, likes_count,
            comments_count, reports_count, created_at, updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, videos_data)

    # Вставка снапшотов
    snapshots_data = []
    for video in data['videos']:
        for snapshot in video['snapshots']:
            snapshots_data.append((
                snapshot['id'],
                snapshot['video_id'],
                snapshot['views_count'],
                snapshot['likes_count'],
                snapshot['comments_count'],
                snapshot['reports_count'],
                snapshot['delta_views_count'],
                snapshot['delta_likes_count'],
                snapshot['delta_comments_count'],
                snapshot['delta_reports_count'],
                snapshot['created_at'],
                snapshot['updated_at']
            ))

    execute_batch(cursor, """
        INSERT INTO video_snapshots (
            id, video_id, views_count, likes_count, comments_count, reports_count,
            delta_views_count, delta_likes_count, delta_comments_count, delta_reports_count,
            created_at, updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, snapshots_data)

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    json_file = "videos.json"
    load_json_to_db(json_file, DSN)
