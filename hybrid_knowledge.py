"""Core hybrid knowledge router for the Version 2 learning project."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


ROUTING_KEYWORDS = {"protocol", "api", "schema", "rule"}


@dataclass
class RouteResult:
    """A transparent result that can be rendered by a CLI or web UI."""

    route: str
    answer: str
    reason: str
    source: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    similarity: float | None = None


class HybridKnowledgeBase:
    """Load local OKF and RAG knowledge and route user questions."""

    def __init__(self, okf_dir: Path, rag_dir: Path) -> None:
        self.okf_dir = okf_dir
        self.rag_dir = rag_dir

    @staticmethod
    def _query_words(query: str) -> set[str]:
        return set(re.findall(r"\b[\w-]+\b", query.lower()))

    @staticmethod
    def parse_okf_markdown(path: Path) -> dict[str, Any]:
        """Parse simple YAML front matter without requiring a YAML package."""
        text = path.read_text(encoding="utf-8")
        match = re.match(r"\A---\s*\n(.*?)\n---\s*\n?(.*)\Z", text, re.DOTALL)
        if not match:
            return {"file": path.name, "content": text.strip()}

        metadata: dict[str, Any] = {"file": path.name}
        for line in match.group(1).splitlines():
            key, separator, value = line.partition(":")
            if separator:
                value = value.strip().strip('"\'')
                metadata[key.strip()] = (
                    [item.strip() for item in value.split(",")]
                    if "," in value
                    else value
                )
        metadata["content"] = match.group(2).strip()
        return metadata

    def _okf_documents(self) -> list[dict[str, Any]]:
        return [
            self.parse_okf_markdown(path)
            for path in sorted(self.okf_dir.glob("*.md"))
        ]

    def _find_okf_document(self, query: str) -> dict[str, Any] | None:
        query_words = self._query_words(query)
        documents = self._okf_documents()

        def score(document: dict[str, Any]) -> int:
            searchable = " ".join(str(value).lower() for value in document.values())
            return sum(1 for word in query_words if word in searchable)

        best = max(documents, key=score, default=None)
        return best if best is not None and score(best) > 0 else None

    def _rag_chunks(self) -> list[dict[str, str]]:
        chunks: list[dict[str, str]] = []
        for path in sorted(self.rag_dir.glob("*.txt")):
            text = path.read_text(encoding="utf-8")
            for chunk in re.split(r"\n\s*\n|(?<=\.)\n", text):
                cleaned = chunk.strip()
                if cleaned:
                    chunks.append({"file": path.name, "text": cleaned})
        return chunks

    def _semantic_search(self, query: str, top_k: int = 1) -> list[dict[str, Any]]:
        chunks = self._rag_chunks()
        if not chunks:
            return []

        texts = [chunk["text"] for chunk in chunks]
        vectorizer = TfidfVectorizer(stop_words="english")
        matrix = vectorizer.fit_transform(texts + [query])
        scores = cosine_similarity(matrix[-1], matrix[:-1]).ravel()
        ranked_indexes = scores.argsort()[::-1][:top_k]
        return [
            {**chunks[index], "score": round(float(scores[index]), 3)}
            for index in ranked_indexes
        ]

    def route(self, query: str) -> RouteResult:
        """Choose deterministic lookup for explicit terms, otherwise use RAG."""
        query_words = self._query_words(query)
        matched_keyword = next(
            (keyword for keyword in ROUTING_KEYWORDS if keyword in query_words),
            None,
        )
        if matched_keyword:
            document = self._find_okf_document(query)
            if document:
                metadata = {
                    key: value for key, value in document.items() if key != "content"
                }
                return RouteResult(
                    route="Deterministic OKF Route",
                    answer=document["content"],
                    reason=f'The query contains the structured keyword "{matched_keyword}".',
                    source=f"okf_knowledge/{document['file']}",
                    metadata=metadata,
                )
            return RouteResult(
                route="Deterministic OKF Route",
                answer="No matching OKF metadata document was found.",
                reason=f'The query contains the structured keyword "{matched_keyword}".',
            )

        results = self._semantic_search(query)
        if not results:
            return RouteResult(
                route="Semantic RAG Route",
                answer="No RAG knowledge was found.",
                reason="The query is exploratory and no local text was available.",
            )

        result = results[0]
        return RouteResult(
            route="Semantic RAG Route",
            answer=result["text"],
            reason="The query is exploratory, so the closest local text chunk was selected.",
            source=f"rag_knowledge/{result['file']}",
            similarity=result["score"],
        )
