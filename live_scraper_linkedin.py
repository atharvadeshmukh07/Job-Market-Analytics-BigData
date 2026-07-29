import os
import csv
import time
import random
from datetime import datetime
import requests
from bs4 import BeautifulSoup

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_OUTPUT_PATH = os.path.join(CURRENT_DIR, "jobs.csv")

def load_existing_urls(filename):
    existing = set()
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                url = row.get("job_url")
                if url:
                    existing.add(url)
    return existing

def append_to_csv(rows, filename):
    if not rows:
        return
    file_exists = os.path.exists(filename)
    try:
        with open(filename, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["title", "company", "city", "job_url", "job_description", "source"],
            )
            if not file_exists:
                writer.writeheader()
            writer.writerows(rows)
        print(f"Successfully saved {len(rows)} new jobs to CSV.")
    except PermissionError:
        print("\n⚠️ Close your CSV file in Excel so Python can write to it!\n")

def scrape_linkedin_page(keyword, location, start_index, existing_urls):
    encoded_keyword = keyword.replace(" ", "%20")
    encoded_location = location.replace(" ", "%20")
    
    search_url = f"https://www.linkedin.com/jobs/search?keywords={encoded_keyword}&location={encoded_location}&start={start_index}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
    }

    try:
        response = requests.get(search_url, headers=headers, timeout=30)
        if response.status_code == 429:
            print("⚠️ LinkedIn flagged the IP (Rate Limited). Sleeping for 5 minutes...")
            time.sleep(300)
            return [], False
        
        response.raise_for_status()
    except Exception as e:
        print(f"Network error on index {start_index}: {e}")
        return [], False

    soup = BeautifulSoup(response.text, "html.parser")
    cards = soup.select('ul.jobs-search__results-list li') or soup.select('div.base-search-card')
    
    if not cards:
        return [], True 

    jobs = []
    for card in cards:
        title_el = card.select_one(".base-search-card__title")
        company_el = card.select_one(".base-search-card__subtitle a") or card.select_one(".base-search-card__subtitle")
        city_el = card.select_one(".job-search-card__location")
        desc_el = card.select_one(".base-search-card__metadata") 
        link_el = card.select_one("a.base-card__full-link")

        job_url = link_el.get("href", "").split("?")[0].strip() if link_el else ""
        if not job_url or job_url in existing_urls:
            continue

        existing_urls.add(job_url)
        jobs.append({
            "title": title_el.get_text(strip=True) if title_el else "N/A",
            "company": company_el.get_text(strip=True) if company_el else "N/A",
            "city": city_el.get_text(strip=True) if city_el else "N/A",
            "job_url": job_url,
            "job_description": desc_el.get_text(strip=True) if desc_el else "N/A",
            "source": f"LinkedIn India - {keyword}",
        })

    return jobs, False

