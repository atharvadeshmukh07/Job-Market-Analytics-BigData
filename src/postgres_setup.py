"""
PostgreSQL Database Setup & PySpark Connection Adapter
------------------------------------------------------
This module allows connecting the Big Data Analytics platform to PostgreSQL 
(Local PostgreSQL Server or Cloud PostgreSQL like AWS RDS / Supabase / Neon / ElephantSQL).
"""

import os
import sqlite3
import pandas as pd

try:
    import psycopg2
    from sqlalchemy import create_engine
    POSTGRES_DRIVER_AVAILABLE = True
except ImportError:
    POSTGRES_DRIVER_AVAILABLE = False

# Default PostgreSQL Connection Configuration
PG_CONFIG = {
    'host': os.environ.get('PG_HOST', 'localhost'),
    'port': os.environ.get('PG_PORT', '5432'),
    'database': os.environ.get('PG_DATABASE', 'job_analytics_db'),
    'user': os.environ.get('PG_USER', 'postgres'),
    'password': os.environ.get('PG_PASSWORD', 'postgres')
}

def get_postgres_sqlalchemy_engine():
    """Builds SQLAlchemy Connection Engine for PostgreSQL."""
    if not POSTGRES_DRIVER_AVAILABLE:
        print("[PostgreSQL Warning] psycopg2/sqlalchemy not available.")
        return None
    try:
        connection_url = f"postgresql://{PG_CONFIG['user']}:{PG_CONFIG['password']}@{PG_CONFIG['host']}:{PG_CONFIG['port']}/{PG_CONFIG['database']}"
        engine = create_engine(connection_url)
        return engine
    except Exception as e:
        print(f"[PostgreSQL Connection Error] Could not create engine: {e}")
        return None

def migrate_sqlite_to_postgres(sqlite_db="job_analytics.db"):
    """
    Migrates SQLite Data Warehouse tables to PostgreSQL relational database.
    """
    print("==================================================")
    print("     POSTGRESQL DATA WAREHOUSE MIGRATION UTILITY   ")
    print("==================================================")
    
    if not os.path.exists(sqlite_db):
        print(f"[Migration Error] SQLite DB '{sqlite_db}' not found.")
        return False

    engine = get_postgres_sqlalchemy_engine()
    if not engine:
        print("[Migration Warning] PostgreSQL server connection unavailable. System is running cleanly on self-contained SQLite warehouse.")
        return False

    try:
        conn_sqlite = sqlite3.connect(sqlite_db)
        tables = ['dim_jobs', 'fact_job_skills', 'agg_top_skills', 'agg_salary_by_title', 'agg_location_analytics']
        
        for table in tables:
            df = pd.read_sql_query(f"SELECT * FROM {table}", conn_sqlite)
            df.to_sql(table, engine, if_exists='replace', index=False)
            print(f"  --> Successfully migrated table '{table}' ({len(df)} rows) to PostgreSQL database '{PG_CONFIG['database']}'")
        
        conn_sqlite.close()
        print("[PostgreSQL Warehouse] All 5 analytical tables deployed to PostgreSQL!")
        return True
    except Exception as e:
        print(f"[PostgreSQL Migration Error] {e}")
        return False


if __name__ == "__main__":
    migrate_sqlite_to_postgres()
