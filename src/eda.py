"""Exploratory Data Analysis and Statistical Computations Module.
Provides robust statistical methods, correlation analysis, hypothesis checks,
and structured aggregations across accounts, content, traffic, and temporal cohorts.
"""

from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
from scipy import stats


def calculate_kpi_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """Compute high-level Executive KPIs from filtered or unfiltered dataset."""
    total_posts = len(df)
    if total_posts == 0:
        return {
            "total_posts": 0, "total_likes": 0, "total_comments": 0,
            "total_shares": 0, "total_saves": 0, "total_interactions": 0,
            "unique_accounts": 0, "total_reach": 0, "total_impressions": 0,
            "total_followers_gained": 0, "avg_engagement_rate": 0.0,
            "avg_reach_per_post": 0.0
        }

    total_likes = int(df["likes"].sum())
    total_comments = int(df["comments"].sum())
    total_shares = int(df["shares"].sum())
    total_saves = int(df["saves"].sum())
    total_interactions = int(df["total_interactions"].sum())
    total_reach = int(df["reach"].sum())
    total_impressions = int(df["impressions"].sum())
    total_followers_gained = int(df["followers_gained"].sum())
    unique_accounts = int(df["account_id"].nunique())
    avg_er = float(df["calculated_engagement_rate"].mean())
    avg_reach = float(df["reach"].mean())

    return {
        "total_posts": total_posts,
        "total_likes": total_likes,
        "total_comments": total_comments,
        "total_shares": total_shares,
        "total_saves": total_saves,
        "total_interactions": total_interactions,
        "unique_accounts": unique_accounts,
        "total_reach": total_reach,
        "total_impressions": total_impressions,
        "total_followers_gained": total_followers_gained,
        "avg_engagement_rate": avg_er,
        "avg_reach_per_post": avg_reach
    }


