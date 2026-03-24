import os
from datetime import datetime

import feedparser
import pandas as pd
from crewai.tools import BaseTool

# Public financial news RSS feeds — no API keys required
RSS_FEEDS = {
    "CNBC":          "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "MarketWatch":   "https://feeds.marketwatch.com/marketwatch/topstories/",
    "Yahoo Finance": "https://finance.yahoo.com/news/rssindex",
    "Seeking Alpha": "https://seekingalpha.com/market_currents.xml",
}

LIVE_RAW_PATH = "data/raw/live_news.csv"


class FinancialNewsWebTool(BaseTool):
    name: str = "financial_news_web_tool"
    description: str = (
        "Fetches live financial news headlines from public RSS feeds "
        "(CNBC, MarketWatch, Reuters, Yahoo Finance). "
        "Accepts an optional max_articles integer (default 30). "
        "Saves results to data/raw/live_news.csv and returns the file path "
        "along with a summary of how many articles were fetched per source."
    )

    def _run(self, max_articles: int = 30) -> str:
        records = []
        per_source = max_articles // len(RSS_FEEDS)
        source_counts = {}

        for source, url in RSS_FEEDS.items():
            try:
                feed = feedparser.parse(url)
                entries = feed.entries[:per_source]
                for entry in entries:
                    records.append({
                        "headline":  entry.get("title", "").strip(),
                        "content":   entry.get("summary", entry.get("description", "")).strip(),
                        "timestamp": self._parse_date(entry),
                        "source":    source,
                    })
                source_counts[source] = len(entries)
            except Exception as e:
                source_counts[source] = f"failed ({e})"

        if not records:
            if os.path.exists(LIVE_RAW_PATH):
                return (
                    f"Failed to fetch live news from all RSS feeds. "
                    f"Falling back to existing data at {LIVE_RAW_PATH}."
                )
            return "Failed to fetch news from all RSS feeds and no existing data found. Check network connectivity."

        df = pd.DataFrame(records)
        # Drop rows where headline is empty
        df = df[df["headline"].str.len() > 0].reset_index(drop=True)

        os.makedirs("data/raw", exist_ok=True)
        df.to_csv(LIVE_RAW_PATH, index=False)

        summary_lines = [f"Fetched {len(df)} articles. Saved to {LIVE_RAW_PATH}."]
        for src, count in source_counts.items():
            summary_lines.append(f"  {src}: {count}")
        return "\n".join(summary_lines)

    @staticmethod
    def _parse_date(entry) -> str:
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            try:
                return datetime(*entry.published_parsed[:6]).isoformat()
            except Exception:
                pass
        return datetime.now().isoformat()
