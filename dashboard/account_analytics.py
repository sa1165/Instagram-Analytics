"""Account Analytics Page.
In-depth profiling of unique accounts, creator vs brand dynamics,
follower size vs interaction rates, and full ranking tables.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from src.eda import analyze_accounts

COLOR_ORANGE = "#FF5A1F"
COLOR_BLUE = "#1A73E8"
CHART_TEMPLATE = "plotly_white"


def render_account_analytics(df):
    st.markdown("## 👤 Account Analytics & Benchmarking")
    st.markdown("Examine individual account performance, creator versus brand strategies, follower tiers, and growth velocity.")

    if df.empty:
        st.warning("⚠️ No records found under current filter criteria.")
        return

    acc_results = analyze_accounts(df)
    acc_summary = acc_results.get("account_summary", None)
    b_vs_c = acc_results.get("brand_vs_creator", None)

    if acc_summary is None or acc_summary.empty:
        st.info("No account summary data available.")
        return

    acc_summary["account_display"] = "Account " + acc_summary["account_id"].astype(str)

    # 1. Summary Metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Profile Entities", f"{len(acc_summary)}")
    with c2:
        top_acc = acc_summary.sort_values(by="total_interactions", ascending=False).iloc[0]
        st.metric("Top Interacted Account", f"{top_acc['account_display']}", f"{top_acc['total_interactions']:,} ints")
    with c3:
        top_er_acc = acc_summary.sort_values(by="avg_er", ascending=False).iloc[0]
        st.metric("Highest Avg. ER Account", f"{top_er_acc['account_display']}", f"{top_er_acc['avg_er']*100:.2f}%")
    with c4:
        top_growth_acc = acc_summary.sort_values(by="followers_gained", ascending=False).iloc[0]
        st.metric("Top Follower Gainer", f"{top_growth_acc['account_display']}", f"{top_growth_acc['followers_gained']:,} gained")

    st.markdown("---")

    # 2. Horizontal Comparative Bar Charts: Likes & Total Interactions
    st.markdown("### 🥇 Top 10 Accounts: Likes vs Total Interactions")
    col1, col2 = st.columns(2)

    with col1:
        top10_likes = acc_summary.sort_values(by="total_likes", ascending=True).tail(10)
        fig_l = px.bar(
            top10_likes,
            x="total_likes",
            y="account_display",
            orientation="h",
            title="Top 10 Accounts by Total Likes Received",
            labels={"total_likes": "Total Likes", "account_display": "Account"},
            color="account_type",
            color_discrete_map={"creator": COLOR_BLUE, "brand": COLOR_ORANGE},
            template=CHART_TEMPLATE
        )
        fig_l.update_layout(height=400)
        st.plotly_chart(fig_l, use_container_width=True)

    with col2:
        top10_ints = acc_summary.sort_values(by="total_interactions", ascending=True).tail(10)
        fig_i = px.bar(
            top10_ints,
            x="total_interactions",
            y="account_display",
            orientation="h",
            title="Top 10 Accounts by Total Interactions",
            labels={"total_interactions": "Interactions", "account_display": "Account"},
            color="account_type",
            color_discrete_map={"creator": COLOR_BLUE, "brand": COLOR_ORANGE},
            template=CHART_TEMPLATE
        )
        fig_i.update_layout(height=400)
        st.plotly_chart(fig_i, use_container_width=True)

    # 3. Follower Count Distribution & Account Engagement Rate
    st.markdown("### 👥 Follower Base and Efficiency Scatter Analysis")
    col3, col4 = st.columns(2)

    with col3:
        fig_scatter = px.scatter(
            acc_summary,
            x="follower_count",
            y="avg_er",
            size="total_interactions",
            color="account_type",
            hover_name="account_display",
            title="Follower Count vs Average Engagement Rate (Bubble = Interactions)",
            labels={"follower_count": "Follower Count", "avg_er": "Avg Engagement Rate"},
            color_discrete_map={"creator": COLOR_BLUE, "brand": COLOR_ORANGE},
            template=CHART_TEMPLATE
        )
        fig_scatter.update_layout(height=400, yaxis_tickformat=".2%")
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col4:
        fig_fol_bar = px.bar(
            acc_summary.sort_values(by="follower_count", ascending=True),
            x="follower_count",
            y="account_display",
            orientation="h",
            title="Audience Size by Account",
            labels={"follower_count": "Follower Count", "account_display": "Account"},
            color_discrete_sequence=[COLOR_ORANGE],
            template=CHART_TEMPLATE
        )
        fig_fol_bar.update_layout(height=400)
        st.plotly_chart(fig_fol_bar, use_container_width=True)

    # 4. Brand vs Creator Comparative Matrix
    if b_vs_c is not None and not b_vs_c.empty:
        st.markdown("### 🏢 Brand vs 🎨 Creator Macro Comparison")
        col5, col6, col7 = st.columns(3)
        with col5:
            fig_pie_acctype = px.pie(
                b_vs_c,
                names="account_type",
                values="total_posts",
                title="Post Volume by Profile Type",
                hole=0.5,
                color="account_type",
                color_discrete_map={"creator": COLOR_BLUE, "brand": COLOR_ORANGE},
                template=CHART_TEMPLATE
            )
            fig_pie_acctype.update_layout(height=320)
            st.plotly_chart(fig_pie_acctype, use_container_width=True)

        with col6:
            fig_bar_er = px.bar(
                b_vs_c,
                x="account_type",
                y="avg_er",
                title="Average Engagement Rate by Type",
                labels={"avg_er": "Engagement Rate", "account_type": "Account Type"},
                color="account_type",
                color_discrete_map={"creator": COLOR_BLUE, "brand": COLOR_ORANGE},
                template=CHART_TEMPLATE
            )
            fig_bar_er.update_layout(height=320, showlegend=False, yaxis_tickformat=".2%")
            st.plotly_chart(fig_bar_er, use_container_width=True)

        with col7:
            fig_bar_reach = px.bar(
                b_vs_c,
                x="account_type",
                y="avg_reach",
                title="Average Reach per Post by Type",
                labels={"avg_reach": "Average Reach", "account_type": "Account Type"},
                color="account_type",
                color_discrete_map={"creator": COLOR_BLUE, "brand": COLOR_ORANGE},
                template=CHART_TEMPLATE
            )
            fig_bar_reach.update_layout(height=320, showlegend=False)
            st.plotly_chart(fig_bar_reach, use_container_width=True)

    # 5. Full Account Summary Table
    st.markdown("### 📋 Complete Account Benchmarking Table")
    display_table = acc_summary[[
        "account_id", "account_type", "follower_count", "posts_count",
        "total_likes", "total_comments", "total_shares", "total_saves",
        "total_interactions", "total_reach", "followers_gained", "avg_er"
    ]].copy()
    display_table["avg_er"] = (display_table["avg_er"] * 100).round(2).astype(str) + "%"
    st.dataframe(display_table.sort_values(by="total_interactions", ascending=False), use_container_width=True)

