"""
Validates the prediction returned by the LLM.
"""

from __future__ import annotations


class PredictionValidator:
    """
    Validates the JSON prediction returned by the Decision Engine.
    """

    VALID_ACTIONS = {
        "notify",
        "digest",
        "mute",
    }

    VALID_MESSAGE_TYPES = {
        "personal",
        "urgent",
        "event",
        "payment",
        "business_update",
        "promotion",
        "greeting",
        "forward",
        "spam",
        "scam",
        "unknown",
    }

    @staticmethod
    def fallback_prediction() -> dict:
        """
        Safe fallback prediction if the LLM output is invalid.
        """

        return {
            "action": "digest",
            "message_type": "unknown",
            "reason": "Fallback prediction due to invalid model output.",
            "confidence": 0.50,
            "evidence_message_ids": "none",
        }

    @classmethod
    def validate(cls, prediction: dict) -> dict:
        """
        Validate the prediction returned by the LLM.
        """

        # -------------------------------------------------
        # Prediction must be a dictionary
        # -------------------------------------------------

        if not isinstance(prediction, dict):
            return cls.fallback_prediction()

        # -------------------------------------------------
        # Normalize text fields
        # -------------------------------------------------

        prediction["action"] = str(
            prediction.get("action", "")
        ).strip().lower()

        prediction["message_type"] = str(
            prediction.get("message_type", "")
        ).strip().lower()

        # -------------------------------------------------
        # Validate Action
        # -------------------------------------------------

        if prediction["action"] not in cls.VALID_ACTIONS:
            return cls.fallback_prediction()

        # -------------------------------------------------
        # Validate Message Type
        # -------------------------------------------------

        if prediction["message_type"] not in cls.VALID_MESSAGE_TYPES:
            return cls.fallback_prediction()

        # -------------------------------------------------
        # Validate Confidence
        # -------------------------------------------------

        confidence = prediction.get("confidence")

        try:
            confidence = float(confidence)
        except (TypeError, ValueError):
            return cls.fallback_prediction()

        if confidence < 0 or confidence > 1:
            return cls.fallback_prediction()

        prediction["confidence"] = confidence

        # -------------------------------------------------
        # Validate Reason
        # -------------------------------------------------

        reason = prediction.get("reason")

        if not isinstance(reason, str) or not reason.strip():
            prediction["reason"] = "No reason provided."

        # -------------------------------------------------
        # Validate Evidence Message IDs
        # -------------------------------------------------

        evidence = prediction.get("evidence_message_ids")

        # GPT may return a list
        if isinstance(evidence, list):
            prediction["evidence_message_ids"] = ";".join(
                map(str, evidence)
            )

        # Empty or missing
        elif not evidence:
            prediction["evidence_message_ids"] = "none"

        else:
            prediction["evidence_message_ids"] = str(evidence)

        return prediction