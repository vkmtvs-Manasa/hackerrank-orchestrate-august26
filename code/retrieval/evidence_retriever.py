"""Retrieve historically similar messages to use as routing evidence."""

from __future__ import annotations

import csv
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Mapping

try:
    from rapidfuzz import fuzz
except ImportError:  # Allows the module to remain usable in minimal environments.
    fuzz = None


class EvidenceRetriever:
    """Rank messages from the cleaned evidence pool for a target message.

    The pool is read once when the retriever is constructed.  ``retrieve`` is
    deliberately side-effect free so callers can reuse one instance for the
    entire prediction run.
    """

    _RETURN_FIELDS = (
        "message_id",
        "message_text",
        "similarity_score",
        "message_opened",
        "message_replied",
        "notification_dismissed",
        "muted_after_message",
        "message_reported",
        "conversation_type",
        "media_type",
        "forwarded_count",
    )
    _MATCH_WEIGHTS = {
        "user_id": 45.0,
        "business_id": 25.0,
        "sender_user_id": 15.0,
        "group_id": 10.0,
        "conversation_type": 8.0,
        "media_type": 5.0,
    }

    def __init__(self) -> None:
        evidence_path = Path(__file__).resolve().parents[1] / "data" / "evidence_pool_clean.csv"
        with evidence_path.open("r", encoding="utf-8", newline="") as evidence_file:
            self._evidence_pool = list(csv.DictReader(evidence_file))

    def retrieve(self, message_row: Mapping[str, Any], top_k: int = 5) -> list[dict[str, Any]]:
        """Return up to ``top_k`` evidence messages ordered by relevance.

        Exact user/conversation identifiers receive most of the ranking weight;
        RapidFuzz text similarity supplies the remaining signal and breaks
        otherwise comparable matches.
        """
        if top_k <= 0:
            return []

        target_text = self._normalise(message_row.get("message_text"))
        ranked: list[tuple[float, float, dict[str, str]]] = []

        for evidence in self._evidence_pool:
            if evidence.get("message_id") == str(message_row.get("message_id", "")):
                continue

            similarity = self._text_similarity(
                target_text, self._normalise(evidence.get("message_text"))
            )
            score = similarity * 0.05

            for field, weight in self._MATCH_WEIGHTS.items():
                target_value = self._normalise(message_row.get(field))
                evidence_value = self._normalise(evidence.get(field))
                if target_value and target_value == evidence_value:
                    score += weight

            ranked.append((score, similarity, evidence))

        ranked.sort(key=lambda item: (item[0], item[1], item[2]["message_id"]), reverse=True)

        results: list[dict[str, Any]] = []
        for _, similarity, evidence in ranked[:top_k]:
            result = {field: evidence.get(field, "") for field in self._RETURN_FIELDS if field != "similarity_score"}
            result["similarity_score"] = round(similarity, 2)
            results.append(result)
        return results

    @staticmethod
    def _normalise(value: Any) -> str:
        """Make identifiers and text safe to compare when CSV values are blank."""
        return "" if value is None else str(value).strip()

    @staticmethod
    def _text_similarity(first: str, second: str) -> float:
        """Use RapidFuzz when available, with a standard-library fallback."""
        if fuzz is not None:
            return float(fuzz.ratio(first, second))
        return SequenceMatcher(None, first, second).ratio() * 100
