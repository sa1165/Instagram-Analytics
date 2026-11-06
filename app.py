"""Instagram Analytics Dashboard - Tableau Inspired Redesign.
Faithfully recreates the visual language, typography, compact layout,
and color palette (#E5933B orange and #607FA9 muted blue) of the Tableau reference design.
Preserves full analytical correctness and existing backend data lifecycle.
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Brand Color Palette matching Tableau Reference
ORANGE = "#E5933B"
MUTED_BLUE = "#607FA9"
NAVY = "#253F68"
LIGHT_GREY = "#F4F5F7"
TEXT_COLOR = "#30343B"
MUTED_TEXT = "#7A828E"
LINE_GREY = "#E1E4E8"
WHITE = "#FFFFFF"

# Categorical palette matching reference bubbles
BUBBLE_PALETTE = [
    "#A89F91",  # Warm taupe / grey
    "#827261",  # Dark taupe
    "#607FA9",  # Muted blue
    "#E5933B",  # Orange
    "#E2BD56",  # Mustard yellow
    "#6FA271",  # Sage green
    "#7BB8B5",  # Soft teal
    "#B05355",  # Muted berry
    "#D99B9B",  # Dusty rose
    "#957E9F"   # Muted purple
]

# Set page config
st.set_page_config(
    page_title="Instagram Clone Data Analysis Dashboard",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to eliminate Streamlit clunky styling and emulate Tableau minimalism
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global Typography & Reset */
    html, body, [class*="css"], .stApp {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: {WHITE} !important;
        color: {TEXT_COLOR} !important;
    }}

    /* Main Container Padding */
    .block-container {{
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100% !important;
    }}

    /* Keep standard Streamlit header accessible for sidebar toggle button */
    header[data-testid="stHeader"] {{
        background: transparent !important;
        z-index: 100 !important;
    }}
    /* Ensure the collapse/expand sidebar button is prominently visible */
    button[data-testid="stSidebarCollapseButton"],
    button[data-testid="stBaseButton-headerNoPadding"] {{
        color: #1E293B !important;
        background-color: #F1F5F9 !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 4px !important;
    }}
    footer {{
        display: none !important;
    }}
    #MainMenu {{
        visibility: hidden !important;
    }}

    /* Tableau Header Style */
    .tableau-title {{
        font-size: 22px;
        font-weight: 700;
        margin-bottom: 0px;
        padding-bottom: 0px;
        letter-spacing: -0.3px;
    }}
    .tableau-title span.orange {{
        color: {ORANGE};
    }}
    .tableau-title span.blue {{
        color: {MUTED_BLUE};
    }}

    /* Section Subtitle */
    .tableau-section-title {{
        font-size: 13px;
        font-weight: 600;
        color: {TEXT_COLOR};
        margin-bottom: 4px;
        letter-spacing: -0.1px;
    }}

    /* KPI Component in Tableau Style (Small label above, huge clean number) */
    .tableau-kpi-container {{
        display: flex;
        flex-direction: column;
        padding: 4px 6px;
        margin-bottom: 12px;
    }}
    .tableau-kpi-label {{
        font-size: 11px;
        font-weight: 500;
        color: {TEXT_COLOR};
        line-height: 1.25;
        min-height: 28px;
        display: flex;
        align-items: flex-end;
    }}
    .tableau-kpi-value {{
        font-size: 34px;
        font-weight: 700;
        line-height: 1.1;
        letter-spacing: -0.5px;
    }}
    .tableau-kpi-value.orange {{
        color: {ORANGE};
    }}
    .tableau-kpi-value.blue {{
        color: {MUTED_BLUE};
    }}
    .tableau-kpi-unit {{
        font-size: 18px;
        font-weight: 500;
        color: {MUTED_BLUE};
    }}

    /* Minimalist Tableau-like Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: #F0F2F5 !important;
        border-right: 1px solid #D0D5DD !important;
        padding-top: 1rem !important;
    }}
    
    /* Force high contrast text on all sidebar elements */
    section[data-testid="stSidebar"] * {{
        color: #1E293B !important;
    }}
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] label p,
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stMultiSelect label,
    section[data-testid="stSidebar"] .stRadio label,
    section[data-testid="stSidebar"] .stRadio div,
    section[data-testid="stSidebar"] .stRadio label p {{
        font-size: 11px !important;
        font-weight: 600 !important;
        color: #0F172A !important;
        opacity: 1 !important;
    }}
    
    /* Radio options high contrast */
    section[data-testid="stSidebar"] div[role="radiogroup"] label {{
        color: #1E293B !important;
        font-weight: 500 !important;
    }}
    section[data-testid="stSidebar"] div[role="radiogroup"] label span {{
        color: #1E293B !important;
    }}

    /* MultiSelect Tags / Badges in Sidebar */
    section[data-testid="stSidebar"] span[data-baseweb="tag"] {{
        background-color: #E2E8F0 !important;
        color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
    }}
    section[data-testid="stSidebar"] span[data-baseweb="tag"] span {{
        color: #0F172A !important;
        font-weight: 500 !important;
    }}
    
    /* Small Compact Selectboxes */
    div[data-baseweb="select"] > div {{
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 4px !important;
        min-height: 32px !important;
        font-size: 12px !important;
    }}
    div[data-baseweb="select"] * {{
        color: #0F172A !important;
    }}

    /* Minimalist Horizontal Line */
    hr.tableau-divider {{
        border: 0;
        height: 1px;
        background: {LINE_GREY};
        margin: 12px 0 16px 0;
    }}

    /* Tighten column gaps */
    div[data-testid="column"] {{
        padding: 0 8px !important;
    }}

    /* Tableau Table Styling */
    .stDataFrame {{
        border: 1px solid #CBD5E1 !important;
        border-radius: 4px;
    }}
</style>
""", unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    """Load cached dataset from parquet or run ETL."""
    p_path = Path("data/processed/cleaned_data.parquet")
    if p_path.exists():
        df = pd.read_parquet(p_path)
    else:
        from src.etl_pipeline import run_etl_pipeline
        run_etl_pipeline()
        df = pd.read_parquet(p_path)
    if not pd.api.types.is_datetime64_any_dtype(df["post_datetime"]):
        df["post_datetime"] = pd.to_datetime(df["post_datetime"])
    return df


