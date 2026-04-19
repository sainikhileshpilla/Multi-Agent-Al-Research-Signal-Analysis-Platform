from pathlib import Path
from typing import Union


PathLike = Union[str, Path]

# Canonical project root for all runtime paths.
REPO_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = REPO_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

LIVE_NEWS_PATH = RAW_DATA_DIR / "live_news.csv"
PROCESSED_NEWS_PATH = PROCESSED_DATA_DIR / "news_cleaned.csv"

MODELS_DIR = REPO_ROOT / "models"
MODEL_PATH = MODELS_DIR / "signal_model.pkl"

LOGS_DIR = REPO_ROOT / "logs"
PERFORMANCE_LOG_PATH = LOGS_DIR / "model_performance.json"

DEPLOYED_DIR = REPO_ROOT / "deployed"
DEPLOYED_MODEL_PATH = DEPLOYED_DIR / "signal_model.pkl"
DEPLOYMENT_MANIFEST_PATH = DEPLOYED_DIR / "deployment_manifest.json"

VECTOR_STORE_DIR = DATA_DIR / "vectorstore"


def resolve_path(path: PathLike) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else REPO_ROOT / candidate