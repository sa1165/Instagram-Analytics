"""Overview Page: Executive Social Media Performance Dashboard.
Displays top-level KPI cards, monthly trends, interaction breakdowns,
account rankings, and media distribution.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from src.eda import calculate_kpi_summary, analyze_accounts, analyze_content, analyze_temporal

# Brand palette constants
COLOR_ORANGE = "#FF5A1F"
COLOR_BLUE = "#1A73E8"
COLOR_LIGHT_BLUE = "#E8F0FE"
COLOR_LIGHT_ORANGE = "#FFF0EB"
CHART_TEMPLATE = "plotly_white"


def render_overview(df):
    st.markdown("## 📊 Executive Overview Dashboard")
    st.markdown("Comprehensive view of high-level Instagram user engagement, content volume, reach, and performance benchmarks.")

    if df.empty:
        st.warning("⚠️ No data matches the active filter settings. Please adjust your sidebar filters.")
        return

    # Calculate KPIs
    kpi = calculate_kpi_summary(df)

    # 1. KPI Cards Row 1
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            label="Total Posts Published",
            value=f"{kpi['total_posts']:,}",
            help="Total number of published Instagram posts within selected slice"
        )
    with col2:
        st.metric(
            label="Total Interactions",
            value=f"{kpi['total_interactions']:,}",
            delta=f"{kpi['total_likes']:,} likes",
            help="Sum of likes, comments, shares, and saves"
        )
    with col3:
        st.metric(
            label="Total Reach",
            value=f"{kpi['total_reach']:,}",
            delta=f"{kpi['avg_reach_per_post']:,.0f} avg/post",
            help="Unique accounts that viewed the posts"
        )
    with col4:
        st.metric(
            label="Avg. Engagement Rate (Reach)",
            value=f"{kpi['avg_engagement_rate']*100:.2f}%",
            help="Formula: (Likes + Comments + Shares + Saves) / Reach"
        )

    # KPI Cards Row 2
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.metric(
            label="Total Likes",
            value=f"{kpi['total_likes']:,}",
            help="Cumulative likes across all posts"
        )
    with col6:
        st.metric(
            label="Total Comments",
            value=f"{kpi['total_comments']:,}",
            help="Cumulative comments received"
        )
    with col7:
        st.metric(
            label="Total Followers Gained",
            value=f"{kpi['total_followers_gained']:,}",
            help="Follower net additions generated from these posts"
        )
    with col8:
        st.metric(
            label="Active Unique Accounts",
            value=f"{kpi['unique_accounts']}",
            help="Number of distinct publishing accounts"
        )

    st.markdown("---")

    # 2. Monthly Engagement & Posting Volume Trends
    temporal_data = analyze_temporal(df)
    m_df = temporal_data.get("monthly_trend", None)

    if m_df is not None and not m_df.empty:
        st.markdown("### 📈 Longitudinal Performance Trends")
        c1, c2 = st.columns(2)

        with c1:
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(
                x=m_df["posting_year_month"],
                y=m_df["total_interactions"],
                name="Total Interactions",
                mode="lines+markers",
                line=dict(color=COLOR_ORANGE, width=3),
                marker=dict(size=7, color=COLOR_ORANGE)
            ))
            fig_trend.add_trace(go.Scatter(
                x=m_df["posting_year_month"],
                y=m_df["total_reach"],
                name="Total Reach",
                mode="lines+markers",
                yaxis="y2",
                line=dict(color=COLOR_BLUE, width=3, dash="dash"),
                marker=dict(size=7, color=COLOR_BLUE)
            ))
            fig_trend.update_layout(
                title="Monthly Interactions vs Reach Trajectory",
                template=CHART_TEMPLATE,
                height=380,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                yaxis=dict(title="Interactions", color=COLOR_ORANGE),
                yaxis2=dict(title="Reach", color=COLOR_BLUE, overlaying="y", side="right")
            )
            st.plotly_chart(fig_trend, use_container_width=True)

        with c2:
            fig_bar = px.bar(
                m_df,
                x="posting_year_month",
                y="posts_count",
                title="Posts Published by Month",
                labels={"posting_year_month": "Month", "posts_count": "Post Volume"},
                color_discrete_sequence=[COLOR_BLUE],
                template=CHART_TEMPLATE
            )
            fig_bar.update_layout(height=380)
            st.plotly_chart(fig_bar, use_container_width=True)

    # 3. Interactions Composition & Performance Buckets
    st.markdown("### 🍩 Interaction Components & Performance Segmentations")
    c3, c4 = st.columns(2)

    with c3:
        interaction_labels = ["Likes", "Comments", "Shares", "Saves"]
        interaction_values = [kpi["total_likes"], kpi["total_comments"], kpi["total_shares"], kpi["total_saves"]]
        fig_donut = go.Figure(data=[go.Pie(
            labels=interaction_labels,
            values=interaction_values,
            hole=0.55,
            marker_colors=[COLOR_ORANGE, COLOR_BLUE, "#34A853", "#FBBC05"]
        )])
        fig_donut.update_layout(
            title="Total Interactions Breakdown",
            template=CHART_TEMPLATE,
            height=360
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with c4:
        content_data = analyze_content(df)
        b_df = content_data.get("bucket_perf", None)
        if b_df is not None:
            fig_bucket = px.pie(
                b_df,
                names="performance_bucket_label",
                values="post_count",
                hole=0.55,
                title="Performance Bucket Distribution",
                color="performance_bucket_label",
                color_discrete_map={
                    "viral": COLOR_ORANGE,
                    "high": COLOR_BLUE,
                    "medium": "#FBBC05",
                    "low": "#9AA0A6"
                },
                template=CHART_TEMPLATE
            )
            fig_bucket.update_layout(height=360)
            st.plotly_chart(fig_bucket, use_container_width=True)

    # 4. Top Accounts Rankings
    st.markdown("### 🏆 Top Performing Accounts Benchmarking")
    acc_data = analyze_accounts(df)
    c5, c6 = st.columns(2)

    with c5:
        top_likes = acc_data.get("top_by_likes", None)
        if top_likes is not None:
            top_likes_sorted = top_likes.sort_values(by="total_likes", ascending=True)
            top_likes_sorted["account_display"] = "Account " + top_likes_sorted["account_id"].astype(str)
            fig_top_likes = px.bar(
                top_likes_sorted,
                x="total_likes",
                y="account_display",
                orientation="h",
                title="Top 10 Accounts by Total Likes",
                labels={"total_likes": "Total Likes", "account_display": "Account"},
                color_discrete_sequence=[COLOR_ORANGE],
                template=CHART_TEMPLATE
            )
            fig_top_likes.update_layout(height=380)
            st.plotly_chart(fig_top_likes, use_container_width=True)

    with c6:
        top_posts = acc_data.get("top_by_posts", None)
        if top_posts is not None:
            top_posts_sorted = top_posts.sort_values(by="posts_count", ascending=True)
            top_posts_sorted["account_display"] = "Account " + top_posts_sorted["account_id"].astype(str)
            fig_top_posts = px.bar(
                top_posts_sorted,
                x="posts_count",
                y="account_display",
                orientation="h",
                title="Top 10 Most Active Accounts by Post Count",
                labels={"posts_count": "Published Posts", "account_display": "Account"},
                color_discrete_sequence=[COLOR_BLUE],
                template=CHART_TEMPLATE
            )
            fig_top_posts.update_layout(height=380)
            st.plotly_chart(fig_top_posts, use_container_width=True)

    # 5. Media & Content Category Distributions
    st.markdown("### 📱 Media Format and Content Category Allocation")
    c7, c8 = st.columns(2)

    with c7:
        m_perf = content_data.get("media_perf", None)
        if m_perf is not None:
            fig_media = px.bar(
                m_perf,
                x="media_type",
                y="post_count",
                title="Posts by Media Format (Image vs Carousel vs Reel)",
                labels={"media_type": "Media Format", "post_count": "Count"},
                color="media_type",
                color_discrete_map={"image": COLOR_BLUE, "carousel": COLOR_ORANGE, "reel": "#34A853"},
                template=CHART_TEMPLATE
            )
            fig_media.update_layout(height=350, showlegend=False)
            st.plotly_chart(fig_media, use_container_width=True)

    with c8:
        c_perf = content_data.get("category_perf", None)
        if c_perf is not None:
            fig_cat = px.bar(
                c_perf.sort_values(by="post_count", ascending=True),
                x="post_count",
                y="content_category",
                orientation="h",
                title="Post Volume by Content Genre",
                labels={"post_count": "Posts Count", "content_category": "Genre"},
                color_discrete_sequence=[COLOR_ORANGE],
                template=CHART_TEMPLATE
            )
            fig_cat.update_layout(height=350)
            st.plotly_chart(fig_cat, use_container_width=True)