if __name__ == "__main__":
    # CONFIGURATION EXPANDED TO 40 TECH JOB TITLES
    KEYWORDS_POOL = [

    # INDIAN IT SERVICE GIANTS / MNC DESIGNATION BANDS (Massive Data Pools)
    "Technology Lead",
    "Technology Analyst",
    "Senior Systems Engineer",
    "Technical Specialist",
    "Module Lead",
    "Project Lead",
    "Delivery Manager",
    "Service Delivery Manager",
    "Portfolio Delivery Lead",
    "Functional Architect",
    "Delivery Excellence Specialist",
    "IT Delivery Manager",
    "AVP Engineering",
    "Director IT Delivery",

    # GLOBAL CAPABILITY CENTERS (GCC) & CHIP DESIGN ROLES (Booming in India)
    "Semiconductor Design Engineer",
    "VLSI Design Engineer",
    "Physical Design Engineer",
    "RTL Design Engineer",
    "ASIC Verification Engineer",
    "FPGA Design Engineer",
    "Hardware Verification Engineer",
    "SoC Architecture Engineer",
    "Analog Layout Engineer",

    # RECRUITMENT & TECH OPERATIONS CAPACITY (High-frequency job postings)
    "US IT Recruiter",
    "Technical Recruiter",
    "IT Technical Recruiter",
    "Senior US IT Recruiter",
    "Bench Sales Recruiter",
    "IT Staffing Consultant",
    "Technical Trainer",
    "Software Technical Trainer",
    "Inside Sales Associate IT",
    "Business Development Executive IT",
    "IT Sales Executive",

    # AGENTIC AI & HYPER-AUTOMATION (2026 Shift Roles)
    "Agentic AI Developer",
    "Intelligent Automation Engineer",
    "AI Agent Engineer",
    "RPA AI Specialist",
    "UiPath Developer",
    "Automation Anywhere Developer",
    "Blue Prism Developer",
    "Cognitive Automation Engineer",

    # GEOSPATIAL & SPECIALIZED DOMAIN ENGINEERING
    "GIS Developer",
    "GIS Engineer",
    "Geospatial Software Engineer",
    "ArcGIS Developer",
    "BIM Software Engineer",
    "PropTech Software Engineer",
    "Bioinformatics Software Engineer",

    # SERVICENOW & ENTERPRISE WORKFLOW SYSTEMS (Extremely high distinct pool in India)
    "ServiceNow Developer",
    "ServiceNow Consultant",
    "ServiceNow ITSM Engineer",
    "ServiceNow Architect",
    "Snow HRSD Developer",
    "ForgeRock Access Management Consultant",
    "Identity Management Consultant",

    # SAP & ENTERPRISE ARCHITECTURE EXTENSIONS (Deep transactional hits)
    "SAP MM Developer",
    "SAP GTS Software Engineer",
    "SAP FI S4HANA Developer",
    "SAP Central Finance Engineer",
    "SAP ABAP Consultant",
    "SAP BASIS Engineer",
    "SAP HANA Architect",
    "SAP SuccessFactors Specialist",

    # COMPLIANCE, SECURITY ASSURANCE & GOVERNANCE
    "IT Control Engineer",
    "Tech Assurance Analyst",
    "Cyber Resilience Engineer",
    "IT Auditor",
    "Technology Risk Analyst",
    "Data Privacy Compliance Specialist",
    "GDPR Analyst IT",
    "BFSI Compliance Analyst",

    # CLOUD SPECIFIC ENDPOINTS & COMPILER INFRASTRUCTURE
    "Microsoft Intune Engineer",
    "Endpoint Security Architect",
    "IT Product Architect",
    "Azure IaaS Engineer",
    "AWS SysOps Administrator",
    "Google Cloud Platform Engineer",

    # RECENT CAMPUS TRAINEE HYPER-VARIATIONS (India Campus Pulses)
    "Graduate Engineer Trainee",
    "GET IT",
    "Post Graduate Engineer Trainee",
    "PGET IT",
    "Trainee Engineer",
    "Software Engineering Intern",
    "Technical Associate Trainee",

    # MAINFRAME & LEGACY BANKING BACKENDS (Massive, high-volume hiring by Indian MNCs)
    "Mainframe Developer",
    "Mainframe Engineer",
    "COBOL Programmer",
    "AS400 Developer",
    "DB2 Developer",
    "JCL Developer",
    "CICS Engineer",
    "Mainframe System Programmer",

    # SPECIFIC BI & DATA INTEGRATION TOOLS (Highly distinct listing pools)
    "Power BI Developer",
    "Tableau Developer",
    "Informatica Developer",
    "Talend Developer",
    "Alteryx Developer",
    "QlikSense Developer",
    "Looker Developer",
    "MicroStrategy Developer",
    "Data Integration Specialist",

    # E-COMMERCE & CMS PLATFORM STACKS (Enormous job volumes in India)
    "Shopify Developer",
    "Magento Developer",
    "Adobe Experience Manager Developer",
    "AEM Developer",
    "WooCommerce Developer",
    "Webflow Developer",
    "WordPress Developer",
    "Drupal Developer",
    "Salesforce Commerce Cloud Developer",

    # DEV_OPS & INFRASTRUCTURE IAC TOOLS (Searching tools directly gets unique hits)
    "Terraform Engineer",
    "Ansible Automation Engineer",
    "Jenkins Engineer",
    "ArgoCD Specialist",
    "Istio Engineer",
    "CloudFormation Specialist",
    "OpenShift Engineer",

    # MOBILE & MODERN LANGUAGES (Untapped Variations)
    "Kotlin Developer",
    "Swift Developer",
    "Elixir Developer",
    "Clojure Developer",
    "Scala Backend Engineer",
    "Rust Software Engineer",

    # TECH ENTRY-LEVEL ACERBATIONS (Specific to Indian Campus Recruitment)
    "Post Graduate Engineer Trainee",
    "PGET",
    "Software Trainee",
    "IT Trainee",
    "Apprentice Software Engineer",
    "Technical Associate Trainee",

    # HIGH-LEVEL ENGINEERING LEADERSHIP (Fewer listings, but highly unique text)
    "Staff Software Engineer",
    "Senior Staff Engineer",
    "Distinguished Engineer",
    "Principal Architect",
    "Director of Engineering",
    "VP of Engineering",
    "Engineering Lead",
    "Head of Technology",

    # DEEP TECH AI, HARDWARE COMPILERS & ACCELERATORS (2026 High-Growth Roles)
    "CUDA Developer",
    "GPU Optimization Engineer",
    "AI Compiler Engineer",
    "Triton Developer",
    "Edge AI Engineer",
    "NLP Data Scientist",
    "Speech Recognition Engineer",

    # CYBERSECURITY PRODUCT & IAM TOOLING
    "Okta Engineer",
    "CyberArk Engineer",
    "Ping Identity Engineer",
    "CrowdStrike Analyst",
    "Splunk Security Engineer",
    "Identity Management Engineer",

    # SPECIFIC ENTERPRISE ERP MODULES (Massive parallel recruitment channels)
    "SAP MM Consultant",
    "SAP SD Consultant",
    "SAP PP Consultant",
    "SAP SuccessFactors Consultant",
    "Salesforce Marketing Cloud Consultant",
    "Salesforce Service Cloud Consultant",

    # MNC SPECIFIC HIERARCHY & TITLE BANDS (Massive Volume in India)
    "Module Leader",
    "Technical Specialist",
    "Senior Technical Specialist",
    "Technology Architect",
    "Senior Technology Architect",
    "Solution Architect",
    "Principal Consultant IT",
    "Senior Consultant IT",
    "Delivery Engineer",
    "Technical Delivery Manager",
    "Associate Consultant IT",
    "Systems Engineer Trainee",
    "Operational Risk Analyst IT",

    # DEEP TECH DATA INFRASTRUCTURE & BACKEND
    "PySpark Engineer",
    "Apache Spark Engineer",
    "Flink Developer",
    "Hadoop Engineer",
    "NoSQL Developer",
    "Elasticsearch Engineer",
    "DynamoDB Developer",
    "Cassandra Developer",
    "Redis Developer",
    "Neo4j Developer",
    "Graph Database Engineer",

    # CLOUD ARCHITECTURE SPECIALIZATIONS
    "GCP Architect",
    "AWS Cloud Architect",
    "Azure Cloud Architect",
    "Multi Cloud Engineer",
    "Hybrid Cloud Engineer",
    "Cloud Migration Specialist",
    "Cloud Automation Specialist",
    "Cloud Governance Analyst",

    # MODERN JAVASCRIPT & FULL-STACK ECOSYSTEMS
    "Svelte Developer",
    "SolidJS Developer",
    "Nuxt Developer",
    "Remix Developer",
    "Gatsby Developer",
    "Electron Developer",
    "Jamstack Engineer",
    "PWA Developer",

    # FINTECH, BLOCKCHAIN & SMART INFRASTRUCTURE
    "Algorithmic Trader Developer",
    "Quant Developer",
    "Solidity Developer",
    "Rust Web3 Developer",
    "DeFi Engineer",
    "Hyperledger Developer",
    "Payment Gateway Integration Engineer",
    "Core Banking Developer",

    # TELEMETRY, OBSERVABILITY & SRE ADVANCED
    "Prometheus Engineer",
    "Grafana Specialist",
    "Datadog Specialist",
    "Splunk Engineer",
    "ELK Stack Engineer",
    "Log Analytics Specialist",
    "APM Engineer",

    # ADVANCED SECURITY & COMPLIANCE (High-Yield Niche)
    "DevSecOps Architect",
    "Application Security Lead",
    "Cloud Security Compliance Analyst",
    "Vulnerability Management Engineer",
    "SRE Security Engineer",
    "Network Security Engineer",
    "Zero Trust Architect",
    "GRC Technology Analyst",

    # TESTING & AUTOMATION NICHE FRAMEWORKS
    "Appium Automation Engineer",
    "Mobile Test Automation Engineer",
    "RestAssured Testing Engineer",
    "Cucumber Testing Engineer",
    "JMeter Performance Tester",
    "LoadRunner Test Engineer",
    "API Automation Tester",

    # INDUSTRIAL IOT, EDGE & HARDWARE-SOFTWARE INTERACTION
    "Edge Computing Engineer",
    "IoT Systems Architect",
    "MQTT Developer",
    "ROS Developer",
    "Robot Operating System Engineer",
    "Computer Vision Researcher",
    "Image Processing Engineer",

    # CRM, ERP & LOW-CODE ENTERPRISE PLATFORMS
    "Microsoft Dynamics Engineer",
    "Oracle Apps Developer",
    "NetSuite Developer",
    "Workday Studio Developer",
    "PowerApps Developer",
    "OutSystems Developer",
    "Mendix Developer",
    "Zoho Developer",

    # PRODUCTION SUPPORT & AGGRESSIVE OPERATIONS (Thousands of listings)
    "L1 Support Engineer",
    "ITSM Analyst",
    "Service Desk Analyst",
    "Application Operations Engineer",
    "Cloud Support Engineer",
    "Technical Operations Engineer",
    "Site Operations Engineer",

    # SITE RELIABILITY & ARCHITECTURE (High-Yield Corporate Titles)
    "Cloud Native Engineer",
    "Infrastructure Architect",
    "Enterprise Architect",
    "Solutions Architect",
    "Technical Architect",
    "Systems Architect",
    "Integration Architect",
    "DevOps Architect",
    "FinOps Analyst",
    "FinOps Engineer",

    # MODERN ADVANCED BACKEND & INTEGRATION
    "GraphQL Developer",
    "FastAPI Developer",
    "NestJS Developer",
    "Ruby on Rails Developer",
    "Golang Backend Engineer",
    "Scala Developer",
    "Backend Solutions Engineer",
    "Distributed Systems Engineer",

    # DEVS_EC_OPS & SITE STABILITY (Separate keywords yield different public sets)
    "DevSecOps Analyst",
    "Platform Operations Engineer",
    "Cloud Infrastructure Engineer",
    "Chaos Engineer",
    "Observability Engineer",
    "Site Reliability Analyst",

    # DATAENGINEERING & MODERN DATA STACK (MDS)
    "Data Infrastructure Engineer",
    "dbt Developer",
    "Snowflake Engineer",
    "Airflow Developer",
    "Streaming Data Engineer",
    "Kafka Developer",
    "Data Virtualization Engineer",
    "Master Data Management Specialist",

    # AI, GENERATIVE AI & ADVANCED ANALYTICS (2026 Niche Shifts)
    "AI Agents Developer",
    "Vector Database Engineer",
    "MLOps Engineer",
    "LLMOps Engineer",
    "AI Product Engineer",
    "Cognitive Engineer",
    "Deep Learning Scientist",
    "AI Model Optimization Engineer",

    # MODERN FRONTEND & CROSS-PLATFORM WEB
    "Next.js Developer",
    "TailwindCSS Developer",
    "Nuxt.js Developer",
    "Micro-Frontend Developer",
    "Web Performance Engineer",
    "Jamstack Developer",

    # QUALITY ENGINEERING & SHIFT-LEFT TESTING
    "Test Automation Specialist",
    "API Testing Engineer",
    "Performance Test Engineer",
    "Security QA Engineer",
    "Mobile Test Engineer",
    "Cypress Automation Engineer",
    "Playwright Automation Engineer",

    # ENTERPRISE CLOUD ECOSYSTEMS (Massive hiring volume in India)
    "MuleSoft Developer",
    "Pega Developer",
    "Appian Developer",
    "Workday Integration Engineer",
    "Guidewire Developer",
    "UiPath Developer",
    "RPA Developer",
    "Robotic Process Automation Engineer",

    # SECURITY OPERATIONS & DEFENSIVE TECH
    "IAM Engineer",
    "Identity and Access Management Specialist",
    "Cloud Security Architect",
    "Application Security Analyst",
    "SIEM Engineer",
    "SOAR Engineer",
    "Data Privacy Engineer",
    "DevSecOps Architect",

    # TELEMETRY & NETWORKING SHIFTS
    "SDN Engineer",
    "Software Defined Network Engineer",
    "Network Automation Engineer",
    "5G Systems Engineer",
    "Wireless Systems Engineer",

    # CORE SYSTEM ENGINEERING & INDUSTRIAL IOT
    "RTOS Developer",
    "Real-Time Systems Engineer",
    "CAN Bus Engineer",
    "Automotive Software Engineer",
    "AUTOSAR Developer",
    "PLC Programmer",
    "SCADA Engineer",

    # SERVICE DESK & OPERATIONS ADJACENCIES (Good for massive entry-level counts)
    "Application Support Specialist",
    "Production Support Engineer",
    "L2 Support Engineer",
    "L3 Technical Support",
    "IT Operations Analyst",
    "Systems Support Engineer",

    # AGREED CORPORATE ALTERNATIVES (India MNC Tier-1 Naming Standard)
    "Systems Analyst",
    "Senior Systems Analyst",
    "Module Lead",
    "Project Lead",
    "Delivery Lead",
    "Engineering Manager",
    "Associate Director Engineering",

    # Core Software Development
    "Application Developer",
    "Application Engineer",
    "Software Consultant",
    "Software Architect",
    "Technical Lead",
    "Lead Software Engineer",
    "Solutions Developer",
    "Solutions Engineer",
    "Software Specialist",
    "Technology Analyst",
    "Technology Associate",
    "Software Engineer",
    "Software Developer",
    "Associate Software Engineer",
    "Junior Software Engineer",
    "Senior Software Engineer",
    "Principal Software Engineer",
    "Python Developer",
    "Java Developer",
    "C Developer",
    "C++ Developer",
    "C# Developer",
    "Golang Developer",
    "Rust Developer",
    "PHP Developer",
    ".NET Developer",
    "Spring Boot Developer",
    "Django Developer",
    "Flask Developer",

    # Backend Variations
    "API Developer",
    "API Engineer",
    "Microservices Developer",
    "Server Side Developer",
    "Java Backend Developer",
    "Python Backend Developer",
    "Node Backend Developer",

    # Frontend Variations
    "UI Developer",
    "UI Engineer",
    "Frontend Architect",
    "React Engineer",
    "Angular Engineer",
    "JavaScript Engineer",
    "Web Application Developer",

    # Full Stack / Frontend / Backend
    "Full Stack Engineer",
    "Software Engineer Full Stack",
    "Web Application Engineer",
    "Application Engineer Full Stack",
    "Full Stack Developer",
    "MERN Stack Developer",
    "MEAN Stack Developer",
    "Frontend Developer",
    "Frontend Engineer",
    "Backend Developer",
    "Backend Engineer",
    "React Developer",
    "Angular Developer",
    "Vue.js Developer",
    "JavaScript Developer",
    "TypeScript Developer",
    "Node.js Developer",
    "Web Developer",

    # Mobile Development
    "Android Developer",
    "iOS Developer",
    "Flutter Developer",
    "React Native Developer",
    "Mobile Application Developer",

    # Data Analytics
    "Data Analytics Specialist",
    "Analytics Consultant",
    "Insights Analyst",
    "Decision Scientist",
    "Marketing Analyst",
    "Operations Analyst",
    "Product Analyst",
    "Research Analyst",
    "Reporting Specialist",
    "Analytics Specialist",
    "Data Analyst",
    "Senior Data Analyst",
    "Business Analyst",
    "Business Intelligence Analyst",
    "BI Analyst",
    "Reporting Analyst",
    "MIS Executive",
    "Data Visualization Analyst",

    # Data Engineering
    "Data Platform Engineer",
    "Data Integration Engineer",
    "Data Migration Engineer",
    "Hadoop Developer",
    "Spark Developer",
    "Big Data Developer",
    "Data Pipeline Engineer",
    "Cloud Data Engineer",
    "Data Operations Engineer",
    "Data Engineer",
    "Senior Data Engineer",
    "Big Data Engineer",
    "ETL Developer",
    "ETL Engineer",
    "Analytics Engineer",
    "Data Warehouse Engineer",
    "PySpark Developer",
    "Databricks Engineer",

    # Data Science & AI
    "Applied Scientist",
    "AI Research Engineer",
    "ML Scientist",
    "Machine Learning Scientist",
    "Predictive Analytics Specialist",
    "Quantitative Analyst",
    "AI Developer",
    "Artificial Intelligence Engineer",
    "Research Scientist AI",
    "GenAI Engineer",
    "AI Application Engineer",
    "Conversational AI Engineer",
    "AI Solutions Engineer",
    "RAG Engineer",
    "AI Platform Engineer",
    "Foundation Model Engineer",
    "Data Scientist",
    "Machine Learning Engineer",
    "AI Engineer",
    "Generative AI Engineer",
    "LLM Engineer",
    "Prompt Engineer",
    "NLP Engineer",
    "Computer Vision Engineer",
    "Deep Learning Engineer",
    "Research Engineer AI",

    # Cloud & DevOps
    "Cloud Consultant",
    "Cloud Specialist",
    "DevSecOps Engineer",
    "Release Engineer",
    "Build Engineer",
    "CI CD Engineer",
    "Kubernetes Engineer",
    "Docker Engineer",
    "Cloud Operations Engineer",
    "Cloud Administrator",
    "Systems Reliability Engineer",
    "DevOps Engineer",
    "Cloud Engineer",
    "Cloud Architect",
    "AWS Engineer",
    "AWS Developer",
    "Azure Engineer",
    "Azure Architect",
    "GCP Engineer",
    "Platform Engineer",
    "Infrastructure Engineer",
    "Site Reliability Engineer",
    "SRE Engineer",

    # Cyber Security
    "Security Engineer",
    "Cloud Security Engineer",
    "Application Security Engineer",
    "Security Consultant",
    "Threat Analyst",
    "Cyber Defense Analyst",
    "Incident Response Analyst",
    "Risk Analyst Cyber Security",
    "Cyber Security Analyst",
    "Cybersecurity Engineer",
    "Information Security Analyst",
    "Information Security Engineer",
    "SOC Analyst",
    "Security Operations Analyst",
    "Penetration Tester",
    "Ethical Hacker",
    "Vulnerability Analyst",

    # QA & Testing
    "QA Analyst",
    "Test Automation Engineer",
    "Validation Engineer",
    "Software Quality Engineer",
    "Quality Engineer",
    "Automation Engineer",
    "UAT Tester",
    "QA Engineer",
    "QA Automation Engineer",
    "Software Tester",
    "Test Engineer",
    "Automation Tester",
    "SDET",
    "Performance Tester",
    "Manual Tester",
    "Selenium Tester",
    "Quality Assurance Analyst",

    # Database
    "Database Engineer",
    "Data Base Developer",
    "SQL Analyst",
    "Database Specialist",
    "Data Warehouse Developer",
    "Database Administrator",
    "SQL Developer",
    "Oracle Developer",
    "MySQL Developer",
    "PostgreSQL Developer",
    "MongoDB Developer",

    # Networking & Systems
    "Cloud Network Engineer",
    "Infrastructure Engineer",
    "NOC Engineer",
    "IT Infrastructure Engineer",
    "Systems Administrator",
    "Network Administrator",
    "Technical Support Engineer",
    "Network Engineer",
    "Systems Engineer",
    "System Administrator",
    "Linux Administrator",
    "Infrastructure Administrator",

    # Product & Management
    "Technical Business Analyst",
    "Business Systems Analyst",
    "Digital Product Manager",
    "Product Owner",
    "Associate Product Owner",
    "Technology Project Manager",
    "Delivery Manager",
    "Product Manager",
    "Technical Product Manager",
    "Associate Product Manager",
    "Project Manager",
    "IT Project Manager",
    "Program Manager",
    "Scrum Master",
    "Agile Coach",

    # Enterprise Applications
    "SAP Technical Consultant",
    "SAP Functional Consultant",
    "Salesforce Consultant",
    "CRM Developer",
    "Dynamics 365 Developer",
    "SAP Consultant",
    "SAP ABAP Developer",
    "SAP FICO Consultant",
    "Salesforce Developer",
    "Salesforce Administrator",
    "ServiceNow Developer",

    # Embedded / Hardware
    "Embedded Developer",
    "Embedded Systems Engineer",
    "Hardware Engineer",
    "Control Systems Engineer",
    "VLSI Engineer",
    "FPGA Engineer",
    "Embedded Engineer",
    "Embedded Software Engineer",
    "Firmware Engineer",
    "Electronics Engineer",
    "Robotics Engineer",
    "IoT Engineer",

    # Emerging Technologies
    "Metaverse Developer",
    "XR Developer",
    "Unity Developer",
    "Unreal Engine Developer",
    "Crypto Developer",
    "Smart Contract Developer",
    "Blockchain Developer",
    "Web3 Developer",
    "AR VR Developer",
    "Game Developer",

    # Freshers / Entry Level
    "Software Developer Intern",
    "Developer Intern",
    "Engineering Intern",
    "Technology Intern",
    "IT Intern",
    "Data Engineering Intern",
    "Cloud Intern",
    "Cyber Security Intern",
    "Graduate Software Engineer",
    "Junior Engineer",
    "Trainee Software Engineer",
    "Trainee Data Analyst",
    "Trainee Data Engineer",
    "Associate Consultant",
    "Graduate Engineer Trainee",
    "Graduate Trainee",
    "Engineer Trainee",
    "Associate Engineer",
    "Associate Developer",
    "Junior Developer",
    "Junior Data Analyst",
    "Junior Data Engineer",
    "Junior Software Engineer",
    "Software Engineer Intern",
    "Data Science Intern",
    "Machine Learning Intern",
    "Data Analyst Intern",
]

    
    LOCATION = "India"  
    MAX_ROWS_TARGET = 30000  # Your target
    
    existing_urls = load_existing_urls(CSV_OUTPUT_PATH)
    print(f"Starting long-term script. Currently tracking {len(existing_urls)} total URLs in database.")

    for current_keyword in KEYWORDS_POOL:
        if len(existing_urls) >= MAX_ROWS_TARGET:
            print(f"\n🎉 Target goal of {MAX_ROWS_TARGET} rows reached!")
            break
            
        print(f"\n🚀 NOW SCRAPING KEYWORD: [ {current_keyword} ] in [ {LOCATION} ]")
        start_index = 0
        consecutive_no_new_jobs = 0  
        
        while len(existing_urls) < MAX_ROWS_TARGET:
            print(f"Fetching '{current_keyword}' jobs starting at index: {start_index}...")
            
            new_jobs, end_of_results = scrape_linkedin_page(current_keyword, LOCATION, start_index, existing_urls)
            
            if end_of_results:
                print(f"Reached the end of available public listings for '{current_keyword}'. Moving to next keyword.")
                break
                
            if new_jobs:
                append_to_csv(new_jobs, CSV_OUTPUT_PATH)
                print(f"Total Database Size: {len(existing_urls)} / {MAX_ROWS_TARGET} jobs.")
                consecutive_no_new_jobs = 0  
            else:
                print("No unique jobs on this page.")
                consecutive_no_new_jobs += 1
            
            if consecutive_no_new_jobs >= 4:
                print(f"Stale data loop detected for '{current_keyword}'. Moving to next keyword.")
                break

            # Advance to the next page of results
            start_index += 25
            
            # Anti-ban sleep timer
            sleep_time = random.uniform(6.0, 12.0)
            print(f"Sleeping for {sleep_time:.2f} seconds...")
            time.sleep(sleep_time)

    print(f"\n🎉 Scraping session completed. Total tracked items in CSV: {len(existing_urls)}")