"""Data Quality Assessment Module.
Performs programmatic auditing for missing values, duplicates, out-of-range values,
logical relationships, timestamp integrity, and IQR outlier bounds.
"""

import json
from pathlib import Path
from typing import Dict, Any
import numpy as np
import pandas as pd


def assess_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
    """Run comprehensive quality and sanity checks across all records.
    Returns structured audit report dict.
    """
    total_records = len(df)

    # 1. Null / Missing Checks
    missing_by_column = {col: int(count) for col, count in df.isnull().sum().items()}
    total_missing_values = int(sum(missing_by_column.values()))

    # 2. Duplicate Checks
    duplicate_rows = int(df.duplicated().sum())
    duplicate_post_ids = int(df["post_id"].duplicated().sum()) if "post_id" in df.columns else 0

    # 3. Numeric Integrity Checks (Negative Values)
    numeric_columns = [
        "follower_count", "likes", "comments", "shares", "saves",
        "reach", "impressions", "engagement_rate", "followers_gained",
        "caption_length", "hashtags_count"
    ]
    negative_values = {}
    for col in numeric_columns:
        if col in df.columns:
            negative_values[col] = int((df[col] < 0).sum())

    # 4. Logical Consistency Checks
    logical_issues = {}

    # Impressions vs Reach
    if "impressions" in df.columns and "reach" in df.columns:
        logical_issues["impressions_less_than_reach"] = int((df["impressions"] < df["reach"]).sum())

    # CTA Binary Validation
    if "has_call_to_action" in df.columns:
        invalid_cta = int((~df["has_call_to_action"].isin([0, 1])).sum())
        logical_issues["invalid_cta_binary"] = invalid_cta

    # Datetime and Derived Date/Hour/Weekday Match
    if "post_datetime" in df.columns:
        parsed_dt = pd.to_datetime(df["post_datetime"], errors="coerce")
        invalid_timestamps = int(parsed_dt.isnull().sum())
        logical_issues["invalid_timestamps"] = invalid_timestamps

        if "post_date" in df.columns:
            mismatched_dates = int((parsed_dt.dt.strftime("%Y-%m-%d") != df["post_date"]).sum())
            logical_issues["date_column_mismatch"] = mismatched_dates

        if "post_hour" in df.columns:
            mismatched_hours = int((parsed_dt.dt.hour != df["post_hour"]).sum())
            logical_issues["hour_column_mismatch"] = mismatched_hours

        if "day_of_week" in df.columns:
            mismatched_weekdays = int((parsed_dt.dt.day_name() != df["day_of_week"]).sum())
            logical_issues["weekday_column_mismatch"] = mismatched_weekdays

    # 5. Outlier Detection using IQR Method
    outliers_iqr = {}
    for col in numeric_columns:
        if col in df.columns:
            q1 = float(df[col].quantile(0.25))
            q3 = float(df[col].quantile(0.75))
            iqr = q3 - q1
            lower_bound = q1 - (1.5 * iqr)
            upper_bound = q3 + (1.5 * iqr)
            outlier_count = int(((df[col] < lower_bound) | (df[col] > upper_bound)).sum())
            outliers_iqr[col] = {
                "q1": q1,
                "q3": q3,
                "iqr": iqr,
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
                "outlier_count": outlier_count,
                "outlier_percentage": round((outlier_count / total_records) * 100, 2),
            }

    # 6. Categorical Value Validation
    valid_categories = {
        "account_type": ["creator", "brand"],
        "media_type": ["image", "carousel", "reel"],
        "performance_bucket_label": ["low", "medium", "high", "viral"]
    }
    invalid_categorical = {}
    for col, valid_vals in valid_categories.items():
        if col in df.columns:
            invalid_categorical[col] = int((~df[col].isin(valid_vals)).sum())

    report = {
        "dataset_total_rows": total_records,
        "total_missing_values": total_missing_values,
        "missing_by_column": missing_by_column,
        "duplicate_rows": duplicate_rows,
        "duplicate_post_ids": duplicate_post_ids,
        "negative_values": negative_values,
        "logical_issues": logical_issues,
        "invalid_categorical": invalid_categorical,
        "outliers_iqr": outliers_iqr,
        "status": "PASSED" if (total_missing_values == 0 and duplicate_rows == 0 and sum(negative_values.values()) == 0) else "WARNINGS_FOUND"
    }

    return report


def save_quality_report(report: Dict[str, Any], filepath: str | Path = "reports/data_quality_report.json") -> None:
    """Save quality audit report to disk in JSON format."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)
    print(f"Data quality report written to {path}")


if __name__ == "__main__":
    from ingestion import load_raw_dataset
    raw_df = load_raw_dataset()
    quality_report = assess_data_quality(raw_df)
    save_quality_report(quality_report)
    print("Quality Assessment Summary:")
    print(f"Status: {quality_report['status']}")
    print(f"Total Missing: {quality_report['total_missing_values']}")
    print(f"Duplicate Rows: {quality_report['duplicate_rows']}")
    print(f"Logical Issues: {quality_report['logical_issues']}")
