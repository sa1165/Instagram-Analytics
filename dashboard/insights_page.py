"""Strategic Insights and Academic Report Outlines Page.
Presents dynamically calculated factual insights, comparative statistical deductions,
and a university submission project outline.
"""

import streamlit as st
from src.insights import generate_dynamic_insights
from src.transformation import investigate_engagement_rate_difference


def render_insights_page(df):
    st.markdown("## 🧠 Dynamic Insights & Academic Evaluation Report")
    st.markdown("Automated algorithmic conclusions synthesized from the current dataset state, along with the theoretical denominator audit and project report structure.")

    if df.empty:
        st.warning("⚠️ No records to analyze. Please adjust sidebar filter constraints.")
        return

    # Generate Dynamic Insights from active slice
    insights_data = generate_dynamic_insights(df)
    summary = insights_data.get("summary", {})
    insights_list = insights_data.get("insights", [])

    st.markdown("### 💡 Automated Findings (Calculated Dynamically)")
    for item in insights_list:
        with st.expander(f"📌 {item['category']}: {item['title']}", expanded=True):
            st.markdown(f"**Empirical Observation:** {item['observation']}")
            st.markdown(f"**Strategic Recommendation:** {item['recommendation']}")

    st.markdown("---")

    # Methodological Finding: Engagement Rate Denominator Investigation
    st.markdown("### 🔬 Methodological Denominator Verification (Stage 5 Investigation)")
    inv = investigate_engagement_rate_difference(df)
    st.info(
        f"**Discovery & Verification:**\n\n{inv['deduction']}\n\n"
        f"- **Correlation (Original ER vs Impressions-based ER):** `{inv['correlation_with_impressions_denominator']:.6f}`\n"
        f"- **Mean Absolute Error (Original ER vs Impressions-based ER):** `{inv['mean_absolute_error_vs_impressions']:.6f}`\n"
        f"- **Correlation (Original ER vs Reach-based ER):** `{inv['correlation_with_reach_denominator']:.6f}`\n\n"
        "**Conclusion for Academic Evaluation:** The original dataset's `engagement_rate` metric is strictly `(Likes + Comments + Shares + Saves) / Impressions`. In modern social media analytics, reach-based engagement is also considered the gold standard for measuring audience engagement depth without impression inflation. Both metrics are preserved and selectable."
    )

    st.markdown("---")

    # Academic Project Evaluation Report Outline
    st.markdown("### 🎓 University Academic Project Report Outline")
    st.markdown(
        """
        Below is the standardized Big Data Visualization project evaluation report structure tailored to this dataset and implementation:
        
        1. **Executive Summary**
           - Project context, dataset scope (29,999 records, 20 accounts), and primary analytical goals.
        2. **Data Engineering & ETL Lifecycle**
           - Data quality assessment: verification of missingness, duplicate analysis, negative bounds, timestamp validity.
           - Cleaning procedures: schema normalization, canonical datetime extraction, safe type casting.
           - Transformation & Feature Engineering: total interactions, rate metrics (reach-based and impression-based), ratio features, and temporal cohorts.
           - Storage architectures: relational SQLite database with indexed summary views, analytical Parquet columnar format, and CSV persistence.
        3. **Exploratory Data Analysis & Empirical Observations**
           - Performance variance across media formats (Image, Reel, Carousel).
           - Genre effectiveness across 10 content verticals (Photography, Fashion, Tech, etc.).
           - Traffic acquisition channels and their relative contribution to reach and engagement.
           - Audience activity temporal rhythm: 24-hour distribution and day-of-week heatmaps.
        4. **Statistical Diagnostics & Hypothesis Testing**
           - Bivariate Pearson correlation matrix.
           - Call-to-action impact evaluation (independent samples t-test).
           - Reach versus impressions frequency distribution.
        5. **Interactive Visualization Dashboard Architecture**
           - High-performance Streamlit UI design following clean corporate styling (white background, orange/blue palette).
           - Dynamic reactive filtering across date ranges, account types, media categories, and traffic sources.
           - Automated dynamic insight synthesis directly from filtered records.
        6. **Strategic Recommendations & Limitations**
           - Algorithmic placement optimization and editorial scheduling guidance.
           - Observational data constraints (absence of individual hashtag text, account usernames, and experimental controls).
        """
    )

