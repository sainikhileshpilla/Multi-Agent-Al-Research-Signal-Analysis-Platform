from datetime import datetime

import pandas as pd


REQUIRED_COLUMNS = ["headline", "content", "timestamp", "source"]


def validate_schema(df: pd.DataFrame) -> None:
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    print("Schema validation passed.")


def parse_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    """Parse timestamp with a few common formats before fallback parsing."""
    df = df.copy()

    formats = ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y", "%m/%d/%Y"]

    for fmt in formats:
        try:
            df["timestamp"] = pd.to_datetime(df["timestamp"], format=fmt)
            return df
        except Exception:
            continue

    try:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    except Exception:
        print("Warning: Could not parse all timestamps; using current date")
        df["timestamp"] = datetime.now()

    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    initial = len(df)

    df = df.drop_duplicates()
    df = df.dropna(subset=["headline", "content"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])

    final = len(df)
    print(f"Cleaned data: {initial} -> {final}")
    return df


def validate_and_clean(df: pd.DataFrame) -> pd.DataFrame:
    """Validate schema and clean dataset in one step."""
    validate_schema(df)
    df = parse_timestamps(df)
    df = df.drop_duplicates(subset=["headline", "source"], keep="first")
    df = df.dropna(subset=["headline", "content"])
    return df[REQUIRED_COLUMNS]


def save_processed(df: pd.DataFrame, path: str) -> None:
    df.to_csv(path, index=False)
    print(f"Saved processed data to {path}")
