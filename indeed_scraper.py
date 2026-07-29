import os
import shutil
import time
import pandas as pd
from seleniumbase import sb_cdp
from playwright.sync_api import sync_playwright

# --- CONFIGURATION ---
CSV_FILE = "indeed_jobs.csv"
BACKUP_FILE = "indeed_jobs_backup.csv"
PAGES_TRACKER_FILE = "scraped_pages.txt"
BASE_URL = "https://in.indeed.com/jobs?q=data+analyst&l=Hyderabad%2C+Telangana&radius=25"
MAX_RUNTIME_SECONDS = 5 * 60 * 60  # run for 5 hours, no record cap


# --- DATA PERSISTENCE HELPERS ---

def get_already_scraped_jobs():
    """Deduplication disabled: always returns an empty set so every job is kept,
    including duplicates across runs."""
    return set()


def save_and_backup(row):
    """Saves a single row immediately and creates a backup of the file."""
    file_exists = os.path.exists(CSV_FILE)
    pd.DataFrame([row]).to_csv(
        CSV_FILE,
        mode="a",
        header=not file_exists,
        index=False,
        encoding="utf-8-sig"
    )
    # Create an instant backup copy
    try:
        shutil.copy2(CSV_FILE, BACKUP_FILE)
    except Exception as e:
        print(f"Backup Error: {e}")


def get_saved_record_count():
    """Counts how many rows are already saved (for logging/progress only)."""
    if os.path.exists(CSV_FILE):
        try:
            return len(pd.read_csv(CSV_FILE))
        except Exception as e:
            print(f"Warning: Could not count existing rows: {e}")
    return 0


def get_scraped_pages():
    """Reads the text file to see which page numbers are already done."""
    if os.path.exists(PAGES_TRACKER_FILE):
        with open(PAGES_TRACKER_FILE, "r") as f:
            return set(int(p) for p in f.read().split(",") if p.strip())
    return set()


def update_page_tracker(page_no):
    """Marks a page as completed in the tracker file."""
    pages = get_scraped_pages()
    pages.add(page_no)
    with open(PAGES_TRACKER_FILE, "w") as f:
        f.write(",".join(map(str, sorted(list(pages)))))


def format_elapsed(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


# --- MAIN SCRAPER ---

def run_scraper():
    scraped_pages = get_scraped_pages()
    seen_jobs = get_already_scraped_jobs()
    total_saved = get_saved_record_count()
    start_time = time.time()
    print(f"Starting with {total_saved} records already saved. "
          f"Will run for up to {format_elapsed(MAX_RUNTIME_SECONDS)} (HH:MM:SS).")

    # Launch Chrome via SeleniumBase CDP
    sb = sb_cdp.Chrome(locale="en")
    endpoint_url = sb.get_endpoint_url()
    browser = None

    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(endpoint_url)
            # Indeed works better with the first existing page
            page = browser.contexts[0].pages[0]

            try:
                page_no = 1
                while True:
                    elapsed = time.time() - start_time
                    if elapsed >= MAX_RUNTIME_SECONDS:
                        print(f"\n⏰ Time limit reached ({format_elapsed(elapsed)} elapsed). Stopping.")
                        break

                    print(f"\n{'=' * 30}\nPROCESSING PAGE: {page_no}  "
                          f"(elapsed {format_elapsed(elapsed)})\n{'=' * 30}")

                    if page_no in scraped_pages:
                        print(f"Skipping page {page_no} (already completed).")
                        page_no += 1
                        continue

                    # Construct Pagination URL
                    url = BASE_URL if page_no == 1 else BASE_URL + f"&start={(page_no - 1) * 10}"
                    page.goto(url, timeout=60000)

                    # Check for Security/Login Wall
                    if "secure.indeed.com" in page.url or "auth" in page.url:
                        print("ACTION REQUIRED: Solve Captcha or Login in the browser...")
                        input("Once you see the job list again, press Enter here to continue...")

                    page.wait_for_timeout(4000)

                    cards_selector = "div.job_seen_beacon"
                    try:
                        page.wait_for_selector(cards_selector, timeout=10000)
                    except:
                        print("No jobs found on this page. Indeed's own results limit may have been "
                              "reached for this query — restarting from page 1 to pick up new listings.")
                        page_no = 1
                        page.wait_for_timeout(5000)
                        continue

                    # Count jobs on current page
                    count = page.locator(cards_selector).count()
                    print(f"Found {count} jobs on page {page_no}")

                    for i in range(count):
                        elapsed = time.time() - start_time
                        if elapsed >= MAX_RUNTIME_SECONDS:
                            print(f"⏰ Time limit reached mid-page ({format_elapsed(elapsed)} elapsed). Stopping.")
                            break

                        try:
                            # 1. Handle Popups (Indeed often shows a 'Job Alert' popup mid-scrape)
                            try:
                                close_popup = page.locator('button[aria-label="close"], button.icl-CloseButton')
                                if close_popup.first.is_visible():
                                    close_popup.first.click()
                            except:
                                pass

                            # 2. Re-locate card and Click
                            # We re-fetch locator inside loop to avoid 'stale element' errors
                            current_card = page.locator(cards_selector).nth(i)
                            current_card.scroll_into_view_if_needed()
                            page.wait_for_timeout(500)

                            # Click with a shorter timeout and 'force' to bypass overlay blocks
                            current_card.click(force=True, timeout=8000)

                            # Wait for right-side panel to load content
                            page.wait_for_timeout(2500)

                            # 3. Data Extraction
                            def get_text(sel):
                                try:
                                    return page.locator(sel).first.inner_text(timeout=4000).strip()
                                except:
                                    return "N/A"

                            title = get_text('[data-testid="jobsearch-JobInfoHeader-title"]')
                            company = get_text('[data-testid="inlineHeader-companyName"]')

                            # 4. Skip only if extraction genuinely failed (duplicates are kept)
                            if title == "N/A":
                                print(f"  - Job {i + 1}: Skipping (empty title)")
                                continue

                            # 5. Build Row and Save Immediately
                            row = {
                                "Page": page_no,
                                "Title": title,
                                "Company": company,
                                "Location": get_text('[data-testid="inlineHeader-companyLocation"]'),
                                "Salary": get_text("#salaryInfoAndJobType"),
                                "Description": get_text("#jobDescriptionText")
                            }

                            save_and_backup(row)
                            total_saved += 1
                            print(f"  ✅ Saved Job {i + 1}: {title} at {company}  |  Total saved: {total_saved}")

                        except Exception as e:
                            print(f"  ⚠️ Error on Job {i + 1}: {e}")
                            # Move to next job instead of crashing the whole page
                            continue

                    # Finished current page
                    update_page_tracker(page_no)
                    page_no += 1

            except KeyboardInterrupt:
                print("\nManual stop detected. All data saved.")
            except Exception as e:
                print(f"\nCRITICAL ERROR: {e}")
            finally:
                # Close the browser here, while Playwright's event loop is still alive
                try:
                    browser.close()
                except Exception as e:
                    print(f"Browser close warning: {e}")

    finally:
        # sb.driver.quit() happens outside the Playwright context, which is fine
        # since it's a separate SeleniumBase-managed process, not the Playwright loop
        try:
            sb.driver.quit()
        except Exception as e:
            print(f"SeleniumBase quit warning: {e}")

    total_elapsed = time.time() - start_time
    print(f"\nDone. Ran for {format_elapsed(total_elapsed)}. Total records saved: {total_saved}")


if __name__ == "__main__":
    run_scraper()