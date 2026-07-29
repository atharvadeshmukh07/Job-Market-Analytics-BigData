import re
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import modular helper cleaners
from src.location_cleaner import clean_and_validate_location
from src.salary_parser import parse_salary_to_lpa
from src.skill_extractor import extract_skills_from_text

def clean_title(title):
    """Strips common junk like '\\n- job post', '- Hyderabad', etc."""
    if not isinstance(title, str):
        return "Software Engineer"
    t = title.replace('\n- job post', '').strip()
    # Strip trailing '- Location' or '- City' in titles like 'Python Developer-Hyderabad'
    t = re.sub(r'[\-\|]\s*(?:Hyderabad|Bengaluru|Bangalore|Pune|Mumbai|Noida|Gurgaon|Chennai|Delhi).*$', '', t, flags=re.IGNORECASE).strip()
    return t if t else title.strip()

def normalize_indeed_row(row):
    title = str(row.get('Title', ''))
    loc = str(row.get('Location', ''))
    desc = str(row.get('Description', ''))
    salary = str(row.get('Salary', '')) if not pd_isna(row.get('Salary')) else ""
    company = str(row.get('Company', 'Unspecified'))
    
    is_indian, city, state, is_remote = clean_and_validate_location(loc, text_fallback=desc)
    min_sal, max_sal, avg_sal = parse_salary_to_lpa(salary)
    skills = extract_skills_from_text(title + " " + desc)

    return {
        'source_portal': 'Indeed',
        'raw_job_title': title,
        'clean_job_title': clean_title(title),
        'company': company.strip(),
        'raw_location': loc,
        'clean_city': city,
        'clean_state': state,
        'is_indian_location': is_indian,
        'is_remote': is_remote,
        'raw_salary': salary,
        'min_salary_lpa': min_sal,
        'max_salary_lpa': max_sal,
        'avg_salary_lpa': avg_sal,
        'job_description': desc,
        'extracted_skills': skills,
        'job_url': ""
    }

def normalize_linkedin_row(row):
    title = str(row.get('title', ''))
    company = str(row.get('company', 'Unspecified'))
    city_raw = str(row.get('city', ''))
    desc = str(row.get('job_description', ''))
    url = str(row.get('job_url', ''))

    is_indian, city, state, is_remote = clean_and_validate_location(city_raw, text_fallback=desc)
    min_sal, max_sal, avg_sal = parse_salary_to_lpa("")
    skills = extract_skills_from_text(title + " " + desc)

    return {
        'source_portal': 'LinkedIn',
        'raw_job_title': title,
        'clean_job_title': clean_title(title),
        'company': company.strip(),
        'raw_location': city_raw,
        'clean_city': city,
        'clean_state': state,
        'is_indian_location': is_indian,
        'is_remote': is_remote,
        'raw_salary': "",
        'min_salary_lpa': min_sal,
        'max_salary_lpa': max_sal,
        'avg_salary_lpa': avg_sal,
        'job_description': desc,
        'extracted_skills': skills,
        'job_url': url
    }

def normalize_wellfound_row(row):
    title = str(row.get('job_title', ''))
    company = str(row.get('company', 'Unspecified'))
    loc = str(row.get('location', ''))
    salary = str(row.get('salary', '')) if not pd_isna(row.get('salary')) else ""
    raw_skills = str(row.get('skills', '')) if not pd_isna(row.get('skills')) else ""
    url = str(row.get('job_url', ''))

    # Check if location was pushed into skills column
    combined_loc = loc + " " + raw_skills
    is_indian, city, state, is_remote = clean_and_validate_location(combined_loc)
    min_sal, max_sal, avg_sal = parse_salary_to_lpa(salary)
    skills = extract_skills_from_text(title + " " + raw_skills)

    return {
        'source_portal': 'Wellfound',
        'raw_job_title': title,
        'clean_job_title': clean_title(title),
        'company': company.strip(),
        'raw_location': loc,
        'clean_city': city,
        'clean_state': state,
        'is_indian_location': is_indian,
        'is_remote': is_remote,
        'raw_salary': salary,
        'min_salary_lpa': min_sal,
        'max_salary_lpa': max_sal,
        'avg_salary_lpa': avg_sal,
        'job_description': raw_skills,
        'extracted_skills': skills,
        'job_url': url
    }

def normalize_naukri_row(row):
    title = str(row.get('Column1', ''))
    company = str(row.get('Column2', 'Unspecified'))
    url = str(row.get('Column3', ''))
    loc = str(row.get('Column4', ''))
    salary = str(row.get('Column5', ''))
    desc = str(row.get('Column6', ''))

    is_indian, city, state, is_remote = clean_and_validate_location(loc, text_fallback=title + " " + desc)
    min_sal, max_sal, avg_sal = parse_salary_to_lpa(salary)
    skills = extract_skills_from_text(title + " " + desc)

    return {
        'source_portal': 'Naukri',
        'raw_job_title': title,
        'clean_job_title': clean_title(title),
        'company': company.strip(),
        'raw_location': loc,
        'clean_city': city,
        'clean_state': state,
        'is_indian_location': is_indian,
        'is_remote': is_remote,
        'raw_salary': salary,
        'min_salary_lpa': min_sal,
        'max_salary_lpa': max_sal,
        'avg_salary_lpa': avg_sal,
        'job_description': desc,
        'extracted_skills': skills,
        'job_url': url
    }

def pd_isna(val):
    if val is None:
        return True
    if isinstance(val, float) and str(val) == 'nan':
        return True
    if str(val).strip().lower() in ['nan', 'none', 'null', '']:
        return True
    return False
