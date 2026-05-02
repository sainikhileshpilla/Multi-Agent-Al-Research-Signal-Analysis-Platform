"""Compatibility shim for gradual migration to services.ml.feature_engineering."""

from services.ml.feature_engineering import (  # noqa: F401
    NEGATIVE_WORDS,
    POSITIVE_WORDS,
    generate_features,
    simple_sentiment_score,
)
