from __future__ import annotations

from typing import Any

from app.knowledge_graph.neo4j_client import Neo4jClient


class GraphRetriever:
    """
    Retrieves relevant entities and relationships
    from the Neo4j Knowledge Graph.
    """

    def __init__(self):
        self.client = Neo4jClient()

    # =====================================================
    # Search Graph
    # =====================================================

    def search(
        self,
        question: str,
        max_results: int = 20,
    ) -> list[dict[str, Any]]:
        """
        Search the knowledge graph using keywords
        extracted from the user question.
        """

        keywords = self._extract_keywords(question)

        if not keywords:
            return []

        results = []

        for keyword in keywords:

            try:

                query = """
                MATCH (n)
                WHERE
                    toLower(coalesce(n.name, ''))
                        CONTAINS toLower($keyword)
                    OR
                    toLower(coalesce(n.label, ''))
                        CONTAINS toLower($keyword)
                    OR
                    toLower(coalesce(n.id, ''))
                        CONTAINS toLower($keyword)

                OPTIONAL MATCH (n)-[r]-(m)

                RETURN
                    n.id AS source_id,
                    coalesce(n.name, n.label, n.id)
                        AS source_name,
                    labels(n) AS source_labels,

                    type(r) AS relationship,

                    m.id AS target_id,
                    coalesce(m.name, m.label, m.id)
                        AS target_name,
                    labels(m) AS target_labels

                LIMIT $limit
                """

                rows = self.client.execute_query(
                    query,
                    {
                        "keyword": keyword,
                        "limit": max_results,
                    },
                )

                results.extend(rows)

            except Exception:
                continue

        return self._remove_duplicates(results)

    # =====================================================
    # Get Neighborhood
    # =====================================================

    def get_neighborhood(
        self,
        node_id: str,
        depth: int = 1,
    ) -> list[dict[str, Any]]:
        """
        Retrieve relationships around a specific node.
        """

        query = """
        MATCH (n {id: $node_id})-[r]-(m)

        RETURN
            n.id AS source_id,
            coalesce(n.name, n.label, n.id)
                AS source_name,
            labels(n) AS source_labels,

            type(r) AS relationship,

            m.id AS target_id,
            coalesce(m.name, m.label, m.id)
                AS target_name,
            labels(m) AS target_labels

        LIMIT 100
        """

        try:

            return self.client.execute_query(
                query,
                {
                    "node_id": node_id
                },
            )

        except Exception:
            return []

    # =====================================================
    # Keyword Extraction
    # =====================================================

    @staticmethod
    def _extract_keywords(
        question: str,
    ) -> list[str]:

        stop_words = {
            "what",
            "which",
            "where",
            "when",
            "who",
            "how",
            "why",
            "show",
            "tell",
            "me",
            "the",
            "is",
            "are",
            "was",
            "were",
            "and",
            "or",
            "of",
            "to",
            "in",
            "on",
            "for",
            "with",
            "from",
            "does",
            "do",
            "can",
            "give",
            "all",
            "about",
        }

        words = question.lower().split()

        keywords = []

        for word in words:

            word = (
                word
                .strip(".,?!:;()[]{}\"'")
            )

            if (
                len(word) >= 3
                and word not in stop_words
            ):
                keywords.append(word)

        return list(dict.fromkeys(keywords))

    # =====================================================
    # Remove Duplicate Results
    # =====================================================

    @staticmethod
    def _remove_duplicates(
        results: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:

        unique = []

        seen = set()

        for result in results:

            key = (
                result.get("source_id"),
                result.get("relationship"),
                result.get("target_id"),
            )

            if key in seen:
                continue

            seen.add(key)

            unique.append(result)

        return unique