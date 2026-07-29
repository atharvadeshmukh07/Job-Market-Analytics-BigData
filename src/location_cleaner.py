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
