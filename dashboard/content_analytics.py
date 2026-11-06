"""Content Analytics Page.
Evaluates Image vs Reel vs Carousel effectiveness, category breakdowns,
interaction types (shares/saves vs likes/comments), and top-performing post leaderboards.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from src.eda import analyze_content

COLOR_ORANGE = "#FF5A1F"
COLOR_BLUE = "#1A73E8"
CHART_TEMPLATE = "plotly_white"


def render_content_analytics(df):
    st.markdown("## 🎬 Content Performance & Media Formats")
    st.markdown("Analyze how creative format choices (Image, Reel, Carousel) and editorial content genres drive virality, reach, and intent actions.")

    if df.empty:
        st.warning("⚠️ No data matches current filters.")
        return

    content_data = analyze_content(df)
    m_perf = content_data.get("media_perf", None)
    c_perf = content_data.get("category_perf", None)

    # 1. Media Type Comparison
    st.markdown("### 📸 Format Performance Comparison: Image vs Reel vs Carousel")
    col1, col2 = st.columns(2)

    with col1:
        if m_perf is not None:
            fig_media_er = px.bar(
                m_perf,
                x="media_type",
                y="avg_er",
                text=m_perf["avg_er"].apply(lambda x: f"{x*100:.2f}%"),
                title="Average Engagement Rate by Media Format",
                labels={"media_type": "Format", "avg_er": "Avg Engagement Rate"},
                color="media_type",
                color_discrete_map={"image": COLOR_BLUE, "carousel": COLOR_ORANGE, "reel": "#34A853"},
                template=CHART_TEMPLATE
            )
            fig_media_er.update_layout(height=380, showlegend=False, yaxis_tickformat=".2%")
            st.plotly_chart(fig_media_er, use_container_width=True)

    with col2:
        if m_perf is not None:
            fig_media_reach = px.bar(
                m_perf,
                x="media_type",
                y="avg_reach",
                text=m_perf["avg_reach"].apply(lambda x: f"{x:,.0f}"),
                title="Average Reach by Media Format",
                labels={"media_type": "Format", "avg_reach": "Average Reach"},
                color="media_type",
                color_discrete_map={"image": COLOR_BLUE, "carousel": COLOR_ORANGE, "reel": "#34A853"},
                template=CHART_TEMPLATE
            )
            fig_media_reach.update_layout(height=380, showlegend=False)
            st.plotly_chart(fig_media_reach, use_container_width=True)

    # 2. Granular Action Breakdown across Media Types (Grouped Bar)
    st.markdown("### 📊 Interaction Profile by Format (Likes, Comments, Shares, Saves)")
    if m_perf is not None:
        fig_actions = go.Figure()
        fig_actions.add_trace(go.Bar(
            name="Avg Likes", x=m_perf["media_type"], y=m_perf["avg_likes"], marker_color=COLOR_ORANGE
        ))
        fig_actions.add_trace(go.Bar(
            name="Avg Saves", x=m_perf["media_type"], y=m_perf["avg_saves"], marker_color=COLOR_BLUE
        ))
        fig_actions.add_trace(go.Bar(
            name="Avg Shares", x=m_perf["media_type"], y=m_perf["avg_shares"], marker_color="#34A853"
        ))
        fig_actions.add_trace(go.Bar(
            name="Avg Comments", x=m_perf["media_type"], y=m_perf["avg_comments"], marker_color="#FBBC05"
        ))
        fig_actions.update_layout(
            barmode="group",
            title="Granular Interaction Averages across Media Formats",
            template=CHART_TEMPLATE,
            height=380,
            yaxis=dict(title="Average Metric per Post")
        )
        st.plotly_chart(fig_actions, use_container_width=True)

    # 3. Content Category Deep Dive
    st.markdown("### 🏷️ Content Category Benchmarking")
    col3, col4 = st.columns(2)

    with col3:
        if c_perf is not None:
            fig_cat_er = px.bar(
                c_perf.sort_values(by="avg_er", ascending=True),
                x="avg_er",
                y="content_category",
                orientation="h",
                text=c_perf["avg_er"].apply(lambda x: f"{x*100:.2f}%"),
                title="Top Content Categories by Engagement Rate",
                labels={"avg_er": "Avg Engagement Rate", "content_category": "Genre"},
                color_discrete_sequence=[COLOR_ORANGE],
                template=CHART_TEMPLATE
            )
            fig_cat_er.update_layout(height=420, yaxis_tickformat=".2%")
            st.plotly_chart(fig_cat_er, use_container_width=True)

    with col4:
        if c_perf is not None:
            fig_cat_reach = px.bar(
                c_perf.sort_values(by="avg_reach", ascending=True),
                x="avg_reach",
                y="content_category",
                orientation="h",
                text=c_perf["avg_reach"].apply(lambda x: f"{x:,.0f}"),
                title="Top Content Categories by Average Reach",
                labels={"avg_reach": "Average Reach", "content_category": "Genre"},
                color_discrete_sequence=[COLOR_BLUE],
                template=CHART_TEMPLATE
            )
            fig_cat_reach.update_layout(height=420)
            st.plotly_chart(fig_cat_reach, use_container_width=True)

    # 4. Top Performing Posts Leaderboard
    st.markdown("### 🚀 Top 10 High-Engagement Posts Leaderboard")
    top_posts = df.sort_values(by="total_interactions", ascending=False).head(10)[[
        "post_id", "account_id", "account_type", "media_type", "content_category",
        "traffic_source", "likes", "comments", "shares", "saves", "reach",
        "calculated_engagement_rate", "performance_bucket_label"
    ]].copy()
    top_posts["calculated_engagement_rate"] = (top_posts["calculated_engagement_rate"] * 100).round(2).astype(str) + "%"
    st.dataframe(top_posts, use_container_width=True)

