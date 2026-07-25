import re

SKILL_DICTIONARY = {
    # Big Data & Data Engineering
    'PySpark': [r'\bpyspark\b'],
    'Apache Spark': [r'\bspark\b', r'\bapache spark\b'],
    'Apache Kafka': [r'\bkafka\b', r'\bapache kafka\b'],
    'Hadoop': [r'\bhadoop\b', r'\bhdfs\b', r'\bmapreduce\b'],
    'Airflow': [r'\bairflow\b', r'\bapache airflow\b'],
    'Snowflake': [r'\bsnowflake\b'],
    'Databricks': [r'\bdatabricks\b'],
    'Hive': [r'\bhive\b', r'\bapache hive\b'],
    'Cassandra': [r'\bcassandra\b'],
    'Flink': [r'\bflink\b'],
    
    # Programming Languages
    'Python': [r'\bpython\b'],
    'Java': [r'\bjava\b'],
    'C++': [r'\bc\+\+\b', r'\bcpp\b'],
    'C#': [r'\bc\#\b', r'\bc sharp\b'],
    'SQL': [r'\bsql\b', r'\btsql\b', r'\bplsql\b', r'\bpl/sql\b'],
    'JavaScript': [r'\bjavascript\b', r'\bjs\b'],
    'TypeScript': [r'\btypescript\b', r'\bts\b'],
    'Scala': [r'\bscala\b'],
    'Go / Golang': [r'\bgolang\b', r'\bgo programming\b'],
    'R': [r'\br programming\b', r'\br lang\b'],
    
    # Databases
    'PostgreSQL': [r'\bpostgres\b', r'\bpostgresql\b'],
    'MySQL': [r'\bmysql\b'],
    'MongoDB': [r'\bmongodb\b', r'\bmongo\b'],
    'Oracle': [r'\boracle\b'],
    'Redis': [r'\bredis\b'],
    'Elasticsearch': [r'\belasticsearch\b'],
    
    # Cloud & Infrastructure
    'AWS': [r'\baws\b', r'\bamazon web services\b', r'\bs3\b', r'\bec2\b', r'\bredshift\b'],
    'Azure': [r'\bazure\b', r'\bmicrosoft azure\b'],
    'GCP': [r'\bgcp\b', r'\bgoogle cloud\b', r'\bbigquery\b'],
    'Docker': [r'\bdocker\b', r'\bcontainerization\b'],
    'Kubernetes': [r'\bkubernetes\b', r'\bk8s\b'],
    'Terraform': [r'\bterraform\b'],
    'CI/CD': [r'\bci/cd\b', r'\bjenkins\b', r'\bgithub actions\b'],
    'Linux': [r'\blinux\b', r'\bbash\b', r'\bshell scripting\b'],

    # Data Science & AI / ML
    'Machine Learning': [r'\bmachine learning\b', r'\bml\b'],
    'Deep Learning': [r'\bdeep learning\b', r'\bdl\b'],
    'NLP': [r'\bnlp\b', r'\bnatural language processing\b'],
    'TensorFlow': [r'\btensorflow\b'],
    'PyTorch': [r'\bpytorch\b'],
    'Scikit-Learn': [r'\bscikit-learn\b', r'\bsklearn\b'],
    'Pandas': [r'\bpandas\b'],
    'NumPy': [r'\bnumpy\b'],
    'Generative AI / LLMs': [r'\bgenerative ai\b', r'\bllm\b', r'\bllms\b', r'\bgpt\b', r'\bopenai\b'],
    'Tableau': [r'\btableau\b'],
    'PowerBI': [r'\bpower bi\b', r'\bpowerbi\b'],

    # Web & Backend
    'React': [r'\breact\b', r'\breactjs\b', r'\breact.js\b'],
    'Node.js': [r'\bnode\b', r'\bnodejs\b', r'\bnode.js\b'],
    'Angular': [r'\bangular\b'],
    'Vue': [r'\bvue\b', r'\bvuejs\b'],
    'Django': [r'\bdjango\b'],
    'Flask': [r'\bflask\b'],
    'FastAPI': [r'\bfastapi\b'],
    'Spring Boot': [r'\bspring boot\b', r'\bspring\b'],
    'REST API': [r'\brest\b', r'\brestful\b', r'\brest api\b'],
    'Microservices': [r'\bmicroservices\b']
}

def extract_skills_from_text(text):
    """
    Extracts structured technical skills from combined title + description text.
    Returns a list of unique matched skill names.
    """
    if not isinstance(text, str) or not text.strip():
        return []

    text_lower = text.lower()
    extracted = []

    for skill_name, patterns in SKILL_DICTIONARY.items():
        for pat in patterns:
            if re.search(pat, text_lower):
                extracted.append(skill_name)
                break

    return sorted(list(set(extracted)))


if __name__ == "__main__":
    sample_text = "Looking for a Data Engineer with PySpark, Apache Kafka, Python, AWS S3, PostgreSQL, and Docker experience."
    print("Sample Text:", sample_text)
    print("Extracted Skills:", extract_skills_from_text(sample_text))
