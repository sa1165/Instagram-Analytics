"""End-to-End ETL Pipeline Orchestrator.
Extracts raw data, audits quality, cleans and transforms schema,
generates feature-rich analytical datasets, and loads into CSV, Parquet, and SQLite.
"""

import json
from pathlib import Path
from typing import Dict, Any
import pandas as pd

from src.ingestion import load_raw_dataset, get_dataset_overview
from src.data_quality import assess_data_quality, save_quality_report
from src.cleaning import clean_instagram_data, save_cleaning_audit
from src.transformation import engineer_features, investigate_engagement_rate_difference
from src.database import store_cleaned_data_to_db


def run_etl_pipeline(
    raw_path: str = "data/raw/Instagram_Analytics.csv",
    processed_csv_path: str = "data/processed/cleaned_data.csv",
    processed_parquet_path: str = "data/processed/cleaned_data.parquet",
    summary_report_path: str = "reports/analytical_summary.json"
) -> Dict[str, Any]:
    """Execute complete reproducible ETL pipeline."""
    print("=" * 60)
    print("STARTING INSTAGRAM ANALYTICS ETL PIPELINE")
    print("=" * 60)

    # 1. EXTRACT
    print("[1/5] Extracting raw data...")
    raw_df = load_raw_dataset(raw_path)
    overview = get_dataset_overview(raw_df)
    print(f"-> Extracted {overview['total_rows']} records across {overview['total_columns']} columns.")

    # 2. QUALITY ASSESSMENT
    print("[2/5] Assessing raw data quality...")
    quality_report = assess_data_quality(raw_df)
    save_quality_report(quality_report)
    print(f"-> Data Quality Status: {quality_report['status']}")

    # 3. CLEANING
    print("[3/5] Cleaning and standardizing dataset...")
    cleaned_df, cleaning_audit = clean_instagram_data(raw_df)
    save_cleaning_audit(cleaning_audit)
    print(f"-> Cleaning complete. Records retained: {cleaning_audit['final_row_count']}")

    # 4. TRANSFORMATION & FEATURE ENGINEERING
    print("[4/5] Engineering analytical features & metric ratios...")
    transformed_df = engineer_features(cleaned_df)
    er_investigation = investigate_engagement_rate_difference(transformed_df)
    print("-> Features engineered successfully. Total columns:", transformed_df.shape[1])

    # 5. LOAD (CSV, PARQUET, SQLITE)
    print("[5/5] Loading transformed datasets to storage layers...")
    Path(processed_csv_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Export CSV
    transformed_df.to_csv(processed_csv_path, index=False)
    print(f"-> Saved processed CSV: {processed_csv_path}")

    # Export Parquet
    transformed_df.to_parquet(processed_parquet_path, index=False, engine="pyarrow")
    print(f"-> Saved processed Parquet: {processed_parquet_path}")

    # Load into SQLite Database
    store_cleaned_data_to_db(transformed_df)
    print("-> Persisted records and indexed summary views into SQLite database.")

    # Generate analytical summary metrics
    summary = {
        "dataset_rows": len(transformed_df),
        "total_accounts": int(transformed_df["account_id"].nunique()),
        "total_posts": len(transformed_df),
        "total_likes": int(transformed_df["likes"].sum()),
        "total_comments": int(transformed_df["comments"].sum()),
        "total_shares": int(transformed_df["shares"].sum()),
        "total_saves": int(transformed_df["saves"].sum()),
        "total_interactions": int(transformed_df["total_interactions"].sum()),
        "total_reach": int(transformed_df["reach"].sum()),
        "total_impressions": int(transformed_df["impressions"].sum()),
        "total_followers_gained": int(transformed_df["followers_gained"].sum()),
        "avg_engagement_rate_reach": float(transformed_df["calculated_engagement_rate"].mean()),
        "avg_engagement_rate_impressions": float(transformed_df["engagement_rate"].mean()),
        "media_type_distribution": transformed_df["media_type"].value_counts().to_dict(),
        "account_type_distribution": transformed_df["account_type"].value_counts().to_dict(),
        "content_category_distribution": transformed_df["content_category"].value_counts().to_dict(),
        "traffic_source_distribution": transformed_df["traffic_source"].value_counts().to_dict(),
        "engagement_rate_study": er_investigation
    }

    Path(summary_report_path).parent.mkdir(parents=True, exist_ok=True)
    with open(summary_report_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)
    print(f"-> Analytical summary saved to {summary_report_path}")

    print("=" * 60)
    print("ETL PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)
    return summary


if __name__ == "__main__":
    run_etl_pipeline()

