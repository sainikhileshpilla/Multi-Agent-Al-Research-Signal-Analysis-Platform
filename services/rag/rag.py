"""
RAG (Retrieval-Augmented Generation) layer.

Retrieval priority:
  1. ChromaDB  — persistent vector database on disk (data/vectorstore/)
       - OpenAI embeddings  when OPENAI_API_KEY is set
       - Default embeddings (all-MiniLM-L6-v2 via onnxruntime) otherwise
  2. TF-IDF    — in-memory keyword fallback when chromadb is not installed
"""

import hashlib
import os
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

from source_code.paths import PROCESSED_NEWS_PATH, VECTOR_STORE_DIR, resolve_path

COLLECTION_NAME = "financial_news"


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _normalize_rows(df: pd.DataFrame) -> pd.DataFrame:
    required = ["headline", "content", "timestamp", "source"]
    normalized = df.copy()
    for col in required:
        if col not in normalized.columns:
            normalized[col] = ""
    return normalized[required].fillna("")


def _build_documents(df: pd.DataFrame) -> List[str]:
    """Combine headline + content into a single string per row."""
    return (
        df["headline"].astype(str).str.strip()
        + "\n"
        + df["content"].astype(str).str.strip()
    ).tolist()


def _doc_id(text: str, idx: int) -> str:
    return hashlib.md5(f"{idx}:{text[:200]}".encode()).hexdigest()


# ---------------------------------------------------------------------------
# ChromaDB helpers
# ---------------------------------------------------------------------------

def _embedding_function():
    from chromadb.utils import embedding_functions

    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        return embedding_functions.OpenAIEmbeddingFunction(
            api_key=api_key,
            model_name=os.environ.get("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
        )
    # Uses all-MiniLM-L6-v2 via onnxruntime — downloads ~80 MB on first run.
    return embedding_functions.DefaultEmbeddingFunction()


def _chroma_client():
    import chromadb

    VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(VECTOR_STORE_DIR))


def _strategy_label() -> str:
    return "chromadb:openai" if os.environ.get("OPENAI_API_KEY") else "chromadb:default"


# ---------------------------------------------------------------------------
# Public: build index
# ---------------------------------------------------------------------------

def build_index(
    data_path: str = str(PROCESSED_NEWS_PATH),
    collection_name: str = COLLECTION_NAME,
    force_rebuild: bool = False,
) -> Dict:
    """
    Read the processed CSV and upsert all rows into a ChromaDB collection.

    Set force_rebuild=True to delete and recreate the collection from scratch.
    Returns a summary dict with status, document count, and storage path.
    """
    resolved = resolve_path(data_path)
    if not resolved.exists():
        raise FileNotFoundError(f"Dataset not found at '{resolved}'.")

    df = pd.read_csv(resolved)
    df = _normalize_rows(df)

    if df.empty:
        return {"status": "skipped", "reason": "empty dataset", "count": 0}

    documents = _build_documents(df)
    ids = [_doc_id(doc, i) for i, doc in enumerate(documents)]
    metadatas = [
        {
            "headline": str(row["headline"]),
            "timestamp": str(row["timestamp"]),
            "source": str(row["source"]),
        }
        for row in df[["headline", "timestamp", "source"]].to_dict(orient="records")
    ]

    client = _chroma_client()
    embed_fn = _embedding_function()

    if force_rebuild:
        try:
            client.delete_collection(collection_name)
        except Exception:
            pass

    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=embed_fn,
        metadata={"hnsw:space": "cosine"},
    )

    # Upsert in batches of 100 so large datasets don't blow up memory.
    batch_size = 100
    for start in range(0, len(documents), batch_size):
        end = min(start + batch_size, len(documents))
        collection.upsert(
            ids=ids[start:end],
            documents=documents[start:end],
            metadatas=metadatas[start:end],
        )

    return {
        "status": "built",
        "collection": collection_name,
        "count": len(documents),
        "strategy": _strategy_label(),
        "persist_dir": str(VECTOR_STORE_DIR),
    }


# ---------------------------------------------------------------------------
# Public: retrieve context
# ---------------------------------------------------------------------------

