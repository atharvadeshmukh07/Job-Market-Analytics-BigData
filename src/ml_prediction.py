import sqlite3
import pandas as pd
import numpy as np
import time

try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.linear_model import Ridge
    from sklearn.cluster import KMeans
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    from sklearn.model_selection import train_test_split, cross_val_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

DB_NAME = "job_analytics.db"

# Curated Role-Specific Skill Mapping to prevent irrelevant skill predictions
CURATED_ROLE_SKILLS = {
    "python": ["Python", "Django", "FastAPI", "Flask", "PyTest", "PostgreSQL", "Docker", "REST API", "Celery", "Redis", "AWS", "Git"],
    "java": ["Java", "Spring Boot", "Microservices", "Hibernate", "Maven", "MySQL", "PostgreSQL", "Docker", "REST API", "Kafka"],
    "react": ["React.js", "JavaScript", "TypeScript", "Redux", "HTML5", "CSS3", "Tailwind CSS", "Next.js", "REST API", "Git"],
    "angular": ["Angular", "TypeScript", "JavaScript", "RxJS", "HTML5", "CSS3", "Bootstrap", "REST API", "Git"],
    "vue": ["Vue.js", "JavaScript", "TypeScript", "Vuex", "HTML5", "CSS3", "REST API", "Git"],
    "frontend": ["React.js", "JavaScript", "TypeScript", "HTML5", "CSS3", "Redux", "Tailwind CSS", "REST API", "Git"],
    "node": ["Node.js", "Express.js", "TypeScript", "JavaScript", "MongoDB", "PostgreSQL", "REST API", "Docker", "Redis"],
    "backend": ["Python", "Node.js", "Java", "PostgreSQL", "MySQL", "Docker", "REST API", "Redis", "Microservices", "AWS"],
    "full stack": ["React.js", "Node.js", "Python", "TypeScript", "JavaScript", "PostgreSQL", "Docker", "REST API", "HTML5", "CSS3"],
    "machine learning": ["Python", "Machine Learning", "TensorFlow", "PyTorch", "Scikit-Learn", "Deep Learning", "NLP", "Pandas", "NumPy", "SQL"],
    "ai": ["Python", "GenAI", "PyTorch", "TensorFlow", "NLP", "Deep Learning", "Machine Learning", "LLMs", "LangChain", "OpenAI"],
    "data scientist": ["Python", "SQL", "Machine Learning", "Pandas", "NumPy", "Scikit-Learn", "Statistics", "Data Visualization", "Tableau", "Power BI"],
    "data engineer": ["PySpark", "Apache Kafka", "SQL", "Python", "AWS", "Snowflake", "Airflow", "Databricks", "Docker", "ETL", "PostgreSQL"],
    "big data": ["PySpark", "Apache Kafka", "Hadoop", "Hive", "SQL", "Python", "AWS", "Databricks", "Scala", "Airflow"],
    "data analyst": ["SQL", "Python", "Power BI", "Tableau", "Excel", "Pandas", "Data Visualization", "Statistics"],
    "devops": ["Docker", "Kubernetes", "AWS", "Terraform", "CI/CD", "Linux", "Jenkins", "Ansible", "Bash", "Python"],
    "cloud": ["AWS", "Azure", "GCP", "Terraform", "Docker", "Kubernetes", "Cloud Architecture", "Linux", "Microservices"],
    "sre": ["Kubernetes", "Docker", "Linux", "Python", "Go", "Prometheus", "Grafana", "AWS", "CI/CD", "Bash"],
    "qa": ["Selenium", "Automation Testing", "PyTest", "Java", "Postman", "Cypress", "Jira", "CI/CD", "SQL", "API Testing"],
    "test": ["Selenium", "Automation Testing", "PyTest", "Java", "Cypress", "Jira", "SQL", "API Testing", "Postman"],
    "mobile": ["Kotlin", "Android SDK", "Java", "Flutter", "React Native", "Swift", "REST API", "Git"],
    "android": ["Kotlin", "Java", "Android SDK", "REST API", "Git", "Gradle", "SQLite"],
    "ios": ["Swift", "SwiftUI", "iOS SDK", "Objective-C", "REST API", "Xcode", "Git"],
    "sql": ["SQL", "PostgreSQL", "MySQL", "Oracle", "Database Administration", "Performance Tuning", "ETL"],
    ".net": [".NET Core", "C#", "ASP.NET", "SQL Server", "Entity Framework", "Azure", "REST API", "Microservices"],
    "c++": ["C++", "Data Structures", "Algorithms", "Linux", "Multithreading", "Object-Oriented Programming", "Git"],
    "c#": ["C#", ".NET Core", "SQL Server", "ASP.NET", "Entity Framework", "Azure", "REST API"],
    "php": ["PHP", "Laravel", "MySQL", "JavaScript", "HTML5", "CSS3", "REST API", "Git"],
    "ui/ux": ["Figma", "UI Design", "UX Research", "Wireframing", "Prototyping", "Adobe XD", "HTML5", "CSS3"],
    "design": ["Figma", "UI/UX Design", "Wireframing", "Prototyping", "Adobe Creative Suite", "User Research"],
    "sales": ["CRM", "Salesforce", "Lead Generation", "B2B Sales", "Client Acquisition", "Negotiation", "Account Management"],
    "hr": ["Technical Recruiting", "Sourcing", "Talent Acquisition", "Screening", "HRIS", "Interviews", "Onboarding"],
    "recruiter": ["Technical Recruiting", "Sourcing", "Talent Acquisition", "LinkedIn Recruiter", "Screening", "Interviews"],
    "manager": ["Agile", "Scrum", "Project Management", "Jira", "Team Leadership", "Product Roadmap", "Stakeholder Management"]
}

