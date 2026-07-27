import sqlite3
import pandas as pd
import numpy as np

try:
    from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
    from sklearn.metrics import mean_absolute_error, r2_score, accuracy_score, classification_report
    from sklearn.model_selection import train_test_split
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

DB_NAME = "job_analytics.db"

def train_and_evaluate_ml_models():
    """
    Trains and evaluates two Machine Learning models:
    1. Salary Regression Model (Predicts Salary Package in INR LPA)
    2. Skill Demand Classifier (Predicts Skill Demand Tier: High / Moderate / Niche)
    """
    print("==================================================")
    print("      MACHINE LEARNING MODEL EVALUATION SUITE      ")
    print("==================================================")

    if not SKLEARN_AVAILABLE:
        print("[ML Error] scikit-learn is missing. Cannot train model.")
        return None

    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query(
        "SELECT clean_job_title, clean_city, is_remote, skills_str, avg_salary_lpa FROM dim_jobs WHERE avg_salary_lpa IS NOT NULL AND avg_salary_lpa > 0 AND avg_salary_lpa <= 80.0",
        conn
    )
    conn.close()

    if len(df) < 10:
        print(f"[ML Warning] Not enough salary records ({len(df)} rows) to train ML model.")
        return None

    # Feature Engineering
    df['is_remote_num'] = df['is_remote'].astype(int)
    
    # Feature matrix (X) and target (y)
    X = pd.get_dummies(df[['clean_job_title', 'clean_city', 'is_remote_num']], drop_first=True)
    y_salary = df['avg_salary_lpa']

    # 1. Train Salary Regression Model
    X_train, X_test, y_train, y_test = train_test_split(X, y_salary, test_size=0.2, random_state=42)

    reg_model = RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42)
    reg_model.fit(X_train, y_train)

    y_pred = reg_model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print("\n--- SALARY REGRESSION MODEL METRICS ---")
    print(f"  * Total Dataset Records: {len(df):,}")
    print(f"  * Mean Absolute Error (MAE): +/- {mae:.2f} LPA")
    print(f"  * R2 Score (Variance Explained): {r2:.2f} ({max(0, r2*100):.1f}%)")

    # Feature Importances
    importances = pd.DataFrame({
        'Feature': X.columns,
        'Importance': reg_model.feature_importances_
    }).sort_values('Importance', ascending=False)
    
    print("\n--- Top 5 Features Driving Salary Predictions ---")
    for idx, row in importances.head(5).iterrows():
        print(f"  - {row['Feature']}: {row['Importance']*100:.2f}% impact")

    metrics_summary = {
        'total_records': len(df),
        'mae_lpa': round(mae, 2),
        'r2_score': round(r2, 2),
        'feature_importances': importances,
        'reg_model': reg_model,
        'feature_cols': list(X.columns)
    }

    return metrics_summary


def predict_skill_demand_classification():
    """
    Classifies skills into Demand Tiers (High Demand / Moderate Demand / Emerging)
    and computes market metrics.
    """
    conn = sqlite3.connect(DB_NAME)
    df_skills = pd.read_sql_query(
        "SELECT skill_name, COUNT(*) as job_count, AVG(avg_salary_lpa) as avg_lpa FROM fact_job_skills GROUP BY skill_name ORDER BY job_count DESC",
        conn
    )
    conn.close()

    if df_skills.empty:
        return pd.DataFrame()

    total_jobs = df_skills['job_count'].sum()
    df_skills['demand_share_%'] = (df_skills['job_count'] / total_jobs * 100).round(2)
    df_skills['avg_lpa'] = df_skills['avg_lpa'].round(2)

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
    train_and_evaluate_ml_models()
    df_trends = predict_skill_demand_classification()
    print("\n🔥 Skill Demand Classification Sample:")
    print(df_trends.head(10))
