"""BM25 retriever for memory store (no external dependencies)."""

from __future__ import annotations

import math
from collections import Counter
from typing import Any

from blindspot.memory.store import MemoryEntry


class BM25Retriever:
    """Sparse BM25 retrieval — no external libraries required."""

    def __init__(self, k1: float = 1.5, b: float = 0.75) -> None:
        self._k1 = k1
        self._b = b
        self._entries: list[MemoryEntry] = []
        self._idf: dict[str, float] = {}
        self._avg_len: float = 0.0

    def index(self, entries: list[MemoryEntry]) -> None:
        """Build the BM25 index from a list of memory entries."""
        self._entries = entries
        n = len(entries)
        if n == 0:
            return

        # Build term → document frequency
        df: Counter[str] = Counter()
        tokenized = [self._tokenize(e.content) for e in entries]
        for tokens in tokenized:
            for term in set(tokens):
                df[term] += 1

        # Compute IDF
        self._idf = {
            term: math.log((n - freq + 0.5) / (freq + 0.5) + 1)
            for term, freq in df.items()
        }
        total_len = sum(len(t) for t in tokenized)
        self._avg_len = total_len / n if n > 0 else 1.0

    def query(self, text: str, k: int = 5) -> list[MemoryEntry]:
        """Return top-k entries by BM25 score."""
        if not self._entries:
            return []

        query_tokens = self._tokenize(text)
        scores: list[tuple[float, MemoryEntry]] = []

        for entry in self._entries:
            doc_tokens = self._tokenize(entry.content)
            doc_len = len(doc_tokens)
            tf = Counter(doc_tokens)
            score = 0.0
            for term in query_tokens:
                if term not in self._idf:
                    continue
                idf = self._idf[term]
                tf_term = tf.get(term, 0)
                numerator = tf_term * (self._k1 + 1)
                denominator = tf_term + self._k1 * (
                    1 - self._b + self._b * doc_len / self._avg_len
                )
                score += idf * (numerator / denominator if denominator > 0 else 0)
            scores.append((score, entry))

        scores.sort(key=lambda x: -x[0])
        return [e for _, e in scores[:k]]

    def _tokenize(self, text: str) -> list[str]:
        return text.lower().split()
