import os
import csv
import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# Define output path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_OUTPUT_PATH = os.path.join(CURRENT_DIR, "naukri_live_jobs.csv")

def scrape_naukri_live(keyword, location):
    # Formulate URL
    # Replace spaces with hyphens for the URL pattern
    keyword_url = keyword.lower().replace(" ", "-")
    location_url = location.lower().replace(" ", "-")
    
    if location_url:
        url = f"https://www.naukri.com/{keyword_url}-jobs-in-{location_url}"
    else:
        url = f"https://www.naukri.com/{keyword_url}-jobs"

    print(f"Navigating to: {url}")
    jobs_data = []

    with sync_playwright() as p:
        # Launch browser with headless=False to mimic a human user and show the window
        browser = p.chromium.launch(headless=False)
        
        # Create a browser context with custom user agent and viewport to mimic real user
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        
        page = context.new_page()
        
        try:
            # Navigate to the page
            page.goto(url, wait_until="load", timeout=30000)
            
            # Wait for job cards to render on the page
            print("Waiting for job listings to load...")
            page.wait_for_selector("div.srp-jobtuple-wrapper", timeout=15000)
            
            # Scroll down slowly to trigger lazy loading of elements if needed
            page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
            time.sleep(1.0)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1.0)

            # Get the page source HTML
            html = page.content()
            soup = BeautifulSoup(html, "html.parser")
            
            # Find all job cards
            job_cards = soup.select("div.srp-jobtuple-wrapper")
            print(f"Found {len(job_cards)} job listings.")

            for card in job_cards:
                # 1. Job Title & URL
                title_element = card.select_one("a.title")
                title = title_element.get_text(strip=True) if title_element else "N/A"
                job_url = title_element["href"] if title_element and title_element.has_attr("href") else "N/A"
                
                # 2. Company Name
                company_element = card.select_one("a.comp-name")
                company = company_element.get_text(strip=True) if company_element else "N/A"

                # 3. City/Location
                # Often loc-wrap contains the city names inside span elements
                city_element = card.select_one("span.loc-wrap, .locWdth")
                city = city_element.get_text(strip=True) if city_element else "N/A"

                # 4. Salary
                salary_element = card.select_one("span.sal-wrap, .sal")
                salary = salary_element.get_text(strip=True) if salary_element else "Not Disclosed"

                # 5. Job Description snippet
                jd_element = card.select_one("span.job-desc, .jobSnippet, .jd-snippet")
                jd = jd_element.get_text(strip=True) if jd_element else "N/A"

                jobs_data.append({
                    "title": title,
                    "company": company,
                    "job_url": job_url,
                    "city": city,
                    "salary": salary,
                    "job_description": jd
                })

        except Exception as e:
            print(f"Error occurred during live scraping: {e}")
            screenshot_path = os.path.join(CURRENT_DIR, "error_screenshot.png")
            try:
                page.screenshot(path=screenshot_path)
                print(f"Saved a screenshot of the page at: {screenshot_path}")
            except Exception as se:
                print(f"Could not save screenshot: {se}")
            print("Note: Naukri may have detected the automated request (e.g. CAPTCHA) or class names might have updated.")
        
        finally:
            browser.close()

    return jobs_data

def save_to_csv(data, filename):
    if not data:
        print("No job data extracted.")
        return

    keys = data[0].keys()
    with open(filename, "w", newline="", encoding="utf-8") as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)
    print(f"Successfully saved {len(data)} jobs to:")
    print(f"  --> {filename}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        keyword = sys.argv[1]
        location = sys.argv[2] if len(sys.argv) > 2 else ""
    else:
        keyword = input("Enter job title / keyword (e.g., Python Developer): ")
        location = input("Enter location (e.g., Bangalore) [Leave blank for any]: ")
    
    print(f"\nStarting live scraping for '{keyword}' in '{location or 'any location'}'...")
    results = scrape_naukri_live(keyword, location)
    save_to_csv(results, CSV_OUTPUT_PATH)
