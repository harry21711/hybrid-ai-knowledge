import unittest
from pathlib import Path

from hybrid_knowledge import HybridKnowledgeBase


PROJECT_DIR = Path(__file__).resolve().parents[1]


class HybridKnowledgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.knowledge = HybridKnowledgeBase(
            PROJECT_DIR / "okf_knowledge",
            PROJECT_DIR / "rag_knowledge",
        )

    def test_structured_query_uses_okf_route(self) -> None:
        result = self.knowledge.route("What is the authentication protocol?")

        self.assertEqual(result.route, "Deterministic OKF Route")
        self.assertEqual(result.source, "okf_knowledge/protocol.md")
        self.assertIn("short-lived bearer token", result.answer)
        self.assertIsNone(result.similarity)

    def test_exploratory_query_uses_rag_route(self) -> None:
        result = self.knowledge.route("Why is the dashboard incomplete?")

        self.assertEqual(result.route, "Semantic RAG Route")
        self.assertEqual(result.source, "rag_knowledge/notes.txt")
        self.assertIn("retry log", result.answer)
        self.assertIsNotNone(result.similarity)


if __name__ == "__main__":
    unittest.main()
