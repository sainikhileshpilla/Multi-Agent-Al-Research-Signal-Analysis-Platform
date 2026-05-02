"""Tests for RAG retrieval system."""

import pytest
from services.rag.rag import retrieve_context, build_index, index_status
from source_code.paths import PROCESSED_NEWS_PATH


def test_retrieve_context_handles_missing_file():
    """Test that retrieve_context raises error for missing data."""
    with pytest.raises(FileNotFoundError):
        retrieve_context(data_path="/tmp/nonexistent.csv")


def test_index_status():
    """Test that index_status returns a status dict."""
    status = index_status()
    assert isinstance(status, dict)
    assert "status" in status


def test_retrieve_context_returns_expected_format():
    """Test that retrieve_context returns proper structure."""
    try:
        result = retrieve_context()
        assert isinstance(result, dict)
        assert "strategy" in result
        assert "query" in result
        assert "results" in result
        assert isinstance(result["results"], list)
    except FileNotFoundError:
        # OK if processed data doesn't exist yet
        pytest.skip("Processed data not available")


def test_build_index_with_missing_file():
    """Test that build_index raises error for missing file."""
    with pytest.raises(FileNotFoundError):
        build_index(data_path="/tmp/nonexistent.csv")
