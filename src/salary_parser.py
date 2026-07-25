import re

def parse_salary_to_lpa(raw_salary, default_usd_to_inr=85.0):
    """
    Parses diverse salary strings into (min_lpa: float, max_lpa: float, avg_lpa: float).
    Returns (None, None, None) if undisclosed or unparseable.
    """
    if not isinstance(raw_salary, str) or not raw_salary.strip():
        return None, None, None

    text = raw_salary.lower().replace(',', '').replace('₹', '').replace('rs', '').strip()
    
    if any(nd in text for nd in ['not disclosed', 'undisclosed', 'nan', 'none', 'not specified']):
        return None, None, None

    # Currency detection
    is_usd = '$' in raw_salary or 'usd' in text
    multiplier_currency = (default_usd_to_inr / 100000.0) if is_usd else 1.0

    # Pattern 1: X - Y Lacs / LPA / PA (e.g., 5-10 Lacs PA, 3.5 - 6 LPA)
    match_lpa_range = re.search(r'([\d\.]+)\s*[\-\–\to]+\s*([\d\.]+)\s*(?:lacs|lakhs|lpa|lac)', text)
    if match_lpa_range:
        low = float(match_lpa_range.group(1))
        high = float(match_lpa_range.group(2))
        avg = round((low + high) / 2.0, 2)
        return round(low, 2), round(high, 2), avg

    # Pattern 2: Single LPA value (e.g., 8 LPA, 12 Lacs)
    match_single_lpa = re.search(r'([\d\.]+)\s*(?:lacs|lakhs|lpa|lac)', text)
    if match_single_lpa:
        val = float(match_single_lpa.group(1))
        return round(val, 2), round(val, 2), round(val, 2)

    # Pattern 3: Full Rupee / Digit Ranges (e.g., 300000 - 480000 a year / PA)
    match_digit_range = re.search(r'(\d+(?:\.\d+)?)\s*[\-\–\to]+\s*(\d+(?:\.\d+)?)', text)
    if match_digit_range:
        try:
            val1 = float(match_digit_range.group(1))
            val2 = float(match_digit_range.group(2))

            # Check if USD 'k' format (e.g., 125k - 222k)
            if 'k' in text:
                val1 *= 1000.0
                val2 *= 1000.0

            # Monthly check
            if 'month' in text or 'pm' in text:
                val1 *= 12
                val2 *= 12

            # Convert to LPA
            if is_usd or 'k' in text:
                lpa1 = (val1 * default_usd_to_inr) / 100000.0
                lpa2 = (val2 * default_usd_to_inr) / 100000.0
            else:
                lpa1 = val1 / 100000.0 if val1 > 100 else val1
                lpa2 = val2 / 100000.0 if val2 > 100 else val2

            low = round(min(lpa1, lpa2), 2)
            high = round(max(lpa1, lpa2), 2)
            avg = round((low + high) / 2.0, 2)
            return low, high, avg
        except ValueError:
            pass

    # Pattern 4: Single digit amount (e.g., 500000 a year, $120k)
    match_single_digit = re.search(r'(\d+(?:\.\d+)?)', text)
    if match_single_digit:
        try:
            val = float(match_single_digit.group(1))
            if 'k' in text:
                val *= 1000.0
            if 'month' in text or 'pm' in text:
                val *= 12

            if is_usd or 'k' in text:
                lpa = (val * default_usd_to_inr) / 100000.0
            else:
                lpa = val / 100000.0 if val > 100 else val

            lpa = round(lpa, 2)
            return lpa, lpa, lpa
        except ValueError:
            pass

    return None, None, None


if __name__ == "__main__":
    samples = [
        "₹3,00,000 - ₹4,80,000 a year",
        "5-10 Lacs PA",
        "12 - 18 LPA",
        "₹ 10,00,000 - 15,00,000 PA",
        "₹50,000 a month",
        "$125k – $222k",
        "Not Disclosed"
    ]
    for s in samples:
        print(f"'{s}' -> {parse_salary_to_lpa(s)}")
