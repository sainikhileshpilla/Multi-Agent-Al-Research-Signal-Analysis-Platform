import pandas as pd
from pathlib import Path
import pdfplumber


def read_csv(file_path: str) -> pd.DataFrame:
    """Read CSV file."""
    return pd.read_csv(file_path)


def read_excel(file_path: str) -> pd.DataFrame:
    """Read Excel file (.xlsx, .xls)."""
    return pd.read_excel(file_path)


def read_pdf(file_path: str) -> pd.DataFrame:
    """Read PDF and extract tables/text into a DataFrame."""
    rows = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            if tables:
                for table in tables:
                    for row in table:
                        rows.append(row)
            else:
                text = page.extract_text()
                if text:
                    rows.append({"content": text})
    
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def normalize_columns(df: pd.DataFrame, source_type: str) -> pd.DataFrame:
    """
    Normalize columns to standard format: headline, content, timestamp, source.
    Handles different naming conventions from different sources.
    """
    df = df.copy()
    
    # Map common column names to standard names
    column_mapping = {
        "title": "headline",
        "text": "content",
        "body": "content",
        "date": "timestamp",
        "published_at": "timestamp",
        "news": "headline",
        "article": "content",
    }
    
    df.rename(columns=column_mapping, inplace=True)
    
    # Ensure required columns exist
    required_cols = ["headline", "content", "timestamp", "source"]
    for col in required_cols:
        if col not in df.columns:
            if col == "source":
                df[col] = source_type
            else:
                df[col] = ""
    
    return df[required_cols]


def load_single_file(file_path: str, source_type: str = None) -> pd.DataFrame:
    """
    Load a single file (CSV/Excel/PDF) and normalize columns.
    
    Args:
        file_path: Path to the file
        source_type: Optional source identifier (e.g., 'reuters', 'earnings_reports')
                    If None, uses filename
    
    Returns:
        Normalized DataFrame
    """
    file_path = Path(file_path)
    suffix = file_path.suffix.lower()
    
    if source_type is None:
        source_type = file_path.stem
    
    if suffix == ".csv":
        df = read_csv(file_path)
    elif suffix in [".xlsx", ".xls"]:
        df = read_excel(file_path)
    elif suffix == ".pdf":
        df = read_pdf(file_path)
    else:
        raise ValueError(f"Unsupported file format: {suffix}")
    
    return normalize_columns(df, source_type)


def load_all_from_directory(
    data_dir: str = "data/raw",
    file_pattern: str = "*",
    exclude_patterns: list = None
) -> pd.DataFrame:
    """
    Load all CSV/Excel/PDF files from a directory and combine them.
    Uses filename stem as source identifier.
    
    Args:
        data_dir: Directory containing raw files
        file_pattern: Glob pattern (default: "*" loads all)
        exclude_patterns: List of patterns to skip (e.g., ["sample_*", "test_*"])
    
    Returns:
        Combined DataFrame with all sources
    """
    if exclude_patterns is None:
        exclude_patterns = []
    
    data_path = Path(data_dir)
    dfs = []
    
    # Collect all supported file types
    for suffix in [".csv", ".xlsx", ".xls", ".pdf"]:
        for file in data_path.glob(f"{file_pattern}{suffix}"):
            # Skip excluded patterns
            if any(file.match(pattern) for pattern in exclude_patterns):
                continue
            
            try:
                df = load_single_file(str(file))
                dfs.append(df)
                print(f"✓ Loaded {len(df)} records from {file.name}")
            except Exception as e:
                print(f"✗ Failed to load {file.name}: {e}")
    
    if dfs:
        combined = pd.concat(dfs, ignore_index=True)
        print(f"\n✓ Total: {len(combined)} records from {len(dfs)} sources")
        return combined
    
    print("No files found matching criteria")
    return pd.DataFrame()