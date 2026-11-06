---
title: Instagram Analytics Dashboard
emoji: 📸
colorFrom: orange
colorTo: blue
sdk: streamlit
sdk_version: 1.41.0
app_file: app.py
pinned: false
license: other
---

# 📸 Instagram User Engagement Analytics & Big Data Visualization Dashboard

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Streamlit-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Visualization](https://img.shields.io/badge/Visualization-Plotly-3F4F75.svg?logo=plotly&logoColor=white)](https://plotly.com/)
[![Storage](https://img.shields.io/badge/Storage-SQLite%20%7C%20Apache%20Parquet-orange.svg)](https://parquet.apache.org/)
[![License](https://img.shields.io/badge/License-Academic%20Evaluation-green.svg)]()

An academic, end-to-end Big Data Analytics and Visualization project analyzing user engagement dynamics, content creative formats, acquisition funnels, and posting schedules across **29,999 records** from an Instagram analytics dataset.

The web application faithfully recreates the minimalist design, typography, compact spacing, and signature color palette (**Orange `#E5933B`** and **Muted Blue `#607FA9`**) of modern enterprise **Tableau Desktop / Power BI** dashboards in pure Python.

---

## 📌 Table of Contents
1. [Project Overview & Objectives](#-project-overview--objectives)
2. [Dataset Profile](#-dataset-profile)
3. [End-to-End Data Lifecycle & Architecture](#-end-to-end-data-lifecycle--architecture)
4. [Data Quality Assessment & Audit](#-data-quality-assessment--audit)
5. [Feature Engineering & Methodological Findings](#-feature-engineering--methodological-findings)
6. [Interactive Dashboard Visual Layout](#-interactive-dashboard-visual-layout)
7. [Statistical Analysis & Key Findings](#-statistical-analysis--key-findings)
8. [Installation & Execution Guide](#-installation--execution-guide)
9. [Presentation & Academic Evaluation Materials](#-presentation--academic-evaluation-materials)
10. [Repository Directory Structure](#-repository-directory-structure)

---

## 🎯 Project Overview & Objectives

In social media growth engineering and content strategy, understanding what drives viewer conversion is critical. This project answers fundamental operational questions:
- **Format Virality:** Which creative format (Image, Reel, Carousel) generates the highest engagement velocity vs absolute reach?
- **Category Conversion:** How do the 10 editorial genres (Photography, Fashion, Tech, Fitness, Food, etc.) compare in performance?
- **Traffic Source Attribution:** How do algorithmic distribution surfaces (Reels Feed, Explore, Hashtags, Profile) amplify reach beyond existing followers?
- **Temporal Sweet Spots:** What are the empirical peak posting hours and optimal day-of-week engagement windows?
- **Follower Count vs. Virality:** Does an account's audience size govern post virality, or does the algorithm reward content resonance?

---

## 📊 Dataset Profile

- **Dataset File:** `Instagram_Analytics.csv`
- **Total Records:** `29,999`
- **Total Features:** `23` original raw columns (expanded to `40` analytical features)
- **Entities:** `20` distinct account IDs
- **Temporal Coverage:** November 2024 to November 2025
- **Aggregate Volume:**
  - **Total Interactions:** `10,593,229` (Likes: `8.63M`, Saves: `1.28M`, Shares: `432K`, Comments: `255K`)
  - **Total Unique Reach:** `188,167,991` accounts
  - **Total Impressions:** `254,000,108` views
  - **Total Followers Gained:** `15,064,082`

---

## 🏗️ End-to-End Data Lifecycle & Architecture

The application implements a production-grade, reproducible data pipeline:

```
┌─────────────────┐       ┌────────────────────────┐       ┌───────────────────────┐
│ Raw Data        │  ───> │ Ingestion & Quality    │  ───> │ Cleaning &            │
│ (CSV untouched) │       │ Audit (reports/*.json) │       │ Schema Sanitization   │
└─────────────────┘       └────────────────────────┘       └───────────────────────┘
                                                                       │
                                                                       ▼
┌───────────────────────────┐      ┌────────────────────────┐      ┌───────────────────────┐
│ Streamlit & Plotly        │ <─── │ Multi-Tier Storage     │ <─── │ Feature Engineering   │
│ Interactive Dashboard UI  │      │ (Parquet, CSV, SQLite) │      │ (14 derived metrics)  │
└───────────────────────────┘      └────────────────────────┘      └───────────────────────┘
```

1. **Ingestion Layer (`src/ingestion.py`):** Loads raw records preserving data immutability.
2. **Quality Assessment Layer (`src/data_quality.py`):** Audits missingness, duplicate keys, relational rules, and IQR bounds.
3. **Cleaning Layer (`src/cleaning.py`):** Harmonizes schema, validates date/weekday consistency, and logs operations into an audit trail.
4. **Transformation Layer (`src/transformation.py`):** Computes rates, ratios, temporal buckets, and cohort brackets.
5. **Storage Layer (`src/database.py`):**
   - **Apache Parquet (`cleaned_data.parquet`):** Columnar format for high-speed dashboard caching.
   - **SQLite Database (`instagram_analytics.db`):** Relational engine with B-Tree indexes and three summary views (`account_summary`, `category_media_summary`, `temporal_engagement_summary`).
   - **Master CSV (`cleaned_data.csv`):** Fully sanitized flat file.

---

## 🔍 Data Quality Assessment & Audit

An automated quality report is generated at [`reports/data_quality_report.json`](reports/data_quality_report.json):
- **Missing Values:** `0` null records across all 23 columns.
- **Duplicate Verification:** `0` duplicate rows; `0` duplicate `post_id`s (100% primary key uniqueness).
- **Relational Integrity:** Confirmed `impressions >= reach` for 100% of rows (no logical violations).
- **Timestamp Harmonization:** Cross-verified `post_date`, `post_hour`, and `day_of_week` against canonical `post_datetime`.
- **Outlier Diagnostics:** Calculated Q1, Q3, and IQR bounds. High-engagement posts represent legitimate viral spikes and are strictly preserved rather than synthetically pruned.

---

## ⚡ Feature Engineering & Methodological Findings

### 1. Engineered Features
- **Total Interactions:** $\text{Interactions} = \text{Likes} + \text{Comments} + \text{Shares} + \text{Saves}$
- **Calculated Engagement Rate (Reach-based):** $\text{ER}_{\text{reach}} = \frac{\text{Total Interactions}}{\text{Reach}}$
- **Impressions-to-Reach Ratio:** $\text{Ratio} = \frac{\text{Impressions}}{\text{Reach}}$ (measures repeat viewing frequency)
- **Engagement per Follower:** $\text{ER}_{\text{follower}} = \frac{\text{Total Interactions}}{\text{Follower Count}}$
- **Temporal Dimensions:** `posting_year`, `posting_month`, `posting_year_month`, `posting_hour`, `posting_weekday`, `is_weekend`
- **Categorical Cohorts:**
  - `hashtag_count_group`: Low (0-4), Medium (5-9), High (10-14), Very High (15+)
  - `follower_count_group`: Emerging (<5K), Growing (5K-15K), Established (15K-30K), Prominent (30K+)

### 2. Methodological Engagement Rate Discovery (Stage 5 Investigation)
In social media analytics, engagement rate is often ambiguous. We performed an empirical correlation analysis between the raw dataset's `engagement_rate` and independent calculations:
- **Correlation with $\frac{\text{Interactions}}{\text{Impressions}}$:** **`0.999999`** (Mean Absolute Error: **`0.000007`**)
- **Correlation with $\frac{\text{Interactions}}{\text{Reach}}$:** `0.975870`

**Conclusion:** The raw dataset used Impressions as its denominator. To maintain academic rigor and digital marketing best practice, both metrics are preserved and selectable across the dashboard.

---

## 🖥️ Interactive Dashboard Visual Layout

The dashboard is modeled after the Tableau reference architecture with a clean white background, `#E5933B` orange, and `#607FA9` muted blue:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ Instagram Clone Data Analysis Dashboard                  [User Post Year: (All) ▼]     │
├──────────────────────────────────────────────────────┬─────────────────────────────────┤
│ ROW 1: Users with the Most Likes (Horizontal Bar)    │ Posts by Most Active Users (Bar)│
│ Top 15 accounts with values at bar ends              │ Top 5 accounts (alternating)    │
├──────────────────────────────────────────────────────┴─────────────────────────────────┤
│ ROW 2: LARGE KPI METRICS (Alternating Orange & Blue, clean typography, 34px)           │
│ [Posts: 29,999] [Likes: 8.6M] [Interactions: 10.6M] [Avg ER: 5.6%] [Reach: 188.2M] ... │
├──────────────────────────────────────────────────────┬─────────────────────────────────┤
│ ROW 3: Number of Engagements per Days (Dual-Line)    │ Most Liked Categories (Bubbles) │
│ Blue: Metric 1 | Orange: Metric 2 with data points   │ Packed organic cluster bubbles  │
├──────────────────────────┬───────────────────────────┼───────────────────┬─────────────┤
│ ROW 4: Media Format      │ Traffic Contribution      │ Category Reach    │ Performance │
│ Donut Chart              │ Horizontal Bar            │ Horizontal Bar    │ Donut Chart │
└──────────────────────────┴───────────────────────────┴───────────────────┴─────────────┘
```

### Key UI Features
- **Hide / Show Filters Toggle:** Top-right button allows collapsing the parameter sidebar completely to expand visualizations to 100% full-screen presentation mode.
- **High-Contrast Readability:** Deep dark slate text (`#0F172A`) against light controls ensures 100% legibility.
- **Drilldown Data Table & CSV Export:** Bottom collapsible drawer allows sorting, pagination, and downloading custom filtered slices.

---

## 📈 Statistical Analysis & Key Findings

1. **Format Effectiveness:**
   - **Reels** achieve the highest engagement efficiency per reached user.
   - **Carousels** generate the highest ratio of **Saves** and **Shares** (evergreen reference material).
   - **Single Images** provide reliable, high-volume baseline likes.
2. **Traffic Funnel Amplification:**
   - **Explore** and **Reels Feed** act as viral distribution surfaces that achieve reach numbers exceeding an account's direct follower count by up to 5x.
   - **Home Feed** delivers the highest conversion of repeat engagements.
3. **Audience Size vs. Engagement Rate:**
   - Pearson correlation is weak ($r \approx 0.05$), proving that platform algorithms prioritize immediate viewer watch/read time and interaction velocity over raw follower count.
4. **Call to Action (CTA) Impact:**
   - Two-sample independent t-test confirms a statistically significant increase in comments and saves on posts with an explicit prompt ($p < 0.05$).

---

## 🚀 Installation & Execution Guide

### 1. Clone the Repository
```bash
git clone https://github.com/sa1165/Instagram-Analytics.git
cd Instagram-Analytics
```

### 2. Set Up Virtual Environment & Dependencies
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Run the Automated ETL Pipeline
```bash
python -m src.etl_pipeline
```
*Extracts raw CSV, validates schema, cleans data, engineers features, and populates SQLite and Parquet stores.*

### 4. Run the Unit & Integration Test Suite
```bash
python -m unittest tests/test_pipeline.py
```
*(All 5 pipeline and data integrity tests pass with `OK` status)*

### 5. Launch the Streamlit Web Dashboard
```bash
streamlit run app.py
```
Open **[http://localhost:8501](http://localhost:8501)** in your web browser.

---

## 🎓 Presentation & Academic Evaluation Materials

A companion PowerPoint presentation has been generated in the project root:
- **File:** [`Instagram_Analytics_Presentation.pptx`](Instagram_Analytics_Presentation.pptx)
- **Structure:** 10 widescreen (16:9) slides styled with Tableau Orange and Muted Blue, covering Project Objectives, Dataset Architecture, ETL, Feature Engineering, Denominator Analysis, Statistical Findings, and UI Architecture.

---

## 📂 Repository Directory Structure

```text
Instagram-Analytics/
│
├── data/
│   ├── raw/
│   │   └── Instagram_Analytics.csv             # Untouched raw dataset (29,999 rows)
│   └── processed/
│       ├── cleaned_data.csv                    # Cleaned & feature-engineered master CSV
│       └── cleaned_data.parquet                # High-speed columnar Parquet file
│
├── database/
│   └── instagram_analytics.db                  # SQLite database with indexed summary views
│
├── src/
│   ├── ingestion.py                            # Raw data loader & schema validation
│   ├── data_quality.py                         # Quality assessment suite (nulls, duplicates, IQR)
│   ├── cleaning.py                             # Cleaning operations & audit trail generator
│   ├── transformation.py                       # Feature engineering & denominator research
│   ├── database.py                             # SQLite persistence & indexed view creation
│   ├── etl_pipeline.py                         # End-to-end reproducible orchestrator
│   ├── eda.py                                  # Core exploratory analytics & statistical tests
│   └── insights.py                             # Dynamic factual insights synthesizer
│
├── dashboard/
│   ├── overview.py                             # Executive overview & high-level trajectories
│   ├── account_analytics.py                    # Account benchmarking & brand vs creator analysis
│   ├── content_analytics.py                    # Creative format & content vertical analytics
│   ├── time_analytics.py                       # 24-hour distribution & weekday heatmaps
│   ├── engagement_analytics.py                 # Traffic channel attribution & correlation matrix
│   ├── data_explorer.py                        # Granular search, filter, and CSV export drawer
│   └── insights_page.py                        # Automated findings & academic report blueprint
│
├── reports/
│   ├── data_quality_report.json                # Automated raw data quality audit findings
│   ├── cleaning_audit.json                     # Data cleaning operational log
│   └── analytical_summary.json                 # Summary metrics and denominator comparison results
│
├── tests/
│   └── test_pipeline.py                        # Automated test suite (ingestion, quality, ETL, db)
│
├── app.py                                      # Main Streamlit web application (Tableau layout)
├── Instagram_Analytics_Presentation.pptx        # 10-slide academic project presentation deck
├── requirements.txt                            # Dependencies (streamlit, plotly, pandas, etc.)
├── .gitignore                                  # Git exclusion configuration
└── README.md                                   # Comprehensive academic documentation
```

---

## 👥 Author
- **Academic Project:** Big Data Visualization & Business Analytics
- **GitHub Repository:** [https://github.com/sa1165/Instagram-Analytics](https://github.com/sa1165/Instagram-Analytics)
