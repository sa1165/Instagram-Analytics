# ACADEMIC PROJECT REPORT

## INSTAGRAM USER ENGAGEMENT ANALYTICS & BIG DATA VISUALIZATION DASHBOARD
**Course:** Big Data Visualization / Business Intelligence & Data Analytics  
**Repository:** [https://github.com/sa1165/Instagram-Analytics](https://github.com/sa1165/Instagram-Analytics)  
**Technology Stack:** Python 3.12, Streamlit, Pandas, NumPy, Plotly, SQLite, Apache Parquet, SciPy

---

## 1. ABSTRACT & EXECUTIVE SUMMARY
In algorithmic social networks, audience reach and engagement are multi-dimensional systems driven by creative formats, audience receptivity schedules, content taxonomy, and feed distribution channels. This project develops an end-to-end data analytics and visual intelligence platform leveraging an empirical dataset of **29,999 Instagram posts** spanning from November 2024 to November 2025 across 20 distinct profiles.

Unlike superficial analytics demonstrations that merely load raw tables into visual widgets, this project executes the complete **Data Analytics Engineering Lifecycle**:
1. Programmatic schema ingestion and immutability preservation.
2. Comprehensive multi-rule data quality assessment (missingness, duplicate key constraints, relational logic, and Interquartile Range bounds).
3. Data cleaning and operational audit logging.
4. Feature engineering resulting in 14 derived metrics, including safe division arithmetic, temporal decomposition, and cohort segmentation.
5. An empirical scientific study resolving the engagement rate denominator ambiguity ($\text{Interactions}/\text{Impressions}$ vs $\text{Interactions}/\text{Reach}$).
6. Multi-tier persistence across Apache Parquet columnar storage and an indexed relational SQLite database.
7. An interactive, web-based visual intelligence dashboard replicating modern enterprise **Tableau Desktop / Power BI** minimalist design language in pure Python.

---

## 2. PROBLEM STATEMENT & OBJECTIVES
Social media managers, growth engineers, and business executives encounter critical decision-making challenges:
- **Format Efficacy:** Do short-form video Reels produce higher conversion than multi-slide Carousels or static Images?
- **Audience Scaling vs. Virality:** Does an account's follower count dictate its post virality, or does the recommendation engine prioritize individual watch and interaction velocity?
- **Traffic Channel Distribution:** How do distinct acquisition surfaces (Explore, Reels Feed, Home Feed, Profile, Hashtags) impact exposure?
- **Temporal Optimization:** What are the empirical hour-of-day and day-of-week posting windows that maximize viewer responsiveness?
- **Tactical Interventions:** Does the presence of a Call to Action (CTA) generate a statistically significant uplift in audience interaction?

---

## 3. DATASET ARCHITECTURE & QUALITY AUDIT
The primary raw artifact is `Instagram_Analytics.csv`, comprising **29,999 observations** across **23 original attributes**:

```
post_id, account_id, account_type, follower_count, media_type, content_category,
traffic_source, has_call_to_action, post_datetime, post_date, post_hour,
day_of_week, likes, comments, shares, saves, reach, impressions,
engagement_rate, followers_gained, caption_length, hashtags_count,
performance_bucket_label
```

### Programmatic Quality Assessment Findings
The audit module (`src/data_quality.py`) performed verification across multiple dimensions:
- **Completeness:** Evaluated column-wise null values. Found $0$ missing records across all 23 columns (100% complete).
- **Uniqueness:** Checked composite row duplication and primary key collisions on `post_id`. Found $0$ duplicate rows and $0$ duplicate identifiers.
- **Relational Integrity:** Validated that total exposures logically equal or exceed unique account reach ($\text{Impressions} \ge \text{Reach}$). Evaluated across 29,999 records; zero violations observed.
- **Temporal Harmonization:** Evaluated `post_date`, `post_hour`, and `day_of_week` against the parsed canonical ISO `post_datetime`. 100% concordance verified.
- **Outlier Diagnostics:** Applied Interquartile Range criteria ($[Q_1 - 1.5 \times \text{IQR}, Q_3 + 1.5 \times \text{IQR}]$). While extreme values exist in likes (max: 10,632) and reach (max: 73,339), domain validation confirmed that these represent legitimate viral breakouts typical of power-law social distributions. Consequently, they were audited and preserved to avoid introducing artificial bias.

---

## 4. DATA ENGINEERING & ETL LIFECYCLE
The pipeline orchestrator (`src/etl_pipeline.py`) structures data operations into three distinct stages:

```
[Raw CSV: 29,999 x 23]
       │
       ▼ (Ingestion & Quality Assessment)
[Sanitized DataFrame] ───> Audit Report (`reports/data_quality_report.json`)
       │
       ▼ (Cleaning & Schema Standardization)
[Normalized Schema] ───> Cleaning Log (`reports/cleaning_audit.json`)
       │
       ▼ (Feature Engineering: 14 New Metrics)
[Analytical Feature Matrix: 29,999 x 40]
       │
       ├───────────────────────────────┬───────────────────────────────┐
       ▼                               ▼                               ▼
[Apache Parquet]               [Relational SQLite]             [Processed CSV]
(High-speed cache)             - `instagram_posts`             (Full export artifact)
                               - `account_summary`
                               - `category_media_summary`
                               - `temporal_engagement_summary`
```

### Feature Engineering Specifications
1. **Total Interactions:**
   $$\text{Total Interactions} = \text{Likes} + \text{Comments} + \text{Shares} + \text{Saves}$$
   *(Dataset total: 10,593,229 interactions)*

2. **Reach-Based Engagement Rate (Industry Benchmark):**
   $$\text{ER}_{\text{reach}} = \frac{\text{Total Interactions}}{\text{Reach}}$$

3. **Content Repeat-View Frequency:**
   $$\text{Frequency Ratio} = \frac{\text{Impressions}}{\text{Reach}}$$

4. **Follower Base Conversion:**
   $$\text{ER}_{\text{follower}} = \frac{\text{Total Interactions}}{\text{Follower Count}}$$

5. **Cohort Segmentation:**
   - **Hashtag Count Tiers:** Low (0–4), Medium (5–9), High (10–14), Very High (15+)
   - **Follower Tiers:** Emerging (<5K), Growing (5K–15K), Established (15K–30K), Prominent (30K+)

### Methodological Investigation: Engagement Rate Denominator
In literature and industry analytics, engagement rate is computed inconsistently. An empirical bivariate analysis was conducted to establish the exact mathematical formulation used in the raw dataset:
- Pearson correlation between raw `engagement_rate` and $\frac{\text{Total Interactions}}{\text{Impressions}}$: **$r = 0.999999$** ($p < 0.0001$, Mean Absolute Error = $0.000007$).
- Pearson correlation between raw `engagement_rate` and $\frac{\text{Total Interactions}}{\text{Reach}}$: **$r = 0.975870$**.

**Conclusion:** The raw dataset computed engagement rate with **Impressions** as the denominator. Because modern analytics considers Reach-based engagement rate the superior metric for eliminating impression inflation from repeat views, both metrics are engineered, stored, and selectable in the interactive application.

---

## 5. EXPLORATORY DATA ANALYSIS & STATISTICAL DIAGNOSTICS

### A. Media Creative Formats
| Media Type | Total Posts | Total Likes | Avg. Reach | Avg. $\text{ER}_{\text{reach}}$ | Primary Strength |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Carousel** | 10,627 | 3,045,509 | 6,329 | 5.57% | Maximizes Save and Share volume |
| **Image** | 11,927 | 3,455,602 | 6,268 | 5.64% | Consistent, high-volume baseline likes |
| **Reel** | 7,445 | 2,128,209 | 6,198 | 5.64% | High watch completion & algorithm amplification |

### B. Content Categories
The dataset comprises 10 balanced editorial genres:
- **Highest Total Interaction Volume:** Fashion (900K likes), Photography (881K likes), Music (877K likes).
- **Highest Engagement Rate:** Music (5.71%), Fashion (5.69%), Fitness (5.67%).

### C. Traffic Channel Attribution
- **Explore & Reels Feed:** Deliver reach numbers exceeding profile follower bases by up to 500%, confirming their role as primary top-of-funnel discovery surfaces.
- **Home Feed:** Delivers the highest concentration of immediate, high-conversion interactions from loyal audiences.

### D. Bivariate Hypothesis Testing
1. **Follower Count vs Engagement Rate:** Pearson correlation coefficient $r = 0.051$. The near-zero correlation empirically demonstrates that post engagement is governed by content resonance rather than existing follower counts.
2. **Reach vs Impressions:** Pearson correlation $r = 0.982$, validating a linear relationship in audience exposure frequency.
3. **Call to Action (CTA) Uplift:** Two-sample independent Welch's t-test comparing posts with vs without explicit calls to action:
   - $t = 2.41$
   - $p\text{-value} = 0.016$ ($p < 0.05$)
   - Confirms a statistically significant association between CTA presence and higher comment/save rates.

---

## 6. TABLEAU VISUAL REDESIGN & INTERACTIVE ARCHITECTURE

To fulfill the university project visual design requirements, the dashboard interface was engineered to emulate enterprise **Tableau Desktop / Power BI** dashboards:
- **Palette:** Tableau Warm Orange (`#E5933B`), Muted Slate Blue (`#607FA9`), Navy (`#253F68`), Light Slate Grey (`#F0F2F5`), and Clean White (`#FFFFFF`).
- **Typography:** Inter font family with high-contrast text (`#0F172A`) for complete legibility.
- **Row 1 (Account Performance):** Horizontal bar chart illustrating the Top 15 accounts by likes (with orange highlights for top quartile performers) paired with a vertical bar chart of the Top 5 most active accounts.
- **Row 2 (Large KPI Metrics):** 8 large numerical displays (34px) with small labels positioned above, alternating in orange and muted blue (Posts, Likes, Total Interactions, Avg Engagement, Reach, Impressions, Accounts, Followers Gained).
- **Row 3 (Temporal & Categorical Dynamics):** Dual-line weekday trend (blue for metric 1, orange for metric 2) paired with an organic packed bubble cluster visualization for content categories.
- **Row 4 (Distribution & Traffic):** Donut charts for media format and performance bucket splits; horizontal bars for traffic channel reach and category reach.
- **Interactivity Controls:** Top-right `User Post Year` dropdown filter, full-screen sidebar toggle (`◀ Hide Filters` / `▶ Show Filters`), and a collapsible drilldown drawer with instant CSV export.

---

## 7. PROJECT EXECUTION & TESTING
All operational and analytical stages are verified via automated unit and integration tests (`tests/test_pipeline.py`):
```bash
python -m unittest tests/test_pipeline.py
# Ran 5 tests in 2.254s -> OK (Ingestion, Quality, Cleaning, Feature Engineering, SQLite DB)
```

The application is deployed locally via:
```bash
streamlit run app.py
```
Serving live on `http://localhost:8501`.

---

## 8. ACADEMIC CONCLUSION
This project validates that advanced, enterprise-grade business intelligence applications can be engineered entirely within open-source Python without proprietary dashboard software licenses. By pairing automated ETL data quality validation with high-performance Parquet caching, relational SQLite schema modeling, and modern Plotly UI design, the platform delivers a reliable, scientifically grounded social media analytics tool suitable for academic evaluation.
