import re

# Comprehensive list of Indian Cities, Metros, IT Hubs, and States
INDIAN_CITIES = {
    'bengaluru', 'bangalore', 'hyderabad', 'pune', 'mumbai', 'navi mumbai', 'thane',
    'delhi', 'new delhi', 'noida', 'greater noida', 'gurgaon', 'gurugram', 'chennai',
    'kolkata', 'ahmedabad', 'kochi', 'cochin', 'trivandrum', 'thiruvananthapuram',
    'coimbatore', 'indore', 'jaipur', 'chandigarh', 'mohali', 'visakhapatnam', 'vizag',
    'surat', 'vadodara', 'nagpur', 'bhopal', 'bhubaneswar', 'mysore', 'mysuru',
    'hubli', 'nashik', 'lucknow', 'kanpur', 'patna', 'guwahati', 'dehradun',
    'mangalore', 'mangaluru', 'secunderabad', 'rajkot', 'aurangabad', 'gwalior',
    'jodhpur', 'ranchi', 'raipur', 'calicut', 'kozhikode', 'thrissur', 'madurai',
    'trichy', 'tiruchirappalli', 'vijayawada', 'warangal', 'tirupati', 'noida'
}

INDIAN_STATES = {
    'karnataka', 'telangana', 'maharashtra', 'tamil nadu', 'delhi', 'delhi ncr',
    'haryana', 'uttar pradesh', 'up', 'west bengal', 'gujarat', 'kerala', 'rajasthan',
    'madhya pradesh', 'mp', 'andhra pradesh', 'ap', 'punjab', 'odisha', 'bihar',
    'assam', 'uttarakhand', 'goa', 'jammu and kashmir', 'chhattisgarh', 'jharkhand'
}

# Standard mappings for city variations
CITY_STANDARDIZATION = {
    'bangalore': 'Bengaluru',
    'bengaluru': 'Bengaluru',
    'gurgaon': 'Gurugram',
    'gurugram': 'Gurugram',
    'cochin': 'Kochi',
    'kochi': 'Kochi',
    'trivandrum': 'Thiruvananthapuram',
    'thiruvananthapuram': 'Thiruvananthapuram',
    'vizag': 'Visakhapatnam',
    'visakhapatnam': 'Visakhapatnam',
    'mysore': 'Mysuru',
    'mysuru': 'Mysuru',
    'mangaluru': 'Mangalore',
    'mangalore': 'Mangalore',
    'calicut': 'Kozhikode',
    'kozhikode': 'Kozhikode',
    'new delhi': 'Delhi NCR',
    'delhi': 'Delhi NCR',
    'noida': 'Delhi NCR',
    'greater noida': 'Delhi NCR',
    'navi mumbai': 'Mumbai',
    'thane': 'Mumbai',
    'mumbai': 'Mumbai',
    'hyderabad': 'Hyderabad',
    'secunderabad': 'Hyderabad',
    'pune': 'Pune',
    'chennai': 'Chennai',
    'kolkata': 'Kolkata',
    'ahmedabad': 'Ahmedabad',
    'coimbatore': 'Coimbatore',
    'indore': 'Indore',
    'jaipur': 'Jaipur',
    'chandigarh': 'Chandigarh',
    'mohali': 'Chandigarh'
}

