import sqlite3
import math
import re
from typing import List, Dict, Tuple
from collections import Counter
import argparse


class ExocortexClient:
    def __init__(self, db_path=".context/knowledge/exocortex.db"):
        self.db_path = db_path

    def _get_connection(self):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            print(f"Error connecting to Exocortex: {e}")
            return None

    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """Basic FTS Search"""
        conn = self._get_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor()
            # FTS5 syntax: column:query OR query
            cursor.execute(
                """
                SELECT title, abstract, url 
                FROM abstracts 
                WHERE abstracts MATCH ? 
                ORDER BY rank 
                LIMIT ?
            """,
                (query, limit),
            )
            results = [dict(row) for row in cursor.fetchall()]
            return results
        except sqlite3.Error as e:
            print(f"Search error: {e}")
            return []
        finally:
            conn.close()

    def get_jargon_injector(self, domain: str, limit: int = 50) -> List[str]:
        """
        Extracts high-value vocabulary from a domain using TF-IDF logic (simplified).
        """
        print(f"--- 💉 JARGON INJECTOR: Scanning '{domain}' ---")

        # 1. Fetch Abstracts
        results = self.search(domain, limit)
        if not results:
            return ["Error: Domain not found in Exocortex."]

        corpus = [r["abstract"] for r in results if r["abstract"]]
        full_text = " ".join(corpus)

        # 2. Tokenize & Clean
        words = re.findall(r"\b[a-zA-Z]{4,}\b", full_text.lower())

        # 3. Frequency Analysis (TF)
        # We want words that are frequent IN THIS DOMAIN but rare generally.
        # Since we don't have a global IDF table loaded, we use a heuristic:
        # Filter out common stop words and generic academic verbs.

        stop_words = set(
            [
                "this",
                "that",
                "with",
                "from",
                "have",
                "which",
                "are",
                "for",
                "the",
                "and",
                "their",
                "they",
                "will",
                "can",
                "what",
                "context",
                "abstract",
                "introduction",
                "study",
                "research",
                "paper",
                "data",
                "analysis",
                "results",
                "conclusion",
                "however",
                "although",
                "between",
                "through",
                "during",
                "within",
                "using",
                "other",
                "these",
                "those",
                "system",
                "model",
                "process",
                "based",
                "found",
            ]
        )

        freq_dist = Counter([w for w in words if w not in stop_words])

        # 4. Extract Top Terms
        # We favor capitalization in the original text to find Proper Nouns/Jargon
        # (This is a simplified Named Entity Recognition)

        # Get top 20 raw terms
        top_terms = [item[0] for item in freq_dist.most_common(20)]

        # Restore capitalization from original text
        final_jargon = []
        for term in top_terms:
            # Find original variations
            matches = re.findall(r"\b" + term + r"\b", full_text, re.IGNORECASE)
            if matches:
                # Pick most common capitalization
                cap_counts = Counter(matches)
                best_cap = cap_counts.most_common(1)[0][0]
                final_jargon.append(best_cap)

        return final_jargon

    def get_serendipity_walk(self, start_concept: str, target_domain: str) -> str:
        """
        Simulated Lateral Traversal via Semantic Bridging.
        Finds a term that appears in the context of BOTH concepts.
        """
        print(f"--- 🧠 SERENDIPITY WALK: {start_concept} -> {target_domain} ---")

        # 1. Get Context A (Start)
        results_a = self.search(start_concept, limit=20)
        text_a = " ".join([r["abstract"] for r in results_a if r["abstract"]]).lower()

        # 2. Get Context B (Target)
        results_b = self.search(target_domain, limit=20)
        text_b = " ".join([r["abstract"] for r in results_b if r["abstract"]]).lower()

        if not text_a or not text_b:
            return f"Error: Could not find sufficient context for {start_concept} or {target_domain}."

        # 3. Find Intersecting Terms (Bridge)
        # Tokenize
        words_a = set(re.findall(r"\b[a-zA-Z]{5,}\b", text_a))
        words_b = set(re.findall(r"\b[a-zA-Z]{5,}\b", text_b))

        # Intersect
        common_terms = words_a.intersection(words_b)

        # Filter common stopwords again to ensure bridge is meaningful
        stop_words = set(
            [
                "between",
                "through",
                "during",
                "within",
                "using",
                "system",
                "model",
                "process",
                "based",
                "found",
                "study",
                "research",
                "paper",
                "analysis",
                "which",
                "their",
                "about",
                "would",
                "could",
                "should",
                "values",
                "these",
            ]
        )
        bridges = [w for w in common_terms if w not in stop_words]

        if not bridges:
            return f"No direct bridge found between {start_concept} and {target_domain}. Try a broader domain."

        # Select the 'rarest' bridge (simplistic heuristic: longest word often correlates with specificity)
        # In a real system we'd use IDF.
        best_bridge = max(bridges, key=len)

        return f"PATH: {start_concept} -> [{best_bridge.title()}] -> {target_domain}\n\nLogic: Both domains rely on the concept of '{best_bridge}'."


# --- CLI Interface for Quick Testing ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kinetic Engine CLI")
    parser.add_argument("tool", choices=["jargon", "walk"], help="Tool to use")
    parser.add_argument("arg1", help="Domain or Start Concept")
    parser.add_argument("arg2", nargs="?", help="Target Concept (for walk)")

    args = parser.parse_args()

    client = ExocortexClient()

    if args.tool == "jargon":
        print(client.get_jargon_injector(args.arg1))
    elif args.tool == "walk":
        if not args.arg2:
            print("Error: Walk requires a target domain.")
        else:
            print(client.get_serendipity_walk(args.arg1, args.arg2))
