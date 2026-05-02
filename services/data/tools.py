from datetime import datetime

import feedparser
import pandas as pd
from crewai.tools import BaseTool

from services.data.ingestion import load_all_from_directory
from services.data.validation import save_processed, validate_and_clean
from services.ml.monitoring.logger import log_ingestion
from source_code.paths import LIVE_NEWS_PATH, resolve_path


RSS_FEEDS = {
    "CNBC": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "MarketWatch": "https://feeds.marketwatch.com/marketwatch/topstories/",
    "Yahoo Finance": "https://finance.yahoo.com/news/rssindex",
    "Seeking Alpha": "https://seekingalpha.com/market_currents.xml",
}

LIVE_RAW_PATH = str(LIVE_NEWS_PATH)


class CSVReaderTool(BaseTool):
    name: str = "csv_reader_tool"
    description: str = (
        "Reads a CSV file from the given path and returns a summary of its contents, "
        "including column names, row count, and the first few records as a formatted table."
    )

    def _run(self, file_path: str) -> str:
        try:
            df = pd.read_csv(resolve_path(file_path))
            summary = (
                f"Rows: {len(df)}\n"
                f"Columns: {list(df.columns)}\n\n"
                f"First 10 records:\n{df.head(10).to_string(index=False)}"
            )
            return summary
        except Exception as exc:
            return f"Failed to read CSV: {str(exc)}"


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
                    records.append(
                        {
                            "headline": entry.get("title", "").strip(),
                            "content": entry.get("summary", entry.get("description", "")).strip(),
                            "timestamp": self._parse_date(entry),
                            "source": source,
                        }
                    )
                source_counts[source] = len(entries)
            except Exception as exc:
                source_counts[source] = f"failed ({exc})"

        if not records:
            if LIVE_NEWS_PATH.exists():
                return (
                    "Failed to fetch live news from all RSS feeds. "
                    f"Falling back to existing data at {LIVE_RAW_PATH}."
                )
            return "Failed to fetch news from all RSS feeds and no existing data found. Check network connectivity."

        df = pd.DataFrame(records)
        df = df[df["headline"].str.len() > 0].reset_index(drop=True)

        LIVE_NEWS_PATH.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(LIVE_NEWS_PATH, index=False)

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


class DataPipelineTool(BaseTool):
    name: str = "data_pipeline_tool"
    description: str = (
        "Loads raw financial news data, validates schema, cleans it, "
        "saves structured output, and logs ingestion metadata."
    )

    def _run(
        self,
        input_path: str = "data/raw",
        output_path: str = "data/processed/news_cleaned.csv",
    ) -> str:
        try:
            resolved_input = resolve_path(input_path)
            resolved_output = resolve_path(output_path)

            df = load_all_from_directory(str(resolved_input))
            if df.empty:
                return f"No data found in {resolved_input}"

            df_clean = validate_and_clean(df)
            if df_clean.empty:
                return "All records were filtered out during validation"

            save_processed(df_clean, str(resolved_output))
            log_ingestion(len(df_clean), str(resolved_output))

            return f"Successfully processed {len(df_clean)} records from multiple sources."

        except Exception as exc:
            return f"Pipeline failed: {str(exc)}"
