"""Engagement and Traffic Analytics Page.
Analyzes traffic acquisition channels, reach vs impressions distribution,
hashtag counts vs engagement, Call-to-Action performance, and statistical correlation matrix.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from src.eda import analyze_traffic_and_features, run_statistical_analysis

COLOR_ORANGE = "#FF5A1F"
COLOR_BLUE = "#1A73E8"
CHART_TEMPLATE = "plotly_white"


def render_engagement_analytics(df):
    st.markdown("## 🚦 Traffic Ingestion & Engagement Drivers")
    st.markdown("Examine traffic channel efficiency, algorithmic distribution (Explore, Reels Feed, Hashtags), Call-to-Action effectiveness, and statistical dependencies.")

    if df.empty:
        st.warning("⚠️ No data matches current filter criteria.")
        return

    tf_data = analyze_traffic_and_features(df)
    traffic_df = tf_data.get("traffic_perf", None)
    cta_df = tf_data.get("cta_perf", None)
    hash_df = tf_data.get("hashtag_perf", None)

    # 1. Traffic Sources Performance
    st.markdown("### 🌐 Traffic Channels: Reach vs Engagement Rate")
    col1, col2 = st.columns(2)

    with col1:
        if traffic_df is not None:
            fig_tr_reach = px.bar(
                traffic_df,
                x="traffic_source",
                y="avg_reach",
                text=traffic_df["avg_reach"].apply(lambda x: f"{x:,.0f}"),
                title="Average Reach Delivered per Traffic Source",
                labels={"traffic_source": "Channel", "avg_reach": "Average Reach"},
                color="traffic_source",
                color_discrete_sequence=px.colors.qualitative.Prism,
                template=CHART_TEMPLATE
            )
            fig_tr_reach.update_layout(height=380, showlegend=False)
            st.plotly_chart(fig_tr_reach, use_container_width=True)

    with col2:
        if traffic_df is not None:
            fig_tr_pie = px.pie(
                traffic_df,
                names="traffic_source",
                values="total_reach",
                hole=0.5,
                title="Total Audience Reach Contribution by Source",
                color_discrete_sequence=px.colors.qualitative.Prism,
                template=CHART_TEMPLATE
            )
            fig_tr_pie.update_layout(height=380)
            st.plotly_chart(fig_tr_pie, use_container_width=True)

    # 2. Reach vs Impressions Relationship
    st.markdown("### 🎯 Reach vs Impressions Distribution & Frequency")
    col3, col4 = st.columns(2)

    with col3:
        # Downsample for snappy scatter plotting if dataset is large
        scatter_sample = df.sample(min(2000, len(df)), random_state=42)
        fig_scatter_ri = px.scatter(
            scatter_sample,
            x="reach",
            y="impressions",
            color="media_type",
            opacity=0.6,
            title="Reach vs Impressions (Sampled n=2,000)",
            labels={"reach": "Reach (Unique)", "impressions": "Impressions (Total Views)"},
            color_discrete_map={"image": COLOR_BLUE, "carousel": COLOR_ORANGE, "reel": "#34A853"},
            template=CHART_TEMPLATE
        )
        fig_scatter_ri.update_layout(height=380)
        st.plotly_chart(fig_scatter_ri, use_container_width=True)

    with col4:
        fig_hist_er = px.histogram(
            df,
            x="calculated_engagement_rate",
            nbins=40,
            title="Calculated Engagement Rate Distribution",
            labels={"calculated_engagement_rate": "Engagement Rate (Reach-based)"},
            color_discrete_sequence=[COLOR_ORANGE],
            template=CHART_TEMPLATE
        )
        fig_hist_er.update_layout(height=380, xaxis_tickformat=".1%")
        st.plotly_chart(fig_hist_er, use_container_width=True)

    # 3. Call-to-Action (CTA) and Hashtags Analysis
    st.markdown("### 📢 Tactical Drivers: Call-to-Action and Hashtag Tiers")
    col5, col6 = st.columns(2)

    with col5:
        if cta_df is not None:
            fig_cta = px.bar(
                cta_df,
                x="has_call_to_action",
                y="avg_er",
                text=cta_df["avg_er"].apply(lambda x: f"{x*100:.2f}%"),
                title="Observed Engagement Rate: With vs Without Call-to-Action",
                labels={"has_call_to_action": "Call-to-Action Presence", "avg_er": "Avg Engagement Rate"},
                color="has_call_to_action",
                color_discrete_map={"With CTA": COLOR_ORANGE, "Without CTA": COLOR_BLUE},
                template=CHART_TEMPLATE
            )
            fig_cta.update_layout(height=360, showlegend=False, yaxis_tickformat=".2%")
            st.plotly_chart(fig_cta, use_container_width=True)

    with col6:
        if hash_df is not None:
            fig_hash = px.bar(
                hash_df,
                x="hashtag_count_group",
                y="avg_er",
                text=hash_df["avg_er"].apply(lambda x: f"{x*100:.2f}%"),
                title="Average Engagement Rate by Hashtag Count Range",
                labels={"hashtag_count_group": "Hashtag Count Tiers", "avg_er": "Avg Engagement Rate"},
                color_discrete_sequence=[COLOR_BLUE],
                template=CHART_TEMPLATE
            )
            fig_hash.update_layout(height=360, yaxis_tickformat=".2%")
            st.plotly_chart(fig_hash, use_container_width=True)

    # 4. Statistical Correlation Matrix
    st.markdown("### 🔬 Statistical Correlation Matrix")
    st.caption("Pearson correlation coefficients across engagement metrics, exposure numbers, and metadata attributes.")
    stats_data = run_statistical_analysis(df)
    corr_mat = stats_data.get("correlation_matrix", None)

    if corr_mat is not None and not corr_mat.empty:
        fig_corr = px.imshow(
            corr_mat,
            text_auto=True,
            aspect="auto",
            color_continuous_scale="RdBu_r",
            zmin=-1,
            zmax=1,
            title="Bivariate Correlation Heatmap",
            template=CHART_TEMPLATE
        )
        fig_corr.update_layout(height=500)
        st.plotly_chart(fig_corr, use_container_width=True)

    # 5. Scientific Interpretation Note
    st.info(
        "💡 **Methodological Note on Observational Data:**\n\n"
        f"- **Reach vs Impressions:** Strong positive correlation (r = {stats_data['corr_reach_imp']:.2f}), confirming repeatable exposure mechanics.\n"
        f"- **Follower Count vs ER:** Weak association (r = {stats_data['corr_follower_er']:.2f}), confirming that viral algorithmic reach is determined by individual content resonance rather than absolute audience size alone.\n"
        f"- **CTA T-Test Outcome:** p-value = {stats_data['cta_ttest']['p_value']:.4f}. Remember that observed differences reflect behavioral associations rather than direct laboratory causality."
    )

