# ⚡ Real-Time Job Market Analytics & Skill Demand Prediction Using Big Data Technologies

[![PySpark](https://img.shields.io/badge/Apache_Spark-PySpark_4.2-orange.svg)](https://spark.apache.org/)
[![Kafka](https://img.shields.io/badge/Event_Streaming-Apache_Kafka-black.svg)](https://kafka.apache.org/)
[![PostgreSQL](https://img.shields.io/badge/Data_Warehouse-PostgreSQL-blue.svg)](https://www.postgresql.org/)
[![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-red.svg)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Language-Python_3.14-green.svg)](https://python.org)

## 📌 Project Overview
An end-to-end Big Data analytics & machine learning platform built to ingest, clean, normalize, and analyze **92,760+ raw job postings** collected from multiple portals (Indeed, LinkedIn, Wellfound, Naukri).

The platform handles real-world data engineering challenges:
- **Divergent Schemas**: Harmonizes 4 different portal structures into a single unified schema.
- **Location Normalization**: Filters out foreign/overseas listings and standardizes Indian tech hubs (Bengaluru, Hyderabad, Pune, Mumbai, Delhi NCR, Chennai, Remote India).
- **Salary Standardization**: Normalizes diverse text formats (`10 LPA`, `₹3,00,000 - ₹4,80,000`, `$120k`, `50,000/month`) into uniform Min/Max/Avg INR LPA metrics.
- **Skill Extraction (NLP)**: Regex & keyword extraction engine identifies technical skills (`PySpark`, `Kafka`, `Python`, `SQL`, `AWS`, `Docker`, `React`, `Machine Learning`).

---

## 🏗️ System Architecture Flow

```
[ Raw CSV Portals ]
  ├── indeed_jobs.csv  (12,013)
  ├── jobs.csv         (30,049)
  ├── master.csv       (29,104)
  └── naukri_jobs.csv  (21,596)
          │
          ▼
[ Kafka Event Producer ] ──> [ Kafka Topic: raw_job_postings ]
          │
          ▼
[ PySpark Distributed ETL Engine ]
  ├── Schema Normalization & Harmonization
  ├── Indian Location Filtering (Rejects Foreign Records)
  ├── Salary Standardization (INR LPA)
  ├── Skill Keyword Extraction (NLP)
  └── Cross-Platform Deduplication
          │
          ▼
[ Relational Data Warehouse (PostgreSQL / SQLite) ]
  ├── dim_jobs                (Clean Main Jobs Table)
  ├── fact_job_skills         (Exploded Skill-Job Junction)
  ├── agg_top_skills          (Skill Demand Frequencies)
  ├── agg_salary_by_title     (Role Salary Metrics)
  └── agg_location_analytics  (City Distribution Metrics)
          │
          ▼
[ Analytics, ML & Interactive Dashboard ]
  ├── Machine Learning Skill Demand & Salary Predictor
  └── Streamlit Interactive Dashboard
```

---

## 📂 Repository Structure

```
├── src/
│   ├── location_cleaner.py  # Indian cities/states mapping & foreign location filter
│   ├── salary_parser.py     # Multi-format salary parser to INR LPA
│   ├── skill_extractor.py   # NLP/Regex tech skill extraction engine
│   ├── unified_schema.py    # Multi-portal schema normalizer
│   ├── kafka_producer.py    # Kafka streaming event producer
│   ├── pyspark_etl.py       # PySpark ETL transformation & warehousing engine
│   └── ml_prediction.py     # Machine Learning skill demand & salary model
├── app.py                   # Interactive Streamlit Dashboard application
├── requirements.txt         # Project dependencies
└── README.md                # Technical Documentation
```

---

## 🚀 How to Run the Project

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Ingest Data via Kafka Producer
```bash
python src/kafka_producer.py
```

### 3. Run PySpark ETL Engine & Load Data Warehouse
```bash
python src/pyspark_etl.py
```

### 4. Launch Streamlit Analytics Dashboard
```bash
streamlit run app.py
```

---

## 👥 Team Members
Developed as part of the CDAC Big Data Analytics Project.
