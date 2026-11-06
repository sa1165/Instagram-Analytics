"""Data Cleaning Module.
Implements standardized cleaning procedures, schema harmonization,
datetime formatting, data type casting, and audit logging.
Legitimate viral/high-performing posts are strictly preserved.
"""

import json
from pathlib import Path
from typing import Tuple, Dict, Any
import pandas as pd


def clean_instagram_data(df_raw: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Clean the raw Instagram dataset without modifying the input in-place.
    Generates a structured cleaning audit.
    """
    initial_rows = len(df_raw)
    df = df_raw.copy()

    # 1. Standardize column names
    df.columns = [col.strip().lower() for col in df.columns]

    # 2. Duplicate Removal
    dedup_before = len(df)
    df = df.drop_duplicates()
    duplicates_removed = dedup_before - len(df)

    # 3. Post ID Uniqueness & Null Handling
    post_id_duplicates_removed = 0
    if "post_id" in df.columns:
        init_p_count = len(df)
        df = df.drop_duplicates(subset=["post_id"], keep="first")
        post_id_duplicates_removed = init_p_count - len(df)
        # Ensure post_id is formatted as string
        df["post_id"] = df["post_id"].astype(str).str.strip()

    # 4. Datetime Standardisation & Conversion
    df["post_datetime"] = pd.to_datetime(df["post_datetime"], errors="coerce")
    # Drop records with invalid timestamps if any
    valid_dt_count = len(df)
    df = df.dropna(subset=["post_datetime"])
    invalid_dates_dropped = valid_dt_count - len(df)

    # Harmonize post_date, post_hour, day_of_week directly from canonical datetime
    df["post_date"] = df["post_datetime"].dt.strftime("%Y-%m-%d")
    df["post_hour"] = df["post_datetime"].dt.hour.astype(int)
    df["day_of_week"] = df["post_datetime"].dt.day_name()

    # 5. Type Conversions & Safe Casting
    integer_cols = [
        "account_id", "follower_count", "has_call_to_action", "post_hour",
        "likes", "comments", "shares", "saves", "reach", "impressions",
        "followers_gained", "caption_length", "hashtags_count"
    ]
    for col in integer_cols:
        if col in df.columns:
            # Fill na with 0 before casting if any
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype("int64")

    if "engagement_rate" in df.columns:
        df["engagement_rate"] = pd.to_numeric(df["engagement_rate"], errors="coerce").astype("float64")

    string_cols = ["account_type", "media_type", "content_category", "traffic_source", "performance_bucket_label"]
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # 6. Sanity Filter on Non-negative values
    non_negative_cols = ["likes", "comments", "shares", "saves", "reach", "impressions", "follower_count"]
    invalid_negatives_adjusted = 0
    for col in non_negative_cols:
        if col in df.columns:
            neg_mask = df[col] < 0
            if neg_mask.any():
                invalid_negatives_adjusted += int(neg_mask.sum())
                df.loc[neg_mask, col] = df.loc[neg_mask, col].abs()

    # 7. Logical Consistency enforcement (Impressions >= Reach)
    # If impressions < reach due to data entry glitch, set impressions = reach
    reach_imp_violations = 0
    if "impressions" in df.columns and "reach" in df.columns:
        inconsistent_mask = df["impressions"] < df["reach"]
        reach_imp_violations = int(inconsistent_mask.sum())
        if reach_imp_violations > 0:
            df.loc[inconsistent_mask, "impressions"] = df.loc[inconsistent_mask, "reach"]

    final_rows = len(df)

    audit_report = {
        "initial_row_count": initial_rows,
        "final_row_count": final_rows,
        "records_dropped": initial_rows - final_rows,
        "duplicate_rows_removed": duplicates_removed,
        "duplicate_post_ids_removed": post_id_duplicates_removed,
        "invalid_timestamps_dropped": invalid_dates_dropped,
        "negative_values_corrected": invalid_negatives_adjusted,
        "reach_impressions_inconsistencies_rectified": reach_imp_violations,
        "cleaning_operations": [
            "Column names standardized to lowercase snake_case",
            "Duplicate check executed across entire dataset and post_id",
            "post_datetime parsed into canonical pd.Timestamp",
            "Derived post_date, post_hour, and day_of_week harmonized with post_datetime",
            "Strict integer casting applied to engagement metrics and counts",
            "Categorical strings stripped and standardized",
            "Preserved legitimate viral and high-engagement records without synthetic clipping"
        ]
    }

    return df, audit_report


def save_cleaning_audit(audit_report: Dict[str, Any], filepath: str | Path = "reports/cleaning_audit.json") -> None:
    """Save cleaning audit report to reports directory."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(audit_report, f, indent=4)
    print(f"Cleaning audit saved to {path}")


if __name__ == "__main__":
    from ingestion import load_raw_dataset
    df_raw = load_raw_dataset()
    df_cleaned, audit = clean_instagram_data(df_raw)
    save_cleaning_audit(audit)
    print(f"Cleaning complete. Retained {audit['final_row_count']} rows.")