def clean_and_validate_location(raw_loc, text_fallback=""):
    """
    Cleans raw location string and determines if it is an Indian location.
    Returns tuple: (is_indian: bool, clean_city: str, clean_state: str, is_remote: bool)
    """
    if not isinstance(raw_loc, str) or not raw_loc.strip():
        raw_loc = str(text_fallback) if isinstance(text_fallback, str) else ""

    text = raw_loc.lower()
    
    # Explicit rejection of foreign locations if mentioned without India
    foreign_keywords = ['canada', 'united states', 'usa', 'uk', 'london', 'singapore', 'berlin', 'germany', 'australia', 'sydney', 'toronto', 'vancouver']
    for fk in foreign_keywords:
        if fk in text and 'india' not in text:
            return False, "Foreign", "Foreign", False

    is_remote = any(r in text for r in ['remote', 'wfh', 'work from home', 'hybrid'])
    
    # Check for Indian indicator
    has_india = 'india' in text or 'in' in text.split()

    matched_city = None
    matched_state = None

    # Check for cities
    for city in INDIAN_CITIES:
        if re.search(rf'\b{re.escape(city)}\b', text):
            std_city = CITY_STANDARDIZATION.get(city, city.title())
            matched_city = std_city
            break

    # Check for states
    for state in INDIAN_STATES:
        if re.search(rf'\b{re.escape(state)}\b', text):
            matched_state = state.title()
            break

    # If city or state matched, or explicitly India
    if matched_city or matched_state or has_india:
        final_city = matched_city if matched_city else ("Remote India" if is_remote else "India (Unspecified)")
        final_state = matched_state if matched_state else "India"
        return True, final_city, final_state, is_remote

    if is_remote:
        return True, "Remote India", "India", True

    return False, "Non-India", "Non-India", False


CANONICAL_ROLES = [
    ("Machine Learning Engineer", [r'\bml\b', r'machine learning', r'ai/ml', r'ai engineer', r'ai developer', r'deep learning', r'llm', r'genai', r'artificial intelligence', r'computer vision', r'nlp']),
    ("Data Engineer", [r'data engineer', r'pyspark', r'big data', r'etl developer', r'etl engineer', r'data pipeline', r'databricks engineer']),
    ("Data Scientist", [r'data scientist', r'data science', r'statistical analyst']),
    ("Data Analyst", [r'data analyst', r'business analyst', r'data analytics', r'bi analyst', r'power bi analyst', r'tableau analyst']),
    ("DevOps Engineer", [r'devops', r'site reliability', r'sre\b', r'ci/cd', r'infrastructure engineer', r'platform engineer']),
    ("Cloud Architect", [r'cloud architect', r'aws architect', r'azure architect', r'cloud engineer', r'solutions architect']),
    ("Full Stack Developer", [r'full stack', r'fullstack', r'mean stack', r'mern stack']),
    ("Frontend Engineer", [r'frontend', r'front end', r'react developer', r'angular developer', r'vue developer', r'ui developer']),
    ("Backend Engineer", [r'backend', r'back end', r'python backend', r'java backend', r'node\.js developer', r'spring boot']),
    ("Software Engineer", [r'software engineer', r'software developer', r'sde', r'swe\b', r'python developer', r'java developer', r'c\+\+ developer', r'member of technical staff']),
    ("Product Manager", [r'product manager', r'technical product manager', r'product owner']),
    ("QA / Test Engineer", [r'qa engineer', r'test engineer', r'automation tester', r'sdet'])
]

def normalize_canonical_job_title(raw_title):
    if not isinstance(raw_title, str) or not raw_title.strip():
        return "Software Engineer"
    
    t = raw_title.lower()
    t = re.sub(r'[^\x00-\x7F]+', '', t)
    
    for canonical_name, patterns in CANONICAL_ROLES:
        for p in patterns:
            if re.search(p, t):
                return canonical_name

    return "Software Engineer"


