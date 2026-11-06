"""Dynamic Automated Insights and Business Recommendations Generator.
Generates facts, findings, and strategic guidance directly calculated from the
active filtered slice of data without hardcoding.
"""

from typing import Dict, Any, List
import pandas as pd


def generate_dynamic_insights(df: pd.DataFrame) -> Dict[str, Any]:
    """Generate analytical takeaways based on empirical data."""
    if df.empty:
        return {"error": "No records available under the active filter combination."}

    # 1. Media Type Performance
    media_grp = df.groupby("media_type")["calculated_engagement_rate"].mean()
    best_media = media_grp.idxmax()
    best_media_val = media_grp.max() * 100

    media_reach = df.groupby("media_type")["reach"].mean()
    top_reach_media = media_reach.idxmax()
    top_reach_val = media_reach.max()

    # 2. Content Category
    cat_grp = df.groupby("content_category")["calculated_engagement_rate"].mean()
    best_cat = cat_grp.idxmax()
    best_cat_val = cat_grp.max() * 100

    cat_likes = df.groupby("content_category")["likes"].sum()
    top_likes_cat = cat_likes.idxmax()

    # 3. Top Account
    acc_grp = df.groupby("account_id")["total_interactions"].sum()
    top_acc = acc_grp.idxmax()
    top_acc_val = acc_grp.max()

    # 4. Traffic Source
    traffic_grp = df.groupby("traffic_source")["reach"].mean()
    top_traffic = traffic_grp.idxmax()
    top_traffic_reach = traffic_grp.max()

    # 5. Temporal Patterns
    day_grp = df.groupby("day_of_week")["calculated_engagement_rate"].mean()
    best_day = day_grp.idxmax()
    best_day_val = day_grp.max() * 100

    hour_grp = df.groupby("posting_hour")["calculated_engagement_rate"].mean()
    best_hour = hour_grp.idxmax()
    best_hour_val = hour_grp.max() * 100

    # 6. Creator vs Brand
    acc_type_grp = df.groupby("account_type")["calculated_engagement_rate"].mean()
    creator_er = acc_type_grp.get("creator", 0) * 100
    brand_er = acc_type_grp.get("brand", 0) * 100

    # 7. CTA Impact
    cta_grp = df.groupby("has_call_to_action")["calculated_engagement_rate"].mean()
    cta_with_er = cta_grp.get(1, 0) * 100
    cta_without_er = cta_grp.get(0, 0) * 100
    cta_diff = cta_with_er - cta_without_er

    # 8. Follower correlation
    corr_fol_er = float(df["follower_count"].corr(df["calculated_engagement_rate"]))

    insights_list = [
        {
            "category": "Media Format Optimization",
            "title": f"{best_media.capitalize()}s Lead in Engagement Rate",
            "observation": f"{best_media.capitalize()}s deliver the highest average engagement rate at {best_media_val:.2f}%. Meanwhile, {top_reach_media.capitalize()}s achieve the highest average reach ({top_reach_val:,.0f} accounts).",
            "recommendation": f"Prioritize {best_media}s for relationship-building and community interaction, while leveraging {top_reach_media}s when top-of-funnel reach is the primary KPI."
        },
        {
            "category": "Category Leadership",
            "title": f"'{best_cat}' Highest Converting Category",
            "observation": f"Posts under '{best_cat}' achieve an average engagement rate of {best_cat_val:.2f}%, while '{top_likes_cat}' amassed the highest absolute volume of likes.",
            "recommendation": f"Allocate editorial resources to test cross-genre content themes blending {best_cat} insights with top audience interests."
        },
        {
            "category": "Traffic Acquisition",
            "title": f"'{top_traffic}' Drives Peak Reach",
            "observation": f"Traffic routed through '{top_traffic}' achieves an average post reach of {top_traffic_reach:,.0f}, demonstrating high algorithmic amplification.",
            "recommendation": "Tailor post hooks and metadata specifically to trigger placement algorithms in discovery surfaces like Explore and Reels feeds."
        },
        {
            "category": "Publishing Schedule",
            "title": f"Optimal Engagement Window: {best_day}s at {best_hour}:00",
            "observation": f"Historical data indicates highest engagement efficiency on {best_day}s ({best_day_val:.2f}% ER) with peak hourly receptivity at {best_hour:02d}:00 hours ({best_hour_val:.2f}% ER).",
            "recommendation": f"Schedule tier-1 content drops during the {best_day} afternoon/evening cycle to capture maximum initial engagement velocity."
        },
        {
            "category": "Account Persona Performance",
            "title": "Creator vs Brand Efficiency",
            "observation": f"Creator profiles average {creator_er:.2f}% engagement rate compared to {brand_er:.2f}% for Brand accounts.",
            "recommendation": "Brand accounts should adopt creator-native storytelling, authentic behind-the-scenes perspectives, and person-fronted media."
        },
        {
            "category": "Call-to-Action (CTA) Strategy",
            "title": "Call-to-Action Behavioral Association",
            "observation": f"Posts containing explicit CTAs exhibit an average engagement rate of {cta_with_er:.2f}% vs {cta_without_er:.2f}% for posts without CTAs (delta: {cta_diff:+.2f}%).",
            "recommendation": "Incorporate clear, low-friction prompts (e.g. 'Save for later', 'Share with a friend') on instructional and viral content."
        }
    ]

    return {
        "summary": {
            "best_media": best_media,
            "best_category": best_cat,
            "top_account_id": int(top_acc),
            "top_traffic_source": top_traffic,
            "best_day": best_day,
            "best_hour": int(best_hour),
            "follower_er_correlation": corr_fol_er
        },
        "insights": insights_list
    }

