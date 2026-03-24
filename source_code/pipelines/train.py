import os
import pathlib
import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

from source_code.pipelines.feature_engineering import generate_features
from source_code.monitoring.logger import log_model_performance


PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
MODEL_DIR = str(PROJECT_ROOT / "models")

CANDIDATES = {
    "LogisticRegression": LogisticRegression(max_iter=1000),
    "RandomForest":       RandomForestClassifier(n_estimators=100, random_state=42),
    "GradientBoosting":   GradientBoostingClassifier(n_estimators=100, random_state=42),
    "SVM":                SVC(kernel="rbf", probability=True),
}


def _evaluate(model, X_train, X_test, y_train, y_test) -> dict:
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    return {
        "accuracy":  float(accuracy_score(y_test, preds)),
        "precision": float(precision_score(y_test, preds, zero_division=0)),
        "recall":    float(recall_score(y_test, preds, zero_division=0)),
        "f1_score":  float(f1_score(y_test, preds, zero_division=0)),
    }


def train_model(data_path: str):
    df = pd.read_csv(data_path)
    features_df = generate_features(df)

    X = features_df[["headline_length", "sentiment_score"]]
    y = features_df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    results = {}
    for name, candidate in CANDIDATES.items():
        results[name] = _evaluate(candidate, X_train, X_test, y_train, y_test)

    # Pick best by F1; break ties with accuracy
    best_name = max(results, key=lambda n: (results[n]["f1_score"], results[n]["accuracy"]))
    best_model = CANDIDATES[best_name]
    best_metrics = results[best_name]
    best_metrics["best_model"] = best_name
    best_metrics["all_models"] = results

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(best_model, os.path.join(MODEL_DIR, "signal_model.pkl"))

    log_model_performance(best_metrics)

    return best_metrics