def retrieve_context(
    data_path: str = str(PROCESSED_NEWS_PATH),
    query: str = "market-moving financial signals",
    top_k: int = 5,
    collection_name: str = COLLECTION_NAME,
) -> Dict:
    """
    Return the top_k most relevant news records for the given query.

    Uses ChromaDB if available; falls back to TF-IDF keyword matching.
    """
    resolved = resolve_path(data_path)
    if not resolved.exists():
        raise FileNotFoundError(f"RAG dataset not found at '{resolved}'.")

    df = pd.read_csv(resolved)
    df = _normalize_rows(df)

    if df.empty:
        return {"strategy": "none", "query": query, "data_path": str(resolved), "results": []}

    top_k = max(1, min(int(top_k), len(df)))

    try:
        import chromadb  # noqa: F401 — just checking it is installed

        results, strategy = _retrieve_chroma(
            data_path=str(resolved),
            query=query,
            top_k=top_k,
            collection_name=collection_name,
        )
    except Exception:
        documents = _build_documents(df)
        results, strategy = _retrieve_tfidf(documents, df, query, top_k)

    return {"strategy": strategy, "query": query, "data_path": str(resolved), "results": results}


def index_status(collection_name: str = COLLECTION_NAME) -> Dict:
    """Return basic stats about the persisted ChromaDB collection."""
    try:
        client = _chroma_client()
        collection = client.get_collection(
            name=collection_name,
            embedding_function=_embedding_function(),
        )
        return {
            "status": "ready",
            "collection": collection_name,
            "count": collection.count(),
            "strategy": _strategy_label(),
            "persist_dir": str(VECTOR_STORE_DIR),
        }
    except Exception as exc:
        return {"status": "not_built", "reason": str(exc)}


# ---------------------------------------------------------------------------
# Private: ChromaDB retrieval
# ---------------------------------------------------------------------------

def _retrieve_chroma(
    data_path: str,
    query: str,
    top_k: int,
    collection_name: str,
) -> Tuple[List[Dict], str]:
    client = _chroma_client()
    embed_fn = _embedding_function()

    try:
        collection = client.get_collection(name=collection_name, embedding_function=embed_fn)
    except Exception:
        # Collection does not exist yet — build it on demand.
        build_index(data_path=data_path, collection_name=collection_name)
        collection = client.get_collection(name=collection_name, embedding_function=embed_fn)

    total = collection.count()
    if total == 0:
        return [], "chromadb:empty"

    n = min(top_k, total)
    response = collection.query(
        query_texts=[query],
        n_results=n,
        include=["documents", "metadatas", "distances"],
    )

    results = []
    for doc, meta, dist in zip(
        response["documents"][0],
        response["metadatas"][0],
        response["distances"][0],
    ):
        # Cosine space: distance 0 = identical → similarity = 1 - distance
        score = max(0.0, float(1.0 - dist))
        content_parts = doc.split("\n", 1)
        results.append(
            {
                "score": score,
                "headline": meta.get("headline", content_parts[0] if content_parts else ""),
                "content": content_parts[1][:400] if len(content_parts) > 1 else doc[:400],
                "timestamp": meta.get("timestamp", ""),
                "source": meta.get("source", ""),
            }
        )

    return results, _strategy_label()


# ---------------------------------------------------------------------------
# Private: TF-IDF fallback
# ---------------------------------------------------------------------------

def _retrieve_tfidf(
    documents: List[str],
    df: pd.DataFrame,
    query: str,
    top_k: int,
) -> Tuple[List[Dict], str]:
    vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
    matrix = vectorizer.fit_transform(documents)
    query_vec = vectorizer.transform([query])
    sims = (matrix @ query_vec.T).toarray().reshape(-1)
    order = np.argsort(-sims)[:top_k]

    results = []
    for idx in order:
        row = df.iloc[idx]
        results.append(
            {
                "score": float(sims[idx]),
                "headline": str(row["headline"]),
                "content": str(row["content"])[:400],
                "timestamp": str(row["timestamp"]),
                "source": str(row["source"]),
            }
        )
    return results, "tfidf"
