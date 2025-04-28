import json, pandas as pd
from pathlib import Path
from playwright.sync_api import sync_playwright

URL = "https://seed.bytedance.com/zh/public_papers?view_from=research"
OUT_DIR = Path("data"); OUT_DIR.mkdir(exist_ok=True)

title_sel = "div.paper-card h4"     # 若抓不到，F12 看实际 DOM 再改
date_sel  = "div.paper-card span.date"

def crawl():
    with sync_playwright() as p:
        page = p.chromium.launch(headless=True).new_page()
        page.goto(URL, wait_until="networkidle")
        cards = page.query_selector_all("div.paper-card")
        rows = []
        for c in cards:
            rows.append({
                "title": c.query_selector(title_sel).inner_text().strip(),
                "date" : c.query_selector(date_sel ).inner_text().strip(),
                "link" : c.query_selector("a").get_attribute("href")
            })
        return rows

def monthly(rows):
    import pandas as pd
    df = pd.DataFrame(rows)
    df["month"] = pd.to_datetime(df["date"]).dt.to_period("M").astype(str)
    return df.groupby("month").size().to_dict()

if __name__ == "__main__":
    rows = crawl()
    Path("data/papers_raw.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2))
    Path("data/monthly_counts.json").write_text(json.dumps(monthly(rows), indent=2))
    print("Scraped", len(rows), "papers")
