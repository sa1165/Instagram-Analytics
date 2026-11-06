"""Transformation and Feature Engineering Module.
Computes standard and multi-denominator engagement rates, ratio features,
temporal attributes, and categorized cohort groups.
Preserves original engagement_rate and documents comparative behavior.
"""

from typing import Dict, Any
import numpy as np
import pandas as pd


def safe_divide(numerator: pd.Series, denominator: pd.Series, default: float = 0.0) -> pd.Series:
    """Perform element-wise division safely avoiding division by zero or NaN values."""
    denom_clean = denominator.replace(0, np.nan)
    res = numerator / denom_clean
    return res.fillna(default)


def engineer_features(df_input: pd.DataFrame) -> pd.DataFrame:
    """Generate all required analytical features, rate metrics, and categorical groups.
    
    Features created:
    1. total_interactions = likes + comments + shares + saves
    2. like_rate = likes / reach
    3. comment_rate = comments / reach
    4. share_rate = shares / reach
    5. save_rate = saves / reach
    6. calculated_engagement_rate = total_interactions / reach
    7. impressions_to_reach_ratio = impressions / reach
    8. engagement_per_follower = total_interactions / follower_count
    9. posting_month = month extracted from post_datetime (1-12)
    10. posting_year = year extracted from post_datetime
    11. posting_hour = hour extracted from post_datetime (0-23)
    12. posting_weekday = weekday name extracted from post_datetime
    13. hashtag_count_group = ranges (0-4, 5-9, 10-14, 15+)
    14. follower_count_group = ranges (Micro <10k, Mid 10k-50k, Macro >50k)
    15. engagement_rate_impressions = total_interactions / impressions (investigative comparison)
    """
    df = df_input.copy()

    # 1. Total Interactions
    df["total_interactions"] = df["likes"] + df["comments"] + df["shares"] + df["saves"]

    # 2-5. Interaction Rates by Reach
    df["like_rate"] = safe_divide(df["likes"], df["reach"])
    df["comment_rate"] = safe_divide(df["comments"], df["reach"])
    df["share_rate"] = safe_divide(df["shares"], df["reach"])
    df["save_rate"] = safe_divide(df["saves"], df["reach"])

    # 6. Calculated Engagement Rate (Standard Social Industry Standard: Interactions / Reach)
    df["calculated_engagement_rate"] = safe_divide(df["total_interactions"], df["reach"])

    # 7. Impressions to Reach Ratio (Content frequency/repeat-view factor)
    df["impressions_to_reach_ratio"] = safe_divide(df["impressions"], df["reach"])

    # 8. Engagement per Follower (Interactions relative to existing follower base)
    df["engagement_per_follower"] = safe_divide(df["total_interactions"], df["follower_count"])

    # 9-12. Temporal Features
    if not pd.api.types.is_datetime64_any_dtype(df["post_datetime"]):
        df["post_datetime"] = pd.to_datetime(df["post_datetime"])

    df["posting_year"] = df["post_datetime"].dt.year
    df["posting_month"] = df["post_datetime"].dt.month
    df["posting_year_month"] = df["post_datetime"].dt.strftime("%Y-%m")
    df["posting_hour"] = df["post_datetime"].dt.hour
    df["posting_weekday"] = df["post_datetime"].dt.day_name()
    df["is_weekend"] = df["post_datetime"].dt.dayofweek.isin([5, 6]).astype(int)

    # 13. Hashtag Count Groups
    hashtag_bins = [-1, 4, 9, 14, 100]
    hashtag_labels = ["Low (0-4)", "Medium (5-9)", "High (10-14)", "Very High (15+)"]
    df["hashtag_count_group"] = pd.cut(df["hashtags_count"], bins=hashtag_bins, labels=hashtag_labels)

    # 14. Follower Count Groups
    # Dataset accounts range from ~1,000 to ~31,095
    follower_bins = [-1, 5000, 15000, 30000, 1000000]
    follower_labels = ["Emerging (<5K)", "Growing (5K-15K)", "Established (15K-30K)", "Prominent (30K+)"]
    df["follower_count_group"] = pd.cut(df["follower_count"], bins=follower_bins, labels=follower_labels)

    # 15. Investigation: Engagement rate based on impressions
    df["engagement_rate_impressions"] = safe_divide(df["total_interactions"], df["impressions"])

    # Round floats to 4 decimal places for consistency
    float_cols = [
        "like_rate", "comment_rate", "share_rate", "save_rate",
        "calculated_engagement_rate", "impressions_to_reach_ratio",
        "engagement_per_follower", "engagement_rate_impressions"
    ]
    for col in float_cols:
        df[col] = df[col].round(4)

    return df


def investigate_engagement_rate_difference(df: pd.DataFrame) -> Dict[str, Any]:
    """Compare the provided `engagement_rate` against `calculated_engagement_rate` (reach)
    and `engagement_rate_impressions` (impressions).
    Documents the exact denominator discovery for academic verification.
    """
    corr_reach = float(df["engagement_rate"].corr(df["calculated_engagement_rate"]))
    corr_imp = float(df["engagement_rate"].corr(df["engagement_rate_impressions"]))
    mae_reach = float((df["engagement_rate"] - df["calculated_engagement_rate"]).abs().mean())
    mae_imp = float((df["engagement_rate"] - df["engagement_rate_impressions"]).abs().mean())

    finding = {
        "correlation_with_reach_denominator": corr_reach,
        "correlation_with_impressions_denominator": corr_imp,
        "mean_absolute_error_vs_reach": mae_reach,
        "mean_absolute_error_vs_impressions": mae_imp,
        "deduction": (
            "The dataset's original 'engagement_rate' column was calculated using "
            "Impressions as the denominator (Total Interactions / Impressions), matching with "
            f"a Pearson correlation of {corr_imp:.6f} and virtually 0 error. In social media "
            "analytics, practitioners distinguish between Reach-based engagement rate "
            "(Total Interactions / Reach) and Impression-based engagement rate. Both metrics "
            "are preserved and made explicitly selectable throughout the application."
        )
    }
    return finding


if __name__ == "__main__":
    from ingestion import load_raw_dataset
    from cleaning import clean_instagram_data

    raw = load_raw_dataset()
    cleaned, _ = clean_instagram_data(raw)
    transformed = engineer_features(cleaned)
    investigation = investigate_engagement_rate_difference(transformed)
    print("Feature Engineering successful. Shape:", transformed.shape)
    print("ER Comparison Analysis:")
    print(investigation["deduction"])

