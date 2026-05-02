import pandas as pd


POSITIVE_WORDS = [
    "rally", "surge", "beat", "growth", "gain", "rise", "up", "high",
    "profit", "strong", "record", "boost", "outperform", "upgrade",
    "bullish", "recovery", "rebound", "opportunity", "positive", "buy",
]

NEGATIVE_WORDS = [
    "drop", "fall", "decline", "loss", "down", "low", "weak", "miss",
    "cut", "layoff", "crash", "risk", "warning", "fear", "sell",
    "bearish", "recession", "inflation", "tariff", "sanction",
]


def simple_sentiment_score(text: str) -> int:
    text_lower = text.lower()
    score = 0
    for word in POSITIVE_WORDS:
        if word in text_lower:
            score += 1
    for word in NEGATIVE_WORDS:
        if word in text_lower:
            score -= 1
    return score


def generate_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["headline_length"] = df["headline"].apply(len)
    df["sentiment_score"] = df["headline"].apply(simple_sentiment_score)

    median = df["sentiment_score"].median()
    df["label"] = (df["sentiment_score"] > median).astype(int)

    return df[["headline_length", "sentiment_score", "label"]]
