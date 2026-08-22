# 🏛️ Smart Civic Issue Analytics & Predictive Dispatcher

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white)](https://scikit-learn.org/)
[![SQL](https://img.shields.io/badge/SQL-MySQL%20%7C%20SQLite-00758F?style=for-the-badge&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Power BI](https://img.shields.io/badge/Power_BI-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)](https://powerbi.microsoft.com/)
[![Tests](https://img.shields.io/badge/Pytest-Passing%20100%25-brightgreen?style=for-the-badge&logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)

> An enterprise-grade, end-to-end municipal intelligence, predictive dispatching, and geospatial analytics platform. Designed to monitor civic health, optimize municipal resource allocation, predict SLA breach risks at ticket registration, and enhance citizen satisfaction.

---

## 📌 Power BI & Web Dashboard Previews

<div align="center">
  <img width="900" alt="Power BI Executive Dashboard" src="Screenshots/Screenshot 2026-08-02 232659.png" />
  <p><em>Figure 1: Executive KPI & Geospatial Incident Dashboard (Power BI Desktop Report)</em></p>
  <img width="900" alt="Departmental Deep Dive" src="Screenshots/Screenshot 2026-08-02 232828.png" />
  <p><em>Figure 2: Departmental Turnaround & Priority Distribution Analysis</em></p>
</div>

---

## 🚀 Key Technical Highlights & Capabilities

- 🤖 **Predictive SLA Breach Classifier (Random Forest & Gradient Boosting):** Accurately classifies whether an incoming civic ticket will breach the 3-day SLA threshold at the time of lodging (**F1-Score: 0.77**, Test Accuracy: **64.2%**).
- ⏱️ **Resolution Turnaround Estimator:** Supervised regressor forecasting repair duration (MAE: 2.4 days) to dynamically set expectations for citizens and dispatchers.
- 🗺️ **Geospatial GIS & DBSCAN Hotspot Clustering:** Detects chronic infrastructure failure zones across municipal coordinates using Haversine distance clustering, identifying recurring pothole corridors and drainage blockages.
- 💻 **Interactive Multi-Page Streamlit Web App:** 6 interactive modules with live filters, interactive Plotly charts, GIS heatmaps, an AI predictive sandbox, and an in-browser SQL query lab.
- 🗄️ **Advanced SQL Analytics Suite:** Enterprise Star Schema (`fact_complaints`, dimension tables) and 15+ complex SQL analytics using Window Functions (`DENSE_RANK()`, `NTILE()`, `LAG()`, `ROWS BETWEEN 6 PRECEDING AND CURRENT ROW`).
- 🛡️ **Automated Data Quality & Validation Engine:** 10-point schema profiler, anomaly detection (negative turnaround prevention, GPS bounding validation), and automated audit reporting.
- 🧪 **Pytest Automated Test Suite:** 100% passing test coverage across data cleaners, feature calculations, ML inference pipelines, and database connectivity.

---

## 🏗️ System Architecture

```mermaid
flowchart LR
    A[Raw Civic Complaints Excel/CSV] --> B[Data Validator & Quality Profiler]
    B --> C[Data Cleaner & Imputer]
    C --> D[Feature Engineering 25+ Features]
    D --> E[(Analytical DB - SQLite/MySQL)]
    D --> F[ML Predictive Engine]
    
    subgraph Machine Learning
        F1[SLA Breach Classifier]
        F2[Turnaround Estimator]
        F3[DBSCAN GIS Hotspots]
    end
    
    F --> G[Interactive Streamlit Dashboard]
    E --> G
    E --> H[Power BI Desktop Report]
```

---

## 📂 Project Structure

```
Smart-Civic-Issue-Analytics/
│
├── data/
│   ├── raw/                             # Raw municipal dataset (Excel/CSV)
│   ├── cleaned/                         # Cleaned, standardized CSV
│   ├── feature_engineered/              # 25+ engineered feature set
│   └── database/                        # Embedded SQLite analytical database
│
├── src/                                 # Modular Python Engineering Package
│   ├── core/                            # Configuration, logging, DB connection
│   │   ├── config.py
│   │   ├── logger.py
│   │   └── db.py
│   ├── data/                            # Ingestion, validation & cleaning
│   │   ├── loader.py
│   │   ├── cleaner.py
│   │   └── validator.py                 # Automated data quality profiler
│   ├── features/                        # Feature engineering pipeline
│   │   └── engineer.py
│   ├── models/                          # ML Training, inference & evaluation
│   │   ├── sla_predictor.py             # Random Forest SLA classifier
│   │   ├── resolution_estimator.py      # Turnaround regressor
│   │   └── cluster_analyzer.py          # DBSCAN geospatial clustering
│   └── analytics/                       # KPI engines & time series
│       ├── kpis.py
│       └── time_series.py
│
├── dashboard/                           # Multi-Page Streamlit Application
│   ├── app.py                           # Command Center & navigation
│   ├── utils.py                         # UI styles and cached loaders
│   └── pages/
│       ├── 1_Executive_Overview.py      # Macro KPIs, SLA rates, trends
│       ├── 2_Geospatial_Explorer.py     # Interactive Folium heatmaps & GIS
│       ├── 3_Department_DeepDive.py     # Turnaround boxplots & officer scorecards
│       ├── 4_AI_Predictive_Studio.py    # Real-time ML risk inference simulator
│       ├── 5_Citizen_Sentiment.py       # Satisfaction drivers & rating analytics
│       └── 6_SQL_Analytics_Lab.py       # Live in-browser SQL query lab
│
├── sql/
│   ├── schema_and_views.sql             # Star schema, indexes, reporting views
│   ├── advanced_analytics.sql           # CTEs, Window functions, rolling averages
│   └── database.sql                     # Upgraded legacy SQL script
│
├── powerbi/
│   ├── complaints.pbix                  # Interactive Power BI Desktop report
│   └── DAX_Measures_Reference.md        # Documented DAX measures for interviews
│
├── docs/                                # Placement & Portfolio Toolkit
│   ├── INTERVIEW_PREP_GUIDE.md          # 20+ STAR-method placement Q&A
│   ├── RESUME_POINTS.md                 # Metric-backed resume bullet points
│   └── PORTFOLIO_CASE_STUDY.md          # Executive case study
│
├── tests/                               # Pytest Unit Test Suite
│   ├── test_cleaner.py
│   ├── test_features.py
│   ├── test_models.py
│   └── test_db.py
│
├── .env.example                         # Environment configuration template
├── run_pipeline.py                      # Master automated CLI pipeline
├── requirements.txt                     # Dependency specifications
└── README.md                            # Project documentation
```

---

## ⚡ Quickstart & Installation

### 1. Clone & Set Up Environment
```bash
git clone https://github.com/your-username/Smart-Civic-Issue-Analytics.git
cd Smart-Civic-Issue-Analytics

# Create virtual environment (optional)
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the End-to-End Pipeline
Execute data validation, cleaning, feature engineering, ML model training, and database seeding in one command:
```bash
python run_pipeline.py
```

### 3. Launch the Interactive Web Dashboard
```bash
streamlit run dashboard/app.py
```

### 4. Run Automated Test Suite
```bash
python -m pytest tests/ -v
```

---

## 🎯 Placement & Interview Resources

Check out the dedicated documentation created for job interviews and portfolio presentations:
- 📖 [**Placement & Interview Prep Guide**](docs/INTERVIEW_PREP_GUIDE.md): 20+ technical and behavioral questions answered with the STAR framework.
- 📄 [**Resume-Ready Bullet Points**](docs/RESUME_POINTS.md): Action-oriented, metric-driven bullet points tailored for Data Analyst, BI, and Data Science roles.
- 📊 [**DAX Measures Reference**](powerbi/DAX_Measures_Reference.md): Complete breakdown of DAX calculations used in the Power BI dashboard.
- 📑 [**Portfolio Case Study**](docs/PORTFOLIO_CASE_STUDY.md): In-depth case study suitable for portfolio websites and LinkedIn.

---

## 👩‍💻 Author & Contact

**Garima Raj**  
B.Tech CSE (Data Science) | Heritage Institute of Technology  
*Specializing in Data Analytics, Business Intelligence & Applied Machine Learning*

---

## 📄 License
This project is open-source under the [MIT License](LICENSE).