def analyze_accounts(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Account-level aggregations and rankings."""
    if df.empty:
        return {}

    acc_group = df.groupby(["account_id", "account_type"]).agg(
        posts_count=("post_id", "count"),
        follower_count=("follower_count", "max"),
        total_likes=("likes", "sum"),
        total_comments=("comments", "sum"),
        total_shares=("shares", "sum"),
        total_saves=("saves", "sum"),
        total_interactions=("total_interactions", "sum"),
        total_reach=("reach", "sum"),
        total_impressions=("impressions", "sum"),
        followers_gained=("followers_gained", "sum"),
        avg_er=("calculated_engagement_rate", "mean"),
        avg_reach_per_post=("reach", "mean")
    ).reset_index()

    # Sortings
    top_by_likes = acc_group.sort_values(by="total_likes", ascending=False).head(10)
    top_by_interactions = acc_group.sort_values(by="total_interactions", ascending=False).head(10)
    top_by_posts = acc_group.sort_values(by="posts_count", ascending=False).head(10)
    top_by_growth = acc_group.sort_values(by="followers_gained", ascending=False).head(10)

    # Brand vs Creator aggregation
    brand_vs_creator = df.groupby("account_type").agg(
        accounts_count=("account_id", "nunique"),
        total_posts=("post_id", "count"),
        avg_followers=("follower_count", "mean"),
        avg_likes=("likes", "mean"),
        avg_comments=("comments", "mean"),
        avg_reach=("reach", "mean"),
        avg_er=("calculated_engagement_rate", "mean")
    ).reset_index()

    return {
        "account_summary": acc_group,
        "top_by_likes": top_by_likes,
        "top_by_interactions": top_by_interactions,
        "top_by_posts": top_by_posts,
        "top_by_growth": top_by_growth,
        "brand_vs_creator": brand_vs_creator
    }


def analyze_content(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Media types and content categories performance."""
    if df.empty:
        return {}

    media_perf = df.groupby("media_type").agg(
        post_count=("post_id", "count"),
        total_likes=("likes", "sum"),
        avg_likes=("likes", "mean"),
        avg_comments=("comments", "mean"),
        avg_shares=("shares", "mean"),
        avg_saves=("saves", "mean"),
        avg_reach=("reach", "mean"),
        avg_impressions=("impressions", "mean"),
        avg_er=("calculated_engagement_rate", "mean"),
        avg_er_imp=("engagement_rate", "mean"),
        total_followers_gained=("followers_gained", "sum")
    ).reset_index()

    category_perf = df.groupby("content_category").agg(
        post_count=("post_id", "count"),
        total_likes=("likes", "sum"),
        avg_likes=("likes", "mean"),
        avg_comments=("comments", "mean"),
        avg_shares=("shares", "mean"),
        avg_saves=("saves", "mean"),
        avg_reach=("reach", "mean"),
        avg_er=("calculated_engagement_rate", "mean")
    ).reset_index().sort_values(by="avg_er", ascending=False)

    bucket_perf = df.groupby("performance_bucket_label").agg(
        post_count=("post_id", "count"),
        avg_likes=("likes", "mean"),
        avg_comments=("comments", "mean"),
        avg_reach=("reach", "mean"),
        avg_impressions=("impressions", "mean"),
        avg_er=("calculated_engagement_rate", "mean")
    ).reset_index()

    return {
        "media_perf": media_perf,
        "category_perf": category_perf,
        "bucket_perf": bucket_perf
    }


def analyze_temporal(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Time-series monthly trends, hourly distribution, and weekday engagement heatmap."""
    if df.empty:
        return {}

    monthly_trend = df.groupby("posting_year_month").agg(
        posts_count=("post_id", "count"),
        total_likes=("likes", "sum"),
        total_reach=("reach", "sum"),
        total_interactions=("total_interactions", "sum"),
        avg_er=("calculated_engagement_rate", "mean")
    ).reset_index().sort_values(by="posting_year_month")

    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekday_perf = df.groupby("day_of_week").agg(
        post_count=("post_id", "count"),
        avg_likes=("likes", "mean"),
        avg_comments=("comments", "mean"),
        avg_reach=("reach", "mean"),
        avg_er=("calculated_engagement_rate", "mean")
    ).reindex(weekday_order).reset_index()

    hourly_perf = df.groupby("posting_hour").agg(
        post_count=("post_id", "count"),
        avg_likes=("likes", "mean"),
        avg_reach=("reach", "mean"),
        avg_er=("calculated_engagement_rate", "mean"),
        avg_interactions=("total_interactions", "mean")
    ).reset_index().sort_values(by="posting_hour")

    # Day-Hour matrix for heatmap
    heatmap_df = df.pivot_table(
        index="day_of_week",
        columns="posting_hour",
        values="calculated_engagement_rate",
        aggfunc="mean"
    ).reindex(weekday_order)

    return {
        "monthly_trend": monthly_trend,
        "weekday_perf": weekday_perf,
        "hourly_perf": hourly_perf,
        "heatmap_df": heatmap_df
    }


def analyze_traffic_and_features(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Traffic sources, Hashtags, and Call-to-Action performance."""
    if df.empty:
        return {}

    traffic_perf = df.groupby("traffic_source").agg(
        post_count=("post_id", "count"),
        total_reach=("reach", "sum"),
        avg_reach=("reach", "mean"),
        avg_likes=("likes", "mean"),
        avg_er=("calculated_engagement_rate", "mean"),
        total_interactions=("total_interactions", "sum")
    ).reset_index().sort_values(by="avg_reach", ascending=False)

    cta_perf = df.groupby("has_call_to_action").agg(
        post_count=("post_id", "count"),
        avg_likes=("likes", "mean"),
        avg_comments=("comments", "mean"),
        avg_shares=("shares", "mean"),
        avg_reach=("reach", "mean"),
        avg_followers_gained=("followers_gained", "mean"),
        avg_er=("calculated_engagement_rate", "mean")
    ).reset_index()
    cta_perf["has_call_to_action"] = cta_perf["has_call_to_action"].map({1: "With CTA", 0: "Without CTA"})

    hashtag_perf = df.groupby("hashtag_count_group", observed=False).agg(
        post_count=("post_id", "count"),
        avg_likes=("likes", "mean"),
        avg_comments=("comments", "mean"),
        avg_reach=("reach", "mean"),
        avg_er=("calculated_engagement_rate", "mean")
    ).reset_index()

    return {
        "traffic_perf": traffic_perf,
        "cta_perf": cta_perf,
        "hashtag_perf": hashtag_perf
    }


def run_statistical_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """Conduct correlation analysis, distribution diagnostics, and hypothesis tests."""
    numeric_cols = [
        "follower_count", "reach", "impressions", "likes", "comments",
        "shares", "saves", "total_interactions", "calculated_engagement_rate",
        "caption_length", "hashtags_count"
    ]
    # Filter columns that exist
    valid_cols = [c for c in numeric_cols if c in df.columns]
    corr_matrix = df[valid_cols].corr(method="pearson").round(3)

    # Key bivariate relationships
    corr_follower_er, _ = stats.pearsonr(df["follower_count"], df["calculated_engagement_rate"])
    corr_reach_imp, _ = stats.pearsonr(df["reach"], df["impressions"])
    corr_hashtag_er, _ = stats.pearsonr(df["hashtags_count"], df["calculated_engagement_rate"])
    corr_caption_er, _ = stats.pearsonr(df["caption_length"], df["calculated_engagement_rate"])

    # CTA T-Test for difference in engagement rate
    cta_with = df[df["has_call_to_action"] == 1]["calculated_engagement_rate"]
    cta_without = df[df["has_call_to_action"] == 0]["calculated_engagement_rate"]
    t_stat, p_val = stats.ttest_ind(cta_with, cta_without, equal_var=False)

    return {
        "correlation_matrix": corr_matrix,
        "corr_follower_er": float(corr_follower_er),
        "corr_reach_imp": float(corr_reach_imp),
        "corr_hashtag_er": float(corr_hashtag_er),
        "corr_caption_er": float(corr_caption_er),
        "cta_ttest": {
            "t_statistic": float(t_stat),
            "p_value": float(p_val),
            "statistically_significant": bool(p_val < 0.05)
        }
    }

