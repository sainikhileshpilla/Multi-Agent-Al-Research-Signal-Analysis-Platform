"""Compatibility shim for gradual migration to services.data.ingestion."""

from services.data.ingestion import (  # noqa: F401
    load_all_from_directory,
    load_single_file,
    normalize_columns,
    read_csv,
    read_excel,
    read_pdf,
)
