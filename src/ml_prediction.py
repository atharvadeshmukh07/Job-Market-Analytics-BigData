import sqlite3
import pandas as pd
import numpy as np
import time

try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.linear_model import Ridge
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    from sklearn.model_selection import train_test_split
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

DB_NAME = "job_analytics.db"

def train_and_compare_ml_models():
    """
    Trains and compares 3 Machine Learning algorithms side-by-side for Viva Defense:
    1. Random Forest Regressor
    2. Gradient Boosting Regressor
    3. Ridge Linear Regression
    """
    if not SKLEARN_AVAILABLE:
        print("[ML Error] scikit-learn missing. Cannot train models.")
        return None

    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query(
        "SELECT clean_job_title, clean_city, is_remote, skills_str, avg_salary_lpa FROM dim_jobs WHERE avg_salary_lpa IS NOT NULL AND avg_salary_lpa > 0 AND avg_salary_lpa <= 80.0",
        conn
    )
    conn.close()

    if len(df) < 20:
        return None

    # Feature Engineering
    df['is_remote_num'] = df['is_remote'].astype(int)
    X = pd.get_dummies(df[['clean_job_title', 'clean_city', 'is_remote_num']], drop_first=True)
    y = df['avg_salary_lpa']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    models = {
        'Random Forest Regressor': RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42),
        'Gradient Boosting Regressor': GradientBoostingRegressor(n_estimators=100, max_depth=6, random_state=42),
        'Ridge Regression': Ridge(alpha=1.0)
    }

    comparison_results = []
    trained_models = {}

    for name, model in models.items():
        t0 = time.time()
        model.fit(X_train, y_train)
        fit_time = round((time.time() - t0) * 1000, 2)
        
        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)

        comparison_results.append({
            'Algorithm': name,
            'MAE (LPA)': round(mae, 2),
            'RMSE (LPA)': round(rmse, 2),
            'R² Score': round(r2, 2),
            'Accuracy %': f"{max(0, round(r2*100, 1))}%",
            'Training Time (ms)': fit_time
        })
        trained_models[name] = model

    df_results = pd.DataFrame(comparison_results)
    
    # Feature Importances from Random Forest
    rf_model = trained_models['Random Forest Regressor']
    importances = pd.DataFrame({
        'Feature': X.columns,
        'Importance': rf_model.feature_importances_
    }).sort_values('Importance', ascending=False)

    return {
        'comparison_table': df_results,
        'feature_importances': importances,
        'total_records': len(df),
        'feature_cols': list(X.columns)
    }

def predict_skill_demand_classification():
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
    res = train_and_compare_ml_models()
    if res:
        print(res['comparison_table'])
