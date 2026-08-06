import os
import sys
import json
import sqlite3
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Fallback PySpark or Pandas PySpark Engine
try:
    from pyspark.sql import SparkSession
    from pyspark.sql import functions as F
    from pyspark.sql.types import (
        StructType, StructField, StringType, DoubleType, BooleanType, ArrayType
    )
    SPARK_AVAILABLE = True
except ImportError:
    SPARK_AVAILABLE = False

DB_NAME = "job_analytics.db"

def get_spark_session(max_retries=3):
    """
    Initializes a PySpark SparkSession with automatic JVM Gateway retry guard
    to catch and recover from JAVA_GATEWAY_EXITED or Py4J errors.
    """
    import time
    for attempt in range(1, max_retries + 1):
        try:
            try:
                active_spark = SparkSession.getActiveSession()
                if active_spark:
                    active_spark.stop()
            except Exception:
                pass

            spark = SparkSession.builder \
                .appName("JobMarketAnalytics") \
                .config("spark.driver.memory", "4g") \
                .config("spark.sql.shuffle.partitions", "8") \
                .getOrCreate()
            return spark
        except Exception as e:
            print(f"[PySpark Gateway Guard] Attempt {attempt}/{max_retries} failed: {e}")
            time.sleep(2)
            if attempt == max_retries:
                raise e