def sanitize_job_title_for_ui(t):
    if not isinstance(t, str):
        return "Software Engineer"
    import re
    
    # 1. Strip quotes and decorative symbols/punctuation
    t = t.strip('\"\' ')
    t = re.sub(r'[^\x00-\x7F]+', '', t) # remove emojis/non-ascii
    t = re.sub(r'[\!\*\#\[\]\{\}\=\~]', ' ', t)
    
    # 2. Remove leading/trailing tracking IDs and job codes like #2026-D-0042 or 3562871- or - 1357
    t = re.sub(r'^(?:\#[\w\-]+\s*|\d{4,}\-?\s*)', '', t)
    t = re.sub(r'[\-\|\:\#]\s*\d{3,}\b', '', t)
    t = re.sub(r'\b\d{5,}\b', '', t)

    # 3. Remove walk-in dates and event information
    t = re.sub(r'\b\d{1,2}(?:st|nd|rd|th)?\s+(?:jan|feb|mar|apr|may|jun|july?|aug|sep|oct|nov|dec)[a-z]*\b.*', '', t, flags=re.IGNORECASE)
    t = re.sub(r'\b(walkin|walk-in|walk in|job drive|hiring drive|mega drive)\b.*', '', t, flags=re.IGNORECASE)

    # 4. Remove experience text (e.g. 'with 5-8 years Exp', '5-8 Yrs', 'Exp: 2-4 yrs')
    t = re.sub(r'\b(?:with\s+)?\d+\s*[\-\+]\s*\d+\s*(?:years?|yrs?)(?:\s*exp(?:erience)?)?\b', '', t, flags=re.IGNORECASE)
    t = re.sub(r'\b(?:with\s+)?\d+\+?\s*(?:years?|yrs?)(?:\s*exp(?:erience)?)?\b', '', t, flags=re.IGNORECASE)
    t = re.sub(r'\bexp(?:erience)?\s*[\:\-]?\s*\d+.*', '', t, flags=re.IGNORECASE)

    # 5. Remove shift information
    t = re.sub(r'\((?:night|day|us|uk|rotational|flexible)\s*shift\)', '', t, flags=re.IGNORECASE)
    t = re.sub(r'\b(?:night|day|us|uk|rotational)\s+shift\b', '', t, flags=re.IGNORECASE)

    # 6. Remove noise hiring keywords
    t = re.sub(r'\b(urgent hiring|urgent|hiring for|hiring|immediate joiner|immediate|m/f/d|apply now|job opening)\b', '', t, flags=re.IGNORECASE)

    # 7. Remove appended location names
    t = re.sub(r'[\-\|\,]\s*(?:Bengaluru|Bangalore|Hyderabad|Pune|Mumbai|Delhi|Noida|Gurgaon|Gurugram|Chennai|Kolkata|Ahmedabad|India|Remote).*$', '', t, flags=re.IGNORECASE)

    # 8. Standardize abbreviations
    t = re.sub(r'\bSr\.\s*', 'Senior ', t, flags=re.IGNORECASE)
    t = re.sub(r'\bSr\b', 'Senior', t, flags=re.IGNORECASE)
    t = re.sub(r'\bJr\.\s*', 'Junior ', t, flags=re.IGNORECASE)
    t = re.sub(r'\bJr\b', 'Junior', t, flags=re.IGNORECASE)
    t = re.sub(r'\bDevelopers\b', 'Developer', t, flags=re.IGNORECASE)
    t = re.sub(r'\bEngineers\b', 'Engineer', t, flags=re.IGNORECASE)
    t = re.sub(r'\bAnalysts\b', 'Analyst', t, flags=re.IGNORECASE)
    t = re.sub(r'\bUs\b', 'US', t)
    t = re.sub(r'\bIt\b', 'IT', t)
    t = re.sub(r'\bAi\b', 'AI', t)
    t = re.sub(r'\bMl\b', 'ML', t)

    # Clean whitespace and punctuation
    t = re.sub(r'\(\s*\)', '', t)
    t = re.sub(r'\s+', ' ', t).strip(' -:|,.')

    if len(t) < 3 or 'big question' in t.lower() or 'what next' in t.lower():
        return "Software Engineer"
    return t.title()

if __name__ == "__main__":
    test_locs = [
        "Hyderabad, Telangana",
        "Coimbatore, Tamil Nadu, India",
        "Bangalore/Bengaluru",
        "Remote Work Policy In office",
        "Remote ( Canada ) • Canada",
        "Hybrid - Gurgaon",
        "Mumbai (All Areas)"
    ]
    for loc in test_locs:
        print(f"'{loc}' -> {clean_and_validate_location(loc)}")

