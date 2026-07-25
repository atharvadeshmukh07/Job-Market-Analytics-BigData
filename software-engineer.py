from playwright.sync_api import sync_playwright
from seleniumbase import sb_cdp
import csv
import os
import time

csv_file = "software-engineer.csv"

headers = [
    "job_title",
    "company",
    "location",
    "salary",
    "employment_type",
    "skills",
    "experience",
    "benefits",
    "application_link",
    "job_url",
]

file_exists = os.path.exists(csv_file)

sb = sb_cdp.Chrome(locale="en")
endpoint_url = sb.get_endpoint_url()


def safe_goto(page, url):
    for _ in range(3):
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(2000)
            return True
        except:
            time.sleep(2)
    return False


with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(endpoint_url)
    context = browser.contexts[0] if browser.contexts else browser.new_context()
    page = context.pages[0] if context.pages else context.new_page()

    base_url = "https://wellfound.com/role/software-engineer"
    page_num = 26

    with open(csv_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)

        if not file_exists:
            writer.writeheader()

        while True:
            print(f"\n================ PAGE {page_num} ================\n")

            # -----------------------------
            # LOAD PAGE
            # -----------------------------
            page.goto(
                base_url if page_num == 1 else f"{base_url}?page={page_num}",
                wait_until="domcontentloaded",
            )
            page.wait_for_timeout(5000)

            # -----------------------------
            # SCROLL TO LOAD JOBS
            # -----------------------------
            for _ in range(10):
                page.mouse.wheel(0, 5000)
                page.wait_for_timeout(1200)

            # -----------------------------
            # COLLECT JOB LINKS
            # -----------------------------
            job_links = page.locator("a[href*='/jobs/']")
            urls = set()

            for i in range(job_links.count()):
                href = job_links.nth(i).get_attribute("href")
                if href and "/jobs/" in href:
                    if href.startswith("/"):
                        href = "https://wellfound.com" + href
                    urls.add(href)

            print("Jobs found on page:", len(urls))

            # STOP if no jobs
            if len(urls) == 0:
                print("No jobs found. Stopping.")
                break

            # -----------------------------
            # SCRAPE EACH JOB
            # -----------------------------
            for url in urls:
                try:
                    job_page = context.new_page()

                    if not safe_goto(job_page, url):
                        job_page.close()
                        continue

                    job = {
                        "job_title": "",
                        "company": "",
                        "location": "",
                        "salary": "",
                        "employment_type": "",
                        "skills": "",
                        "experience": "",
                        "benefits": "",
                        "application_link": job_page.url,
                        "job_url": url,
                    }

                    # TITLE
                    try:
                        job["job_title"] = job_page.locator("h1").inner_text().strip()
                    except:
                        pass

                    # COMPANY
                    try:
                        job["company"] = job_page.locator("a[href*='/company/'] span").inner_text().strip()
                    except:
                        pass

                    # SALARY
                    try:
                        job["salary"] = job_page.locator("text=/\\$[0-9]+k?/").first.inner_text().strip()
                    except:
                        pass

                    # EXPERIENCE
                    try:
                        job["experience"] = job_page.locator("text=/[0-9]+ years of exp/").first.inner_text().strip()
                    except:
                        pass

                    # EMPLOYMENT TYPE
                    for t in ["Full Time", "Part Time", "Contract", "Internship"]:
                        if job_page.locator(f"text={t}").count() > 0:
                            job["employment_type"] = t
                            break

                    # LOCATION
                    try:
                        loc = job_page.locator("text=Remote").first
                        job["location"] = loc.locator("..").inner_text().replace("\n", " ").strip()
                    except:
                        pass

                    # BENEFITS
                    try:
                        if job_page.locator("text=Benefits").count() > 0:
                            job["benefits"] = job_page.locator("text=Benefits").locator("..").inner_text().strip()
                    except:
                        pass

                    # SKILLS
                    try:
                        skills_elements = job_page.locator("div.flex.flex-wrap div")
                        skills_list = skills_elements.all_inner_texts()
                        skills_list = list(set([s.strip() for s in skills_list if s.strip()]))
                        job["skills"] = ", ".join(skills_list)
                    except:
                        job["skills"] = ""

                    writer.writerow(job)
                    f.flush()

                    print("Saved:", job["job_title"] or url)

                    job_page.close()

                except Exception as e:
                    print("Failed:", url, e)

            # -----------------------------
            # NEXT PAGE CHECK
            # -----------------------------
            next_btn = page.locator("a[aria-label='Next page']")

            if next_btn.count() == 0:
                print("No next page button. Done.")
                break

            next_href = next_btn.get_attribute("href")

            if not next_href:
                print("Next page disabled. Done.")
                break

            page_num += 1
            time.sleep(2)

print("DONE")