def run_pyspark_etl(input_buffer_file="kafka_stream_buffer.jsonl"):
    print("==================================================")
    print("      PYSPARK BIG DATA ETL & ANALYTICS ENGINE      ")
    print("==================================================")

    if not os.path.exists(input_buffer_file):
        print(f"[PySpark Error] Input stream buffer '{input_buffer_file}' not found. Run ingestion first!")
        return False

    print(f"[PySpark ETL] Loading raw stream data from '{input_buffer_file}'...")

    use_pyspark = False
    if SPARK_AVAILABLE:
        try:
            print("[PySpark Engine] Initializing PySpark Session with JVM Gateway Retry Guard...")
            spark = get_spark_session()

            schema = StructType([
                StructField("source_portal", StringType(), True),
                StructField("raw_job_title", StringType(), True),
                StructField("clean_job_title", StringType(), True),
                StructField("company", StringType(), True),
                StructField("raw_location", StringType(), True),
                StructField("clean_city", StringType(), True),
                StructField("clean_state", StringType(), True),
                StructField("is_indian_location", BooleanType(), True),
                StructField("is_remote", BooleanType(), True),
                StructField("raw_salary", StringType(), True),
                StructField("min_salary_lpa", DoubleType(), True),
                StructField("max_salary_lpa", DoubleType(), True),
                StructField("avg_salary_lpa", DoubleType(), True),
                StructField("job_description", StringType(), True),
                StructField("extracted_skills", ArrayType(StringType()), True),
                StructField("job_url", StringType(), True)
            ])

            # Read JSON into Spark DataFrame
            df_raw = spark.read.schema(schema).json(input_buffer_file)
            raw_count = df_raw.count()
            print(f"  --> Total raw stream events ingested: {raw_count}")

            # Transformation 1: Filter strictly for Indian Cities / States
            df_india = df_raw.filter(F.col("is_indian_location") == True)
            india_count = df_india.count()
            print(f"  --> Filtered Indian job postings: {india_count} (Dropped {raw_count - india_count} non-Indian/foreign records)")

            # Transformation 2: Deduplication across platforms (Deduplicate by raw_job_title + company + city)
            df_clean = df_india.dropDuplicates(["raw_job_title", "company", "clean_city"])
            clean_count = df_clean.count()
            print(f"  --> Deduplicated clean jobs: {clean_count} (Removed {india_count - clean_count} duplicate postings)")

            # Convert to Pandas for SQL / SQLite storage
            pdf_clean = df_clean.toPandas()
            use_pyspark = True
        except Exception as spark_err:
            print(f"[PySpark Notice] PySpark JVM is not available on this environment ({spark_err}). Switching seamlessly to Pandas Big Data Ingestion Engine...")
            use_pyspark = False

    if not use_pyspark:
        print("[PySpark Fallback Engine] Using Pandas Engine for Big Data ETL processing...")
        records = []
        with open(input_buffer_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
        
        pdf_raw = pd.DataFrame(records)
        raw_count = len(pdf_raw)
        print(f"  --> Total raw stream events ingested: {raw_count}")

        pdf_india = pdf_raw[pdf_raw['is_indian_location'] == True]
        india_count = len(pdf_india)
        print(f"  --> Filtered Indian job postings: {india_count}")

        pdf_clean = pdf_india.drop_duplicates(subset=['raw_job_title', 'company', 'clean_city'])
        clean_count = len(pdf_clean)
        print(f"  --> Deduplicated clean jobs: {clean_count}")

    from src.location_cleaner import sanitize_job_title_for_ui
    
    # Apply clean title sanitizer to produce thousands of clean role titles
    pdf_clean['clean_job_title'] = pdf_clean['raw_job_title'].apply(sanitize_job_title_for_ui)

    # Prepare PostgreSQL / SQLite Analytical Tables
    print("\n[Data Warehouse] Saving clean analytical tables to SQLite/PostgreSQL Database...")
    conn = sqlite3.connect(DB_NAME)

    # 1. Main Cleaned Jobs Table
    pdf_jobs_table = pdf_clean.copy()
    pdf_jobs_table['skills_str'] = pdf_jobs_table['extracted_skills'].apply(lambda x: ", ".join(x) if isinstance(x, list) else "")
    pdf_jobs_table.drop(columns=['extracted_skills'], inplace=True, errors='ignore')
    pdf_jobs_table.to_sql("dim_jobs", conn, if_exists="replace", index=False)

    # 2. Exploded Skill Analytics Table (fact_job_skills)
    skill_rows = []
    for _, row in pdf_clean.iterrows():
        skills = row['extracted_skills']
        if isinstance(skills, (list, tuple)) or (hasattr(skills, '__iter__') and not isinstance(skills, str)):
            for sk in skills:
                if isinstance(sk, str) and sk.strip():
                    skill_rows.append({
                        'clean_job_title': row['clean_job_title'],
                        'company': row['company'],
                        'clean_city': row['clean_city'],
                        'avg_salary_lpa': row['avg_salary_lpa'],
                        'skill_name': sk.strip()
                    })
    
    pdf_skills = pd.DataFrame(skill_rows, columns=['clean_job_title', 'company', 'clean_city', 'avg_salary_lpa', 'skill_name'])
    if not pdf_skills.empty:
        pdf_skills.to_sql("fact_job_skills", conn, if_exists="replace", index=False)

        # 3. Top Skills Aggregation
        skill_counts = pdf_skills['skill_name'].value_counts().reset_index()
        skill_counts.columns = ['skill_name', 'job_demand_count']
        skill_counts['demand_percentage'] = round((skill_counts['job_demand_count'] / max(clean_count, 1)) * 100, 2)
        skill_counts.to_sql("agg_top_skills", conn, if_exists="replace", index=False)
    else:
        pd.DataFrame(columns=['clean_job_title', 'company', 'clean_city', 'avg_salary_lpa', 'skill_name']).to_sql("fact_job_skills", conn, if_exists="replace", index=False)
        pd.DataFrame(columns=['skill_name', 'job_demand_count', 'demand_percentage']).to_sql("agg_top_skills", conn, if_exists="replace", index=False)

    # 4. Salary Aggregation by Job Title
    salary_agg = pdf_clean.groupby('clean_job_title').agg(
        total_jobs=('clean_job_title', 'count'),
        min_lpa=('min_salary_lpa', 'min'),
        max_lpa=('max_salary_lpa', 'max'),
        avg_lpa=('avg_salary_lpa', 'mean')
    ).reset_index()
    salary_agg['avg_lpa'] = salary_agg['avg_lpa'].round(2)
    salary_agg.to_sql("agg_salary_by_title", conn, if_exists="replace", index=False)

    # 5. Location Distribution
    loc_agg = pdf_clean.groupby('clean_city').agg(
        job_count=('clean_city', 'count'),
        avg_lpa=('avg_salary_lpa', 'mean')
    ).reset_index()
    loc_agg['avg_lpa'] = loc_agg['avg_lpa'].round(2)
    loc_agg.to_sql("agg_location_analytics", conn, if_exists="replace", index=False)

    conn.close()
    print("[Data Warehouse] ETL complete! Successfully loaded 5 analytical tables into 'job_analytics.db'.")
    return True


if __name__ == "__main__":
    run_pyspark_etl()
