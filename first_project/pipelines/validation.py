import pandas as pd
from datetime import datetime

REQUIRED_COLUMNS = ["headline", "content", "timestamp", "source"]

def validate_schema(df: pd.DataFrame):
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    print("Schema validation passed.")

def parse_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    """Parse timestamp column intelligently (handles multiple formats)."""
    df = df.copy()
    
    # Try common datetime formats
    formats = ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y", "%m/%d/%Y"]
    
    for fmt in formats:
        try:
            df["timestamp"] = pd.to_datetime(df["timestamp"], format=fmt)
            return df
        except:
            continue
    
    # Fallback: try pandas' infer_datetime_format
    try:
        df["timestamp"] = pd.to_datetime(df["timestamp"], infer_datetime_format=True)
    except:
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
    print(f"Cleaned data: {initial} → {final}")

    return df

def validate_and_clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate schema and clean the dataset in one step.
    """
    validate_schema(df)
    df = parse_timestamps(df)
    df = df.drop_duplicates(subset=["headline", "source"], keep="first")
    df = df.dropna(subset=["headline", "content"])
    
    return df[REQUIRED_COLUMNS]

def save_processed(df: pd.DataFrame, path: str):
    df.to_csv(path, index=False)
    print(f"Saved processed data to {path}")