def main():
    df_raw = load_data()
    all_years = sorted(df_raw["posting_year"].unique().tolist())
    all_acc_types = sorted(df_raw["account_type"].unique().tolist())
    all_acc_ids = sorted(df_raw["account_id"].unique().tolist())
    all_media_types = sorted(df_raw["media_type"].unique().tolist())
    all_categories = sorted(df_raw["content_category"].unique().tolist())
    all_traffic_sources = sorted(df_raw["traffic_source"].unique().tolist())
    all_buckets = ["low", "medium", "high", "viral"]

    # Session state for sidebar visibility
    if "show_sidebar" not in st.session_state:
        st.session_state["show_sidebar"] = True

    # If user chose to hide sidebar, inject CSS to collapse it completely
    if not st.session_state["show_sidebar"]:
        st.markdown("""
        <style>
            section[data-testid="stSidebar"] {
                display: none !important;
            }
        </style>
        """, unsafe_allow_html=True)

    # ==========================================
    # SIDEBAR: 25% Filter & Interactive Controls
    # ==========================================
    if st.session_state["show_sidebar"]:
        with st.sidebar:
            st.markdown(f"<div style='font-size:14px; font-weight:700; color:{NAVY}; margin-bottom:8px;'>Parameters & Filters</div>", unsafe_allow_html=True)

            # Hide sidebar button inside sidebar
            if st.button("◀ Hide Filters Sidebar", use_container_width=True):
                st.session_state["show_sidebar"] = False
                st.rerun()

            # Reset button
            if st.button("↺ Reset All Filters", use_container_width=True):
                st.session_state.clear()
                st.session_state["show_sidebar"] = True
                st.rerun()

            st.markdown("<hr style='margin:8px 0; border:none; border-top:1px solid #CBD5E1;'/>", unsafe_allow_html=True)

            # 1. Year Filter
            selected_years = st.multiselect("Year", options=all_years, default=all_years)

            # 2. Account Type Filter
            selected_acc_types = st.multiselect("Account Type", options=all_acc_types, default=all_acc_types)

            # 3. Account ID Filter
            acc_id_options = [f"account_{i}" for i in all_acc_ids]
            selected_account_labels = st.multiselect("Account ID (Single/Multi)", options=acc_id_options, default=[])
            selected_accounts = [int(lbl.replace("account_", "")) for lbl in selected_account_labels]

            # 4. Media Type Filter
            selected_media = st.multiselect("Media Type", options=all_media_types, default=all_media_types)

            # 5. Content Category Filter
            selected_categories = st.multiselect("Content Category", options=all_categories, default=all_categories)

            # 6. Traffic Source Filter
            selected_traffic = st.multiselect("Traffic Source", options=all_traffic_sources, default=all_traffic_sources)

            # 7. Performance Bucket
            selected_buckets = st.multiselect("Performance Bucket", options=all_buckets, default=all_buckets)

            # 8. Call to Action Filter
            cta_opt = st.radio("Call to Action (CTA)", ["(All)", "With CTA (1)", "Without CTA (0)"], index=0)

            st.markdown("<hr style='margin:10px 0; border:none; border-top:1px solid #CBD5E1;'/>", unsafe_allow_html=True)

            # Interaction Toggle for Tableau Dual-Line
            weekday_metric_toggle = st.radio(
                "Weekday Trend Display Metric:",
                ["Average (Likes vs Comments)", "Totals (Likes vs Comments)", "Total Interactions vs Reach"],
                index=0
            )

            # Bubble size encoding option
            bubble_size_mode = st.radio(
                "Category Bubble Size Metric:",
                ["Total Interactions", "Post Count (Volume)", "Total Reach"],
                index=0
            )
    else:
        # Default fallback values when sidebar is hidden
        selected_years = all_years
        selected_acc_types = all_acc_types
        selected_accounts = []
        selected_media = all_media_types
        selected_categories = all_categories
        selected_traffic = all_traffic_sources
        selected_buckets = all_buckets
        cta_opt = "(All)"
        weekday_metric_toggle = "Average (Likes vs Comments)"
        bubble_size_mode = "Total Interactions"

    # ==========================================
    # APPLY FILTERING LOGIC
    # ==========================================
    df = df_raw.copy()

    if selected_years:
        df = df[df["posting_year"].isin(selected_years)]
    if selected_acc_types:
        df = df[df["account_type"].isin(selected_acc_types)]
    if selected_accounts:
        df = df[df["account_id"].isin(selected_accounts)]
    if selected_media:
        df = df[df["media_type"].isin(selected_media)]
    if selected_categories:
        df = df[df["content_category"].isin(selected_categories)]
    if selected_traffic:
        df = df[df["traffic_source"].isin(selected_traffic)]
    if selected_buckets:
        df = df[df["performance_bucket_label"].isin(selected_buckets)]
    if cta_opt == "With CTA (1)":
        df = df[df["has_call_to_action"] == 1]
    elif cta_opt == "Without CTA (0)":
        df = df[df["has_call_to_action"] == 0]

    if df.empty:
        st.warning("⚠️ No records match the active filter criteria. Please broaden your selection in the sidebar.")
        return

    # ==========================================
    # HEADER ROW: Tableau Title + Controls
    # ==========================================
    header_col1, header_col2, header_col3 = st.columns([2.8, 0.7, 0.5])
    with header_col1:
        st.markdown("""
        <div class="tableau-title">
            <span class="orange">Instagram</span> <span class="blue">Clone Data Analysis Dashboard</span>
        </div>
        """, unsafe_allow_html=True)

    with header_col2:
        # Top right compact year filter mirroring reference screenshot
        year_options = ["(All)"] + [str(y) for y in all_years]
        top_year = st.selectbox(
            "User Post Year",
            options=year_options,
            index=0,
            label_visibility="visible"
        )
        if top_year != "(All)":
            df = df[df["posting_year"] == int(top_year)]

    with header_col3:
        st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
        # Show toggle button for sidebar when hidden or visible
        if not st.session_state["show_sidebar"]:
            if st.button("▶ Show Filters", use_container_width=True):
                st.session_state["show_sidebar"] = True
                st.rerun()
        else:
            if st.button("◀ Hide Filters", use_container_width=True):
                st.session_state["show_sidebar"] = False
                st.rerun()

    # ==========================================
    # ROW 1: ACCOUNT PERFORMANCE
    # Left: Top 15 Accounts by Total Likes (Horizontal Bar)
    # Right: Top 5 Accounts by Number of Posts (Vertical Bar)
    # ==========================================
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    row1_left, row1_right = st.columns([65, 35])

    with row1_left:
        # Top 15 Accounts by Likes
        acc_likes = df.groupby("account_id")["likes"].sum().reset_index()
        top15 = acc_likes.sort_values(by="likes", ascending=True).tail(15).copy()
        top15["account_label"] = "account_" + top15["account_id"].astype(str)

        # Alternating / Highlight top bars with orange and remaining with muted blue as in Tableau ref
        # In the reference, top 4-5 bars and selected records are highlighted orange
        max_likes = top15["likes"].max()
        cutoff_high = top15["likes"].quantile(0.70)
        bar_colors = [ORANGE if val >= cutoff_high else MUTED_BLUE for val in top15["likes"]]

        fig_row1_left = go.Figure(go.Bar(
            x=top15["likes"],
            y=top15["account_label"],
            orientation="h",
            marker=dict(color=bar_colors),
            text=top15["likes"].apply(lambda v: f"{v:,.0f}"),
            textposition="outside",
            textfont=dict(size=10, family="Inter", color=TEXT_COLOR),
            cliponaxis=False
        ))

        fig_row1_left.update_layout(
            title=dict(
                text="Users with the Most Likes",
                font=dict(size=13, family="Inter", color=TEXT_COLOR, weight=600),
                x=0,
                y=0.98
            ),
            plot_bgcolor=WHITE,
            paper_bgcolor=WHITE,
            margin=dict(l=85, r=75, t=35, b=25),
            height=340,
            xaxis=dict(
                range=[0, max_likes * 1.15],
                showgrid=True,
                gridcolor=LINE_GREY,
                gridwidth=0.5,
                zeroline=True,
                zerolinecolor=LINE_GREY,
                showticklabels=True,
                tickfont=dict(size=9, color=MUTED_TEXT)
            ),
            yaxis=dict(
                showgrid=False,
                tickfont=dict(size=10, color=TEXT_COLOR)
            )
        )
        st.plotly_chart(fig_row1_left, use_container_width=True, config={"displayModeBar": False})

    with row1_right:
        # Top 5 Accounts by Number of Posts (Vertical Bar)
        top5_posts = df.groupby("account_id")["post_id"].count().reset_index()
        top5_posts = top5_posts.rename(columns={"post_id": "post_count"}).sort_values(by="post_count", ascending=True).tail(5).copy()
        top5_posts["account_label"] = "acc_" + top5_posts["account_id"].astype(str)
        max_posts = top5_posts["post_count"].max()

        # Alternating blue and orange bars matching the reference
        vert_colors = [MUTED_BLUE, ORANGE, MUTED_BLUE, MUTED_BLUE, ORANGE]

        fig_row1_right = go.Figure(go.Bar(
            x=top5_posts["account_label"],
            y=top5_posts["post_count"],
            marker=dict(color=vert_colors),
            text=top5_posts["post_count"].apply(lambda v: f"{v:,}"),
            textposition="outside",
            textfont=dict(size=10, family="Inter", color=TEXT_COLOR),
            cliponaxis=False
        ))

        fig_row1_right.update_layout(
            title=dict(
                text="Number of Posts by Most<br>Active Users",
                font=dict(size=13, family="Inter", color=TEXT_COLOR, weight=600),
                x=0,
                y=0.98
            ),
            plot_bgcolor=WHITE,
            paper_bgcolor=WHITE,
            margin=dict(l=40, r=20, t=45, b=25),
            height=340,
            xaxis=dict(
                showgrid=False,
                tickfont=dict(size=10, color=TEXT_COLOR),
                tickangle=-90
            ),
            yaxis=dict(
                range=[0, max_posts * 1.15],
                showgrid=True,
                gridcolor=LINE_GREY,
                gridwidth=0.5,
                zeroline=False,
                tickfont=dict(size=9, color=MUTED_TEXT)
            )
        )
        st.plotly_chart(fig_row1_right, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<hr class='tableau-divider'/>", unsafe_allow_html=True)

    # ==========================================
    # ROW 2: LARGE TABLEAU-STYLE KPI METRICS
    # Small label above, large clean numbers alternating Orange and Blue
    # ==========================================
    total_posts = len(df)
    total_likes = int(df["likes"].sum())
    total_interactions = int(df["total_interactions"].sum())
    avg_er = float(df["calculated_engagement_rate"].mean())
    total_reach = int(df["reach"].sum())
    total_impressions = int(df["impressions"].sum())
    unique_accounts = int(df["account_id"].nunique())
    total_growth = int(df["followers_gained"].sum())
    max_likes_on_photo = int(df["likes"].max())

    kpi_cols = st.columns(8)

    with kpi_cols[0]:
        st.markdown(f"""
        <div class="tableau-kpi-container">
            <div class="tableau-kpi-label">Total Number<br>of Posts</div>
            <div class="tableau-kpi-value orange">{total_posts:,}</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_cols[1]:
        st.markdown(f"""
        <div class="tableau-kpi-container">
            <div class="tableau-kpi-label">Total Likes<br>Received</div>
            <div class="tableau-kpi-value blue">{total_likes/1000:,.0f}k</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_cols[2]:
        st.markdown(f"""
        <div class="tableau-kpi-container">
            <div class="tableau-kpi-label">Total<br>Interactions</div>
            <div class="tableau-kpi-value orange">{total_interactions/1000:,.0f}k</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_cols[3]:
        st.markdown(f"""
        <div class="tableau-kpi-container">
            <div class="tableau-kpi-label">Average<br>Engagement</div>
            <div class="tableau-kpi-value blue">{avg_er*100:.1f}<span class="tableau-kpi-unit">%</span></div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_cols[4]:
        st.markdown(f"""
        <div class="tableau-kpi-container">
            <div class="tableau-kpi-label">Total Content<br>Reach</div>
            <div class="tableau-kpi-value orange">{total_reach/1000000:.1f}<span class="tableau-kpi-unit">M</span></div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_cols[5]:
        st.markdown(f"""
        <div class="tableau-kpi-container">
            <div class="tableau-kpi-label">Total<br>Impressions</div>
            <div class="tableau-kpi-value blue">{total_impressions/1000000:.1f}<span class="tableau-kpi-unit">M</span></div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_cols[6]:
        st.markdown(f"""
        <div class="tableau-kpi-container">
            <div class="tableau-kpi-label">Active Unique<br>Accounts</div>
            <div class="tableau-kpi-value orange">{unique_accounts}</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi_cols[7]:
        st.markdown(f"""
        <div class="tableau-kpi-container">
            <div class="tableau-kpi-label">Followers<br>Gained</div>
            <div class="tableau-kpi-value blue">{total_growth/1000000:.1f}<span class="tableau-kpi-unit">M</span></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr class='tableau-divider'/>", unsafe_allow_html=True)

    # ==========================================
    # ROW 3: TEMPORAL ANALYSIS & BUBBLE CHART
    # Left: Dual-line weekday trend (Muted Blue and Orange)
    # Right: Content Category Packed Bubble Chart
    # ==========================================
    row3_left, row3_right = st.columns([50, 50])

    with row3_left:
        # Weekday Dual Line Chart
        weekday_order = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        w_df = df.groupby("day_of_week").agg(
            avg_likes=("likes", "mean"),
            avg_comments=("comments", "mean"),
            tot_likes=("likes", "sum"),
            tot_comments=("comments", "sum"),
            tot_interactions=("total_interactions", "sum"),
            tot_reach=("reach", "sum")
        ).reindex(weekday_order).reset_index()

        fig_dual_line = go.Figure()

        if weekday_metric_toggle == "Average (Likes vs Comments)":
            y1_series = w_df["avg_likes"]
            y2_series = w_df["avg_comments"]
            y1_name = "Avg. Likes"
            y2_name = "Avg. Comments"
            chart_subtitle = "Average Engagement per Weekday (Likes vs Comments)"
        elif weekday_metric_toggle == "Totals (Likes vs Comments)":
            y1_series = w_df["tot_likes"] / 1000
            y2_series = w_df["tot_comments"] / 1000
            y1_name = "Total Likes (k)"
            y2_name = "Total Comments (k)"
            chart_subtitle = "Total Volume per Weekday (k Likes vs k Comments)"
        else:
            y1_series = w_df["tot_interactions"] / 1000
            y2_series = w_df["tot_reach"] / 10000
            y1_name = "Interactions (k)"
            y2_name = "Reach (10k)"
            chart_subtitle = "Total Interactions vs Scaled Reach per Day"

        # Blue Line (Metric 1)
        fig_dual_line.add_trace(go.Scatter(
            x=w_df["day_of_week"],
            y=y1_series,
            mode="lines+markers+text",
            name=y1_name,
            line=dict(color=MUTED_BLUE, width=2.5),
            marker=dict(size=6, color=MUTED_BLUE),
            text=y1_series.apply(lambda v: f"{v:.1f}" if v < 100 else f"{v:,.0f}"),
            textposition="top center",
            textfont=dict(size=9, family="Inter", color=MUTED_BLUE)
        ))

        # Orange Line (Metric 2)
        fig_dual_line.add_trace(go.Scatter(
            x=w_df["day_of_week"],
            y=y2_series,
            mode="lines+markers+text",
            name=y2_name,
            line=dict(color=ORANGE, width=2.5),
            marker=dict(size=6, color=ORANGE),
            text=y2_series.apply(lambda v: f"{v:.1f}" if v < 100 else f"{v:,.0f}"),
            textposition="bottom center",
            textfont=dict(size=9, family="Inter", color=ORANGE)
        ))

        fig_dual_line.update_layout(
            title=dict(
                text=f"Number of Engagements per Days<br><span style='font-size:10px; color:{MUTED_TEXT};'>{chart_subtitle}</span>",
                font=dict(size=13, family="Inter", color=TEXT_COLOR, weight=600),
                x=0,
                y=0.98
            ),
            plot_bgcolor=WHITE,
            paper_bgcolor=WHITE,
            margin=dict(l=40, r=20, t=50, b=30),
            height=330,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=10, color=TEXT_COLOR)
            ),
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                tickfont=dict(size=10, color=MUTED_TEXT)
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor=LINE_GREY,
                gridwidth=0.5,
                zeroline=False,
                tickfont=dict(size=9, color=MUTED_TEXT)
            )
        )
        st.plotly_chart(fig_dual_line, use_container_width=True, config={"displayModeBar": False})

    with row3_right:
        # Category Engagement Bubble Chart (Packed Cluster Visualization in Tableau Reference Style)
        cat_agg = df.groupby("content_category").agg(
            post_count=("post_id", "count"),
            total_interactions=("total_interactions", "sum"),
            total_reach=("reach", "sum"),
            avg_er=("calculated_engagement_rate", "mean")
        ).reset_index()

        # Sort for deterministic cluster packing
        cat_agg = cat_agg.sort_values(by="total_interactions", ascending=False).reset_index(drop=True)

        if bubble_size_mode == "Total Interactions":
            size_metric = cat_agg["total_interactions"]
            size_label = "Interactions"
        elif bubble_size_mode == "Post Count (Volume)":
            size_metric = cat_agg["post_count"]
            size_label = "Posts"
        else:
            size_metric = cat_agg["total_reach"]
            size_label = "Reach"

        # Generate cluster coordinates (spiral packing algorithm so bubbles form a tight cluster like Tableau)
        n = len(cat_agg)
        angles = np.linspace(0, 2.5 * np.pi, n)
        radii = np.linspace(0.8, 3.2, n)
        x_coords = radii * np.cos(angles)
        y_coords = radii * np.sin(angles)

        # Scale bubble sizes to visually match Tableau reference (approx 45 to 85px)
        norm_sizes = (size_metric - size_metric.min()) / (size_metric.max() - size_metric.min() + 1e-6)
        marker_sizes = 55 + (norm_sizes * 40)

        fig_bubble = go.Figure()

        for idx, row in cat_agg.iterrows():
            c_color = BUBBLE_PALETTE[idx % len(BUBBLE_PALETTE)]
            fig_bubble.add_trace(go.Scatter(
                x=[x_coords[idx]],
                y=[y_coords[idx]],
                mode="markers+text",
                name=row["content_category"],
                marker=dict(
                    size=[marker_sizes[idx]],
                    color=c_color,
                    opacity=0.88,
                    line=dict(width=0)
                ),
                text=[f"<b>{row['content_category'].lower()}</b>"],
                textposition="middle center",
                textfont=dict(size=10, family="Inter", color=WHITE),
                hovertemplate=f"<b>{row['content_category']}</b><br>{size_label}: {size_metric[idx]:,}<br>Avg ER: {row['avg_er']*100:.2f}%<extra></extra>"
            ))

        fig_bubble.update_layout(
            title=dict(
                text="Most Liked & Active Content Categories",
                font=dict(size=13, family="Inter", color=TEXT_COLOR, weight=600),
                x=0,
                y=0.98
            ),
            plot_bgcolor=WHITE,
            paper_bgcolor=WHITE,
            margin=dict(l=10, r=10, t=40, b=10),
            height=330,
            showlegend=False,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
        st.plotly_chart(fig_bubble, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<hr class='tableau-divider'/>", unsafe_allow_html=True)

    # ==========================================
    # ROW 4: CONTENT & TRAFFIC BREAKDOWNS
    # Compact Tableau Visualizations:
    # 1. Media Type (Image vs Carousel vs Reel) Donut Chart
    # 2. Traffic Source Contribution Horizontal Bar
    # 3. Content Category Avg Reach Bar
    # 4. Performance Bucket Distribution Donut Chart
    # ==========================================
    st.markdown(f"<div class='tableau-section-title' style='margin-bottom:8px;'>Content Distribution, Traffic Sourcing & Performance Segmentations</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        # 1. Media Type Donut Chart
        media_agg = df.groupby("media_type")["total_interactions"].sum().reset_index()
        fig_donut_media = go.Figure(go.Pie(
            labels=media_agg["media_type"].str.capitalize(),
            values=media_agg["total_interactions"],
            hole=0.62,
            marker=dict(colors=[ORANGE, MUTED_BLUE, "#7BB8B5"]),
            textinfo="percent",
            textfont=dict(size=10, family="Inter", color=TEXT_COLOR),
            hovertemplate="<b>%{label}</b><br>Interactions: %{value:,}<br>%{percent}<extra></extra>"
        ))
        fig_donut_media.update_layout(
            title=dict(
                text="Engagement by Media Type",
                font=dict(size=12, family="Inter", color=TEXT_COLOR, weight=600),
                x=0.5,
                xanchor="center",
                y=0.95
            ),
            plot_bgcolor=WHITE,
            paper_bgcolor=WHITE,
            margin=dict(l=10, r=10, t=35, b=20),
            height=240,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5, font=dict(size=9))
        )
        st.plotly_chart(fig_donut_media, use_container_width=True, config={"displayModeBar": False})

    with c2:
        # 2. Traffic Source Contribution (Horizontal Bar)
        traffic_agg = df.groupby("traffic_source")["reach"].sum().reset_index().sort_values(by="reach", ascending=True)
        fig_traffic = go.Figure(go.Bar(
            x=traffic_agg["reach"] / 1000000,
            y=traffic_agg["traffic_source"],
            orientation="h",
            marker=dict(color=MUTED_BLUE),
            text=(traffic_agg["reach"] / 1000000).apply(lambda v: f"{v:.1f}M"),
            textposition="outside",
            textfont=dict(size=9, family="Inter", color=TEXT_COLOR),
            cliponaxis=False
        ))
        fig_traffic.update_layout(
            title=dict(
                text="Reach by Traffic Source (M)",
                font=dict(size=12, family="Inter", color=TEXT_COLOR, weight=600),
                x=0,
                y=0.95
            ),
            plot_bgcolor=WHITE,
            paper_bgcolor=WHITE,
            margin=dict(l=65, r=30, t=35, b=20),
            height=240,
            xaxis=dict(showgrid=True, gridcolor=LINE_GREY, gridwidth=0.5, tickfont=dict(size=8, color=MUTED_TEXT)),
            yaxis=dict(showgrid=False, tickfont=dict(size=9, color=TEXT_COLOR))
        )
        st.plotly_chart(fig_traffic, use_container_width=True, config={"displayModeBar": False})

    with c3:
        # 3. Content Category Avg Reach (Horizontal Bar)
        cat_reach = df.groupby("content_category")["reach"].mean().reset_index().sort_values(by="reach", ascending=True)
        fig_cat_reach = go.Figure(go.Bar(
            x=cat_reach["reach"],
            y=cat_reach["content_category"],
            orientation="h",
            marker=dict(color=ORANGE),
            text=cat_reach["reach"].apply(lambda v: f"{v:,.0f}"),
            textposition="outside",
            textfont=dict(size=8, family="Inter", color=TEXT_COLOR),
            cliponaxis=False
        ))
        fig_cat_reach.update_layout(
            title=dict(
                text="Average Reach per Category",
                font=dict(size=12, family="Inter", color=TEXT_COLOR, weight=600),
                x=0,
                y=0.95
            ),
            plot_bgcolor=WHITE,
            paper_bgcolor=WHITE,
            margin=dict(l=75, r=35, t=35, b=20),
            height=240,
            xaxis=dict(showgrid=True, gridcolor=LINE_GREY, gridwidth=0.5, tickfont=dict(size=8, color=MUTED_TEXT)),
            yaxis=dict(showgrid=False, tickfont=dict(size=9, color=TEXT_COLOR))
        )
        st.plotly_chart(fig_cat_reach, use_container_width=True, config={"displayModeBar": False})

    with c4:
        # 4. Performance Bucket Donut Chart
        bucket_agg = df.groupby("performance_bucket_label")["post_id"].count().reset_index()
        fig_bucket_donut = go.Figure(go.Pie(
            labels=bucket_agg["performance_bucket_label"].str.capitalize(),
            values=bucket_agg["post_id"],
            hole=0.62,
            marker=dict(colors=[ORANGE, MUTED_BLUE, "#D99B9B", "#A89F91"]),
            textinfo="percent",
            textfont=dict(size=10, family="Inter", color=TEXT_COLOR),
            hovertemplate="<b>%{label}</b><br>Posts: %{value:,}<br>%{percent}<extra></extra>"
        ))
        fig_bucket_donut.update_layout(
            title=dict(
                text="Performance Bucket Split",
                font=dict(size=12, family="Inter", color=TEXT_COLOR, weight=600),
                x=0.5,
                xanchor="center",
                y=0.95
            ),
            plot_bgcolor=WHITE,
            paper_bgcolor=WHITE,
            margin=dict(l=10, r=10, t=35, b=20),
            height=240,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5, font=dict(size=9))
        )
        st.plotly_chart(fig_bucket_donut, use_container_width=True, config={"displayModeBar": False})

    # ==========================================
    # COLLAPSIBLE DETAIL SECTION: DATA INSPECTOR & EXPORT
    # Clean tabular view allowing full CSV export without cluttering the Tableau layout
    # ==========================================
    with st.expander("🔍 Filtered Data Table & Export (Power BI / Tableau Style Drilldown)", expanded=False):
        c_search, c_dl = st.columns([3, 1])
        with c_search:
            st.caption(f"Currently displaying {len(df):,} matching rows.")
        with c_dl:
            csv_data = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Export Active View (CSV)",
                data=csv_data,
                file_name="instagram_tableau_view.csv",
                mime="text/csv",
                use_container_width=True
            )
        st.dataframe(
            df[["post_id", "account_id", "account_type", "media_type", "content_category", "traffic_source", "post_date", "likes", "comments", "shares", "saves", "reach", "calculated_engagement_rate", "performance_bucket_label"]].head(100),
            use_container_width=True,
            height=250
        )


if __name__ == "__main__":
    main()
