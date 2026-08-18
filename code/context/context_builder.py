"""
Builds the complete context that will be passed to the Decision Engine.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


class ContextBuilder:
    """
    Loads contextual datasets once and builds a structured context dictionary
    for the Decision Engine.
    """

    def __init__(self) -> None:
        # Project Root
        repo_root = Path(__file__).resolve().parents[2]

        # Original datasets
        dataset_dir = repo_root / "dataset"

        # Load datasets once
        self.users = pd.read_csv(dataset_dir / "users.csv")
        self.groups = pd.read_csv(dataset_dir / "groups.csv")
        self.businesses = pd.read_csv(dataset_dir / "business_accounts.csv")
        self.user_business = pd.read_csv(
            dataset_dir / "user_business_history.csv"
        )

    def _lookup(
        self,
        df: pd.DataFrame,
        column: str,
        value: Any,
    ) -> dict:
        """
        Return the first matching row as a dictionary.
        """

        if value is None or pd.isna(value):
            return {}

        match = df[df[column] == value]

        if match.empty:
            return {}

        return match.iloc[0].to_dict()

    def _build_evidence_summary(
        self,
        evidence: list[dict],
    ) -> dict:
        """
        Create a compact summary of retrieved evidence for the LLM.
        """

        summary = {
            "total_evidence": len(evidence),
            "opened_count": 0,
            "replied_count": 0,
            "dismissed_count": 0,
            "reported_count": 0,
            "muted_count": 0,
        }

        for item in evidence:

            if str(item.get("message_opened", "")).lower() in ("1", "true", "yes"):
                summary["opened_count"] += 1

            if str(item.get("message_replied", "")).lower() in ("1", "true", "yes"):
                summary["replied_count"] += 1

            if str(item.get("notification_dismissed", "")).lower() in ("1", "true", "yes"):
                summary["dismissed_count"] += 1

            if str(item.get("message_reported", "")).lower() in ("1", "true", "yes"):
                summary["reported_count"] += 1

            if str(item.get("muted_after_message", "")).lower() in ("1", "true", "yes"):
                summary["muted_count"] += 1

        return summary

    def build_context(
        self,
        message_row: dict | pd.Series,
        evidence: list[dict],
    ) -> dict:
        """
        Build the complete context for the Decision Engine.
        """

        # Convert pandas Series safely
        if isinstance(message_row, pd.Series):
            message_row = message_row.to_dict()

        # User context
        user = self._lookup(
            self.users,
            "user_id",
            message_row.get("user_id"),
        )

        # Group context
        group = self._lookup(
            self.groups,
            "group_id",
            message_row.get("group_id"),
        )

        # Business context
        business = self._lookup(
            self.businesses,
            "business_id",
            message_row.get("business_id"),
        )

        # Relationship context
        relationship = {}

        if (
            message_row.get("user_id") is not None
            and message_row.get("business_id") is not None
        ):

            rel = self.user_business[
                (self.user_business["user_id"] == message_row["user_id"])
                &
                (self.user_business["business_id"] == message_row["business_id"])
            ]

            if not rel.empty:
                relationship = rel.iloc[0].to_dict()

        # Summarize retrieved evidence
        evidence_summary = self._build_evidence_summary(evidence)

        # Final Context
        context = {

            "current_message": dict(message_row),

            "timestamp": message_row.get("created_at"),

            "user_context": user,

            "group_context": group,

            "business_context": business,

            "relationship_context": relationship,

            "historical_evidence": evidence,

            "evidence_summary": evidence_summary,
        }

        return context