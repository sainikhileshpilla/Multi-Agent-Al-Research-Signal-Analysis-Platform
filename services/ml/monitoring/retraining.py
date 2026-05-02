from source_code.paths import PROCESSED_NEWS_PATH, resolve_path
from services.ml.train import train_model


def trigger_retraining(data_path: str = str(PROCESSED_NEWS_PATH)) -> dict:
    resolved_data_path = resolve_path(data_path)
    if not resolved_data_path.exists():
        raise FileNotFoundError(
            f"Retraining dataset not found at '{resolved_data_path}'."
        )

    metrics = train_model(str(resolved_data_path))
    return {
        "status": "retrained",
        "data_path": str(resolved_data_path),
        "best_model": metrics["best_model"],
        "accuracy": metrics["accuracy"],
        "precision": metrics["precision"],
        "recall": metrics["recall"],
        "f1_score": metrics["f1_score"],
    }