def get_curated_skills_for_role(role_title):
    if not isinstance(role_title, str):
        return ["Python", "SQL", "Git", "Docker", "PostgreSQL"]
    
    t_lower = role_title.lower()
    
    # Priority keyword matching
    for key, skills in CURATED_ROLE_SKILLS.items():
        if key in t_lower:
            return skills
            
    return ["Python", "SQL", "Git", "Docker", "PostgreSQL", "REST API", "Linux", "AWS"]

def train_unsupervised_kmeans_imputation(df):
    """
    Applies Unsupervised K-Means Clustering (K=8) on TF-IDF skill & text vectors
    to impute estimated salaries for unlabelled job postings.
    """
    if not SKLEARN_AVAILABLE or df.empty:
        return df, None

    df['text_features'] = df['clean_job_title'].fillna('') + " " + df['skills_str'].fillna('') + " " + df['clean_city'].fillna('')
    
    # Fast TF-IDF + K-Means (n_init=1, max_features=40)
    tfidf = TfidfVectorizer(max_features=40, stop_words='english')
    X_tfidf = tfidf.fit_transform(df['text_features'])

    kmeans = KMeans(n_clusters=8, random_state=42, n_init=1)
    df['cluster'] = kmeans.fit_predict(X_tfidf)

    disclosed_mask = (df['avg_salary_lpa'].notnull()) & (df['avg_salary_lpa'] >= 1.5) & (df['avg_salary_lpa'] <= 80.0)
    cluster_medians = df[disclosed_mask].groupby('cluster')['avg_salary_lpa'].median().to_dict()
    overall_median = df[disclosed_mask]['avg_salary_lpa'].median() if disclosed_mask.any() else 12.5

    df['imputed_salary_lpa'] = df.apply(
        lambda row: row['avg_salary_lpa'] if (pd.notnull(row['avg_salary_lpa']) and 1.5 <= row['avg_salary_lpa'] <= 80.0)
        else cluster_medians.get(row['cluster'], overall_median),
        axis=1
    )
    return df, kmeans

def train_and_compare_ml_models():
    """
    Trains ML Regressors on K-Means imputed Data Warehouse records
    and computes Train vs Test Overfitting/Underfitting diagnostics.
    """
    if not SKLEARN_AVAILABLE:
        print("[ML Error] scikit-learn missing.")
        return None

    conn = sqlite3.connect(DB_NAME)
    df_raw = pd.read_sql_query(
        "SELECT clean_job_title, clean_city, is_remote, skills_str, avg_salary_lpa FROM dim_jobs",
        conn
    )
    conn.close()

    if len(df_raw) < 20:
        return None

    # Step 1: Unsupervised Learning K-Means Imputation
    df, kmeans_model = train_unsupervised_kmeans_imputation(df_raw)

    # Step 2: Feature Engineering (Lightweight sampling for sub-second diagnostic evaluation)
    df['is_remote_num'] = df['is_remote'].astype(int)
    top_100_titles = set(df['clean_job_title'].value_counts().head(100).index)
    df['canonical_role_100'] = df['clean_job_title'].apply(lambda t: t if t in top_100_titles else 'Software Engineer')
    
    # Sample up to 5000 records for lightning-fast model evaluation benchmark
    df_eval = df.sample(n=min(5000, len(df)), random_state=42) if len(df) > 5000 else df
    X = pd.get_dummies(df_eval[['canonical_role_100', 'clean_city', 'is_remote_num']], drop_first=True)
    y = df_eval['imputed_salary_lpa']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    models = {
        'Random Forest Regressor': RandomForestRegressor(n_estimators=40, max_depth=8, min_samples_split=5, random_state=42, n_jobs=-1),
        'Gradient Boosting Regressor': GradientBoostingRegressor(n_estimators=30, max_depth=4, random_state=42),
        'Ridge Regression': Ridge(alpha=1.0)
    }

    comparison_results = []
    trained_models = {}

    for name, model in models.items():
        t0 = time.time()
        model.fit(X_train, y_train)
        fit_time = round((time.time() - t0) * 1000, 2)
        
        # Train diagnostics
        y_train_pred = model.predict(X_train)
        train_mae = mean_absolute_error(y_train, y_train_pred)
        train_r2 = r2_score(y_train, y_train_pred)

        # Test diagnostics
        y_test_pred = model.predict(X_test)
        test_mae = mean_absolute_error(y_test, y_test_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
        test_r2 = r2_score(y_test, y_test_pred)

        # 5-Fold Cross Validation
        cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='neg_mean_absolute_error')
        cv_mae = -cv_scores.mean()

        overfit_status = "Balanced (Optimal)" if abs(test_mae - train_mae) < 0.8 else ("Overfitting" if test_mae > train_mae else "Underfitting")

        comparison_results.append({
            'Algorithm': name,
            'Train MAE': round(train_mae, 2),
            'Test MAE (LPA)': round(test_mae, 2),
            '5-Fold CV MAE': round(cv_mae, 2),
            'RMSE (LPA)': round(rmse, 2),
            'Train R²': round(train_r2, 2),
            'Test R² Score': round(test_r2, 2),
            'Status': overfit_status,
            'Fit Time (ms)': fit_time
        })
        trained_models[name] = model

    df_results = pd.DataFrame(comparison_results)
    
    rf_model = trained_models['Random Forest Regressor']
    importances = pd.DataFrame({
        'Feature': X.columns,
        'Importance': rf_model.feature_importances_
    }).sort_values('Importance', ascending=False)

    return {
        'comparison_table': df_results,
        'feature_importances': importances,
        'total_records': len(df),
        'disclosed_records': int((df_raw['avg_salary_lpa'] >= 1.5).sum()),
        'imputed_records': len(df) - int((df_raw['avg_salary_lpa'] >= 1.5).sum()),
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

