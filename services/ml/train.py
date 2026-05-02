import os

import joblib
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC

from services.ml.feature_engineering import generate_features
from source_code.monitoring.logger import log_model_performance
from source_code.paths import MODEL_PATH, MODELS_DIR


CANDIDATES = {
    "LogisticRegression": LogisticRegression(max_iter=1000),
    "RandomForest": RandomForestClassifier(n_estimators=100, random_state=42),
    "GradientBoosting": GradientBoostingClassifier(n_estimators=100, random_state=42),
    "SVM": SVC(kernel="rbf", probability=True),
}


def _evaluate(model, X_train, X_test, y_train, y_test) -> dict:
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    return {
        "accuracy": float(accuracy_score(y_test, preds)),
        "precision": float(precision_score(y_test, preds, zero_division=0)),
        "recall": float(recall_score(y_test, preds, zero_division=0)),
        "f1_score": float(f1_score(y_test, preds, zero_division=0)),
    }


def train_model(data_path: str) -> dict:
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

    best_name = max(results, key=lambda n: (results[n]["f1_score"], results[n]["accuracy"]))
    best_model = CANDIDATES[best_name]

    best_metrics = {
        **results[best_name],
        "best_model": best_name,
        "all_models": results,
    }

    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(best_model, str(MODEL_PATH))

    log_model_performance(best_metrics)
    return best_metrics
