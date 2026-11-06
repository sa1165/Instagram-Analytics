"""Database Storage and Aggregation Module.
Handles SQLite schema definition, table loading, analytical view creation,
and optimized SQL queries for high-performance dashboard analytics.
"""

import sqlite3
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd

DB_FILE = Path("database/instagram_analytics.db")


def get_db_connection(db_path: Path = DB_FILE) -> sqlite3.Connection:
    """Return an active connection to the SQLite database."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    return conn


def store_cleaned_data_to_db(df: pd.DataFrame, db_path: Path = DB_FILE) -> None:
    """Persist cleaned and feature-engineered records into SQLite table `instagram_posts`.
    Creates indexed analytical summary tables.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    # Prepare DataFrame for SQL insertion (convert timestamp & categoricals to string)
    df_sql = df.copy()
    if pd.api.types.is_datetime64_any_dtype(df_sql["post_datetime"]):
        df_sql["post_datetime"] = df_sql["post_datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")

    for col in df_sql.select_dtypes(include=["category"]).columns:
        df_sql[col] = df_sql[col].astype(str)

    # 1. Store main posts table
    df_sql.to_sql("instagram_posts", conn, if_exists="replace", index=False)

    # 2. Create indices for fast filtering and slicing
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_account_id ON instagram_posts(account_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_media_type ON instagram_posts(media_type);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON instagram_posts(content_category);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_traffic ON instagram_posts(traffic_source);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_post_date ON instagram_posts(post_date);")

    # 3. Create Analytical Aggregation Table: Account Performance Summary
    cursor.execute("DROP TABLE IF EXISTS account_summary;")
    cursor.execute("""
        CREATE TABLE account_summary AS
        SELECT 
            account_id,
            account_type,
            MAX(follower_count) AS follower_count,
            COUNT(post_id) AS total_posts,
            SUM(likes) AS total_likes,
            SUM(comments) AS total_comments,
            SUM(shares) AS total_shares,
            SUM(saves) AS total_saves,
            SUM(total_interactions) AS total_interactions,
            SUM(reach) AS total_reach,
            SUM(impressions) AS total_impressions,
            SUM(followers_gained) AS total_followers_gained,
            ROUND(AVG(calculated_engagement_rate), 4) AS avg_engagement_rate_reach,
            ROUND(AVG(engagement_rate), 4) AS avg_engagement_rate_imp
        FROM instagram_posts
        GROUP BY account_id, account_type;
    """)

    # 4. Create Analytical Aggregation Table: Category & Media Performance
    cursor.execute("DROP TABLE IF EXISTS category_media_summary;")
    cursor.execute("""
        CREATE TABLE category_media_summary AS
        SELECT 
            content_category,
            media_type,
            COUNT(post_id) AS post_count,
            ROUND(AVG(likes), 2) AS avg_likes,
            ROUND(AVG(comments), 2) AS avg_comments,
            ROUND(AVG(shares), 2) AS avg_shares,
            ROUND(AVG(saves), 2) AS avg_saves,
            ROUND(AVG(reach), 2) AS avg_reach,
            ROUND(AVG(impressions), 2) AS avg_impressions,
            ROUND(AVG(calculated_engagement_rate), 4) AS avg_engagement_rate
        FROM instagram_posts
        GROUP BY content_category, media_type;
    """)

    # 5. Create Analytical Aggregation Table: Day and Hour Heatmap Summary
    cursor.execute("DROP TABLE IF EXISTS temporal_engagement_summary;")
    cursor.execute("""
        CREATE TABLE temporal_engagement_summary AS
        SELECT 
            day_of_week,
            posting_hour,
            COUNT(post_id) AS post_count,
            ROUND(AVG(total_interactions), 2) AS avg_interactions,
            ROUND(AVG(calculated_engagement_rate), 4) AS avg_engagement_rate,
            ROUND(AVG(reach), 2) AS avg_reach
        FROM instagram_posts
        GROUP BY day_of_week, posting_hour;
    """)

    conn.commit()
    conn.close()
    print(f"Database successfully updated at {db_path} with indices and analytical summary tables.")


def load_from_db(query: str = "SELECT * FROM instagram_posts", db_path: Path = DB_FILE) -> pd.DataFrame:
    """Execute SQL query and return DataFrame."""
    conn = get_db_connection(db_path)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


if __name__ == "__main__":
    from ingestion import load_raw_dataset
    from cleaning import clean_instagram_data
    from transformation import engineer_features

    raw = load_raw_dataset()
    clean, _ = clean_instagram_data(raw)
    feat = engineer_features(clean)
    store_cleaned_data_to_db(feat)

