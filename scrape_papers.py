import re, json, pandas as pd, time, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

URL = "https://seed.bytedance.com/zh/public_papers?view_from=research"
OUT = Path("data"); OUT.mkdir(exist_ok=True)

CARD = "div.paper-card"          # 实测可用；若之后改版再调

def crawl():
    rows = []
    with sync_playwright() as p:
        page = p.chromium.launch(headless=True).new_page()
        page.goto(URL, wait_until="networkidle")
        page.wait_for_selector(CARD, timeout=15000)

        # 懒加载：多滚几屏
        for _ in range(4):
            page.mouse.wheel(0, 5000)
            time.sleep(0.8)

        for c in page.query_selector_all(CARD):
            txt = c.inner_text().strip()          # 整段文字
            m = re.search(r"\d{4}-\d{2}-\d{2}", txt)
            if not m:
                print("⚠️  no date, skip"); continue
            date = m.group(0)
            rest = txt.replace(date, "").strip()
            title = rest.split("\n",1)[0]         # 第一行即标题
            link  = c.query_selector("a").get_attribute("href")
            rows.append({"date": date, "title": title, "link": link})
    print("✅  captured", len(rows), "rows")
    return rows

def to_monthly(rows):
    df = pd.DataFrame(rows)
    df["month"] = pd.to_datetime(df["date"]).dt.to_period("M").astype(str)
    return df.groupby("month").size().to_dict()

if __name__ == "__main__":
    papers = crawl()
    if not papers:
        sys.exit("❌  crawl got 0 rows – selector/anti-bot?")
    Path("data/papers_raw.json").write_text(json.dumps(papers, ensure_ascii=False, indent=2))
    Path("data/monthly_counts.json").write_text(json.dumps(to_monthly(papers), indent=2))
