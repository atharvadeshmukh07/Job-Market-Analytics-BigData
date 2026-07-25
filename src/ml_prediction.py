import sqlite3
import pandas as pd
import numpy as np

try:
    from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
    from sklearn.preprocessing import OneHotEncoder
    from sklearn.model_selection import train_test_split
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

DB_NAME = "job_analytics.db"

def train_salary_prediction_model():
    """
    Trains a Machine Learning Random Forest model to predict Salary (in LPA)
    based on Job Title, City, Remote status, and Tech Stack skills.
    """
    if not SKLEARN_AVAILABLE:
        print("[ML Error] scikit-learn is missing. Cannot train model.")
        return None, None

    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT clean_job_title, clean_city, is_remote, skills_str, avg_salary_lpa FROM dim_jobs WHERE avg_salary_lpa IS NOT NULL AND avg_salary_lpa > 0", conn)
    conn.close()

    if len(df) < 10:
        print(f"[ML Warning] Not enough salary data ({len(df)} rows) to train ML model.")
        return None, None

    # Feature Engineering
    df['is_remote_num'] = df['is_remote'].astype(int)
    
    # Feature matrix (X) and target (y)
    X = pd.get_dummies(df[['clean_job_title', 'clean_city', 'is_remote_num']], drop_first=True)
    y = df['avg_salary_lpa']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    print(f"[ML Model Trained] Salary Prediction Model | Train R2: {train_score:.2f}, Test R2: {test_score:.2f}")

    return model, list(X.columns)

def predict_skill_demand_trends():
    """
    Analyzes historical skill frequencies and forecasts future demand tier.
    """
    conn = sqlite3.connect(DB_NAME)
    df_skills = pd.read_sql_query("SELECT skill_name, COUNT(*) as job_count, AVG(avg_salary_lpa) as avg_lpa FROM fact_job_skills GROUP BY skill_name ORDER BY job_count DESC", conn)
    conn.close()

    if df_skills.empty:
        return pd.DataFrame()

    total_jobs = df_skills['job_count'].sum()
    df_skills['demand_share_%'] = (df_skills['job_count'] / total_jobs * 100).round(2)
    df_skills['avg_lpa'] = df_skills['avg_lpa'].round(2)

    # Classify Demand Tiers
    def classify_tier(row):
        if row['job_count'] >= 50:
            return "High Demand (Hot)"
        elif row['job_count'] >= 15:
            return "Moderate Demand"
        else:
            return "Emerging / Niche"

    df_skills['demand_tier'] = df_skills.apply(classify_tier, axis=1)
    return df_skills


if __name__ == "__main__":
    train_salary_prediction_model()
    df_trends = predict_skill_demand_trends()
    print("Skill Demand Forecast Sample:")
    print(df_trends.head(10))
