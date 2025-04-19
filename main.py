import time
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

YOUTUBE_URL = 'https://www.youtube.com/watch?v=9Csd_qZyt3c&t=437s&ab_channel=VarunMayya'

def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--log-level=3")
    return webdriver.Chrome(options=options)

def scroll_to_load_comments(driver, max_comments=5000):
    driver.get(YOUTUBE_URL)
    time.sleep(5)

    driver.execute_script("window.scrollTo(0, 500);")
    time.sleep(3)

    last_height = driver.execute_script("return document.documentElement.scrollHeight")
    comments_collected = 0
    loops = 0

    while comments_collected < max_comments and loops < 5000:
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(3)
        new_height = driver.execute_script("return document.documentElement.scrollHeight")

        if new_height == last_height:
            break
        last_height = new_height
        loops += 1

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        comments_collected = len(soup.select("#content #content-text"))
        print(f"Loaded {comments_collected} comments...")

    return soup

def extract_comments_with_superthanks(soup):
    comments = soup.select("ytd-comment-thread-renderer")
    result = []

    for comment in comments:
        content = comment.select_one("#content-text")
        author = comment.select_one("#author-text span")
        price_elem = comment.select_one("#comment-chip-price")

        text = content.text.strip() if content else ""
        name = author.text.strip() if author else ""
        super_thanks_amount = price_elem.text.strip() if price_elem else ""

        result.append({
            'author': name,
            'comment': text,
            'super_thanks_amount': super_thanks_amount
        })

    return result

if __name__ == "__main__":
    driver = get_driver()
    try:
        soup = scroll_to_load_comments(driver, max_comments=5000)
        all_comments = extract_comments_with_superthanks(soup)

        json_output_path = "youtube_superthanks_comments2.json"
        with open(json_output_path, "w", encoding="utf-8") as f:
            json.dump(all_comments, f, indent=2, ensure_ascii=False)

        print(f"✅ Done! Extracted {len(all_comments)} comments.")
        print(f"💾 Saved to {json_output_path}")

    finally:
        driver.quit()
