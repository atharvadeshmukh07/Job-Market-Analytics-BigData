# ⚡ Real-Time Job Market Analytics & Skill Demand Prediction Using Big Data Technologies

[![AWS Deployment](https://img.shields.io/badge/AWS_EC2-Live_Server-orange.svg)](http://18.60.142.234:8501/)
[![Streamlit Cloud](https://img.shields.io/badge/Streamlit_Cloud-Live_App-red.svg)](https://job-market-analytics-bigdata.streamlit.app/)
[![PySpark](https://img.shields.io/badge/Apache_Spark-PySpark_4.2-orange.svg)](https://spark.apache.org/)
[![Kafka](https://img.shields.io/badge/Event_Streaming-Apache_Kafka-black.svg)](https://kafka.apache.org/)
[![SQLite/PostgreSQL](https://img.shields.io/badge/Data_Warehouse-PostgreSQL%2FSQLite-blue.svg)](https://www.postgresql.org/)
[![Python](https://img.shields.io/badge/Language-Python_3.14-green.svg)](https://python.org)

---

## 🌐 Live Cloud Deployment Links

- ☁️ **AWS EC2 Server (Live 24/7)**: [http://18.60.142.234:8501/](http://18.60.142.234:8501/)
- 🚀 **Streamlit Cloud App**: [https://job-market-analytics-bigdata.streamlit.app/](https://job-market-analytics-bigdata.streamlit.app/)

---

## 📌 Project Overview & Key Highlights

An end-to-end **Big Data Analytics & Machine Learning Platform** built to ingest, clean, normalize, warehouse, and analyze **92,762+ raw job postings** collected across top recruitment portals (Indeed, LinkedIn, Wellfound, Naukri).

### 🎯 Key Deliverables (Version 3.0 Release):
1. **Data Warehouse Scale (41,091 Clean Jobs)**: Harmonized and deduplicated 92,762 raw stream events into **41,091 clean Indian job listings** in `job_analytics.db`.
2. **Balanced Canonical Role Normalization (502 Roles)**: Multi-stage regex cleaning strips noise (`!!!!!`, `***`, `#`, `[ ]`, job IDs, walk-in dates, experience text, shift info, and location tags), grouping raw titles into exactly **502 clean, standardized canonical roles**.
3. **Curated Role-Skill Tech Matrix**: Dynamic, domain-curated technology stacks mapped to target roles (e.g. *Python Developer* $\rightarrow$ `Python, Django, FastAPI, Flask, PostgreSQL, Docker, Redis, Celery, AWS`).
4. **Machine Learning Salary & Skill Demand Engine**:
   - **Unsupervised K-Means Clustering ($K=8$)**: Imputes estimated CTC compensation for undisclosed salary postings based on TF-IDF skill & role co-occurrences.
   - **Supervised Random Forest Regressor**: Predicts expected LPA CTC salary ranges ($R^2 = 0.82$, Test MAE $\pm 1.85$ LPA) with zero overfitting.
5. **AWS EC2 Production Daemon (Systemd + Cron Auto-Pull)**: Hosted on an AWS EC2 `t3.medium` instance running 24/7 with automatic 5-minute GitHub auto-deployments.

---

## 🤖 Machine Learning Model Evaluation & Overfitting Diagnostics

We evaluated three regression models on 5-fold cross-validated test splits:

| Algorithm | Train MAE (LPA) | Test MAE (LPA) | $R^2$ Variance Score | Overfitting Status | Selection Rationale |
|---|---|---|---|---|---|
| **Random Forest Regressor** 🏆 | **₹1.81 LPA** | **₹1.85 LPA** | **0.82** | **Balanced (Optimal)** | **Selected Winner**: Lowest prediction error, highest accuracy, zero overfitting, and best non-linear feature handling. |
| **Gradient Boosting Regressor** | ₹2.10 LPA | ₹2.18 LPA | 0.76 | Balanced (Optimal) | Runner-up: Strong performance, slightly higher variance error than Random Forest. |
| **Ridge Linear Regression** | ₹2.25 LPA | ₹2.30 LPA | 0.52 | Balanced (Optimal) | Baseline: Underfits complex non-linear tech stack combinations. |

---

## 🏗️ End-to-End System Architecture

```
[ Raw Stream CSV Portals ] 
  ├── indeed_jobs.csv            (12,013)
  ├── jobs.csv                   (30,049)
  ├── master.csv                 (29,104)
  └── naukri_live_jobs (2).csv   (21,596)
          │
          ▼
[ Kafka Event Streaming Producer ] ──> [ kafka_stream_buffer.jsonl (92,762 Events) ]
          │
          ▼
[ PySpark / Pandas Distributed ETL Engine ]
  ├── Schema Normalization & Harmonization
  ├── Indian Location Filtering (Rejects Overseas Postings)
  ├── Salary Package Standardization (INR LPA)
  ├── NLP Skill Co-occurrence Keyword Extractor
  └── Multi-Field Deduplication (raw_job_title + company + clean_city)
          │
          ▼
[ Relational Data Warehouse (job_analytics.db) ]
  ├── dim_jobs                (41,091 Clean Main Jobs Table)
  ├── fact_job_skills         (Exploded Skill-Job Junction Table)
  ├── agg_top_skills          (Skill Demand Frequency Metrics)
  ├── agg_salary_by_title     (Canonical Role Compensation Metrics)
  └── agg_location_analytics  (City Tech Hub Distribution Metrics)
          │
          ▼
[ Analytics, Machine Learning & Interactive UI ]
  ├── Random Forest Salary Predictor (Tab 5)
  ├── Multi-City Tech Hub Analytics (Tab 4)
  ├── Company & Remote Hiring Intelligence (Tab 3)
  └── Streamlit Interactive Dashboard (app.py)
```

---

## 📂 Project Repository Structure

```
├── src/
│   ├── location_cleaner.py  # Indian city/state normalizer & 502 canonical title sanitizer
│   ├── salary_parser.py     # Multi-format salary parser to INR LPA
│   ├── skill_extractor.py   # NLP/Regex tech skill extraction engine
│   ├── unified_schema.py    # Multi-portal schema normalizer
│   ├── kafka_producer.py    # Kafka streaming event producer
│   ├── pyspark_etl.py       # PySpark ETL transformation & warehousing engine
│   └── ml_prediction.py     # Machine Learning K-Means imputation & Random Forest regressor
├── app.py                   # Interactive Streamlit Dashboard application
├── job_analytics.db         # SQLite/PostgreSQL Data Warehouse (41,091 records)
├── requirements.txt         # Python package dependencies
└── README.md                # Technical Documentation & AWS Guide
```

---

## 🚀 How to Run Locally

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Data Ingestion & ETL Data Warehouse Engine
```bash
# Step A: Ingest Stream Events
python -c "from src.kafka_producer import run_ingestion_pipeline; run_ingestion_pipeline()"

# Step B: Execute PySpark ETL Pipeline
python -c "from src.pyspark_etl import run_pyspark_etl; run_pyspark_etl()"
```

### 3. Launch Streamlit Dashboard
```bash
streamlit run app.py
```

---

## 👥 Team & Project Credits
Developed as part of the **CDAC Big Data Analytics Project**.  
- **Lead Developer**: Atharva Deshmukh  
- **Personal Repository**: [https://github.com/atharvadeshmukh07/Job-Market-Analytics-BigData.git](https://github.com/atharvadeshmukh07/Job-Market-Analytics-BigData.git)  
- **Group Repository**: [https://github.com/atharvadeshmukh07/Job-Market-Analytics-BigData-CDAC.git](https://github.com/atharvadeshmukh07/Job-Market-Analytics-BigData-CDAC.git)

