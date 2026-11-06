"""Audience and Temporal Analytics Page.
Analyzes posting schedules, day-of-week receptivity, hourly engagement curves,
and day vs hour engagement heatmaps.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from src.eda import analyze_temporal

COLOR_ORANGE = "#FF5A1F"
COLOR_BLUE = "#1A73E8"
CHART_TEMPLATE = "plotly_white"


def render_time_analytics(df):
    st.markdown("## ⏰ Audience Activity & Temporal Analytics")
    st.markdown("Identify peak audience responsiveness, optimal posting windows, weekday variations, and hourly engagement rhythms.")

    if df.empty:
        st.warning("⚠️ No data matches current filter settings.")
        return

    t_data = analyze_temporal(df)
    w_df = t_data.get("weekday_perf", None)
    h_df = t_data.get("hourly_perf", None)
    heatmap_df = t_data.get("heatmap_df", None)

    # 1. Optimal Windows Summary Cards
    if h_df is not None and w_df is not None and not h_df.empty and not w_df.empty:
        best_hour_row = h_df.sort_values(by="avg_er", ascending=False).iloc[0]
        best_day_row = w_df.sort_values(by="avg_er", ascending=False).iloc[0]
        peak_volume_hour = h_df.sort_values(by="post_count", ascending=False).iloc[0]

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Best Engagement Day", f"{best_day_row['day_of_week']}", f"{best_day_row['avg_er']*100:.2f}% avg ER")
        with c2:
            st.metric("Peak Engagement Hour", f"{int(best_hour_row['posting_hour']):02d}:00 HRS", f"{best_hour_row['avg_er']*100:.2f}% avg ER")
        with c3:
            st.metric("Highest Posting Density", f"{int(peak_volume_hour['posting_hour']):02d}:00 HRS", f"{int(peak_volume_hour['post_count']):,} posts")

    st.markdown("---")

    # 2. Weekday Engagement and Volume
    st.markdown("### 📅 Day of Week Engagement Dynamics")
    col1, col2 = st.columns(2)

    with col1:
        if w_df is not None:
            fig_week_er = px.bar(
                w_df,
                x="day_of_week",
                y="avg_er",
                text=w_df["avg_er"].apply(lambda x: f"{x*100:.2f}%"),
                title="Average Engagement Rate by Day of Week",
                labels={"day_of_week": "Day", "avg_er": "Avg Engagement Rate"},
                color_discrete_sequence=[COLOR_ORANGE],
                template=CHART_TEMPLATE
            )
            fig_week_er.update_layout(height=360, yaxis_tickformat=".2%")
            st.plotly_chart(fig_week_er, use_container_width=True)

    with col2:
        if w_df is not None:
            fig_week_vol = px.bar(
                w_df,
                x="day_of_week",
                y="post_count",
                text="post_count",
                title="Publication Frequency by Day of Week",
                labels={"day_of_week": "Day", "post_count": "Total Posts Published"},
                color_discrete_sequence=[COLOR_BLUE],
                template=CHART_TEMPLATE
            )
            fig_week_vol.update_layout(height=360)
            st.plotly_chart(fig_week_vol, use_container_width=True)

    # 3. Hourly Engagement and Interaction Profiles
    st.markdown("### 🕒 24-Hour Engagement & Volume Trajectory")
    if h_df is not None:
        fig_hour = go.Figure()
        fig_hour.add_trace(go.Scatter(
            x=h_df["posting_hour"],
            y=h_df["avg_er"] * 100,
            mode="lines+markers",
            name="Avg Engagement Rate (%)",
            line=dict(color=COLOR_ORANGE, width=3),
            marker=dict(size=8, color=COLOR_ORANGE)
        ))
        fig_hour.add_trace(go.Bar(
            x=h_df["posting_hour"],
            y=h_df["post_count"],
            name="Posting Count (Volume)",
            yaxis="y2",
            marker_color=COLOR_BLUE,
            opacity=0.3
        ))
        fig_hour.update_layout(
            title="Hourly Posting Density vs Observed Engagement Efficiency",
            template=CHART_TEMPLATE,
            height=380,
            xaxis=dict(title="Hour of Day (0-23)", tickmode="linear", tick0=0, dtick=1),
            yaxis=dict(title="Avg Engagement Rate (%)", color=COLOR_ORANGE),
            yaxis2=dict(title="Published Post Volume", color=COLOR_BLUE, overlaying="y", side="right"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_hour, use_container_width=True)

    # 4. Day vs Hour Heatmap
    st.markdown("### 🗺️ Day vs Hour Engagement Rate Heatmap")
    st.caption("Visual matrix highlighting high-yield publication sweet spots (Darker Orange = Higher Engagement Rate).")
    if heatmap_df is not None and not heatmap_df.empty:
        fig_heat = px.imshow(
            heatmap_df * 100,
            labels=dict(x="Hour of Day (24h)", y="Day of Week", color="Avg ER (%)"),
            x=[f"{h:02d}:00" for h in heatmap_df.columns],
            y=heatmap_df.index,
            color_continuous_scale=["#FFF5F0", "#FEE0D2", "#FC9272", "#FB6A4A", "#DE2D26", "#A50F15"],
            template=CHART_TEMPLATE,
            aspect="auto"
        )
        fig_heat.update_layout(height=420)
        st.plotly_chart(fig_heat, use_container_width=True)

