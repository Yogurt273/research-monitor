import json
import feedparser             # pip install feedparser
import pandas as pd
from pathlib import Path

# 输出目录
OUT = Path("data"); OUT.mkdir(exist_ok=True)

# arXiv API：查询 cs.AI （人工智能）分类，最新 200 篇
API_URL = (
    "http://export.arxiv.org/api/query?"
    "search_query=cat:cs.AI&"
    "start=0&max_results=200&"
    "sortBy=submittedDate&sortOrder=descending"
)

def crawl():
    feed = feedparser.parse(API_URL)
    rows = []
    for e in feed.entries:
        date = e.published[:10]         # 取 YYYY-MM-DD
        title = e.title.strip().replace("\n"," ")
        link  = e.link
        rows.append({"date": date, "title": title, "link": link})
    print(f"✅  fetched {len(rows)} entries")
    return rows

def to_monthly(rows):
    df = pd.DataFrame(rows)
    df["month"] = pd.to_datetime(df["date"]).dt.to_period("M").astype(str)
    return df.groupby("month").size().to_dict()

if __name__ == "__main__":
    papers = crawl()
    # 写入文件
    Path("data/papers_raw.json").write_text(
        json.dumps(papers, ensure_ascii=False, indent=2)
    )
    Path("data/monthly_counts.json").write_text(
        json.dumps(to_monthly(papers), indent=2)
    )
    print("🎉  done")
