from crewai.tools import BaseTool

from source_code.paths import PROCESSED_NEWS_PATH
from services.rag.rag import retrieve_context


class RAGRetrievalTool(BaseTool):
    name: str = "rag_retrieval_tool"
    description: str = (
        "Retrieves the most relevant financial news records for a query from a processed CSV "
        "using semantic retrieval. Accepts optional data_path, query, and top_k. "
        "Returns ranked context snippets with source and timestamp."
    )

    def _run(
        self,
        query: str = "market-moving financial signals",
        data_path: str = str(PROCESSED_NEWS_PATH),
        top_k: int = 5,
    ) -> str:
        try:
            payload = retrieve_context(data_path=data_path, query=query, top_k=top_k)
            results = payload["results"]

            if not results:
                return (
                    f"No retrievable records found in {payload['data_path']} "
                    f"for query '{payload['query']}'."
                )

            lines = [
                f"RAG strategy: {payload['strategy']}",
                f"Query: {payload['query']}",
                f"Data: {payload['data_path']}",
                f"Top results: {len(results)}",
                "",
            ]

            for i, row in enumerate(results, start=1):
                lines.extend(
                    [
                        f"[{i}] score={row['score']:.4f} source={row['source']} timestamp={row['timestamp']}",
                        f"headline: {row['headline']}",
                        f"content: {row['content'][:400]}",
                        "",
                    ]
                )

            return "\n".join(lines).strip()
        except Exception as exc:
            return f"RAG retrieval failed: {str(exc)}"
