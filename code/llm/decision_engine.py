"""
Decision Engine

Coordinates prompt generation,
Gemini inference,
and prediction validation.
"""

from __future__ import annotations

from .groq_client import GeminiClient
from .prompt_builder import PromptBuilder
from .validator import PredictionValidator


class DecisionEngine:
    """
    Generates notification routing decisions.
    """

    def __init__(
        self,
        model: str = "openai/gpt-oss-20b",
    ) -> None:

        self.prompt_builder = PromptBuilder()

        self.gemini = GeminiClient(model=model)

    # ==========================================================
    # SINGLE MESSAGE
    # ==========================================================

    def predict(
        self,
        context: dict,
    ) -> dict:

        try:

            prompt = self.prompt_builder.build_prompt(
                context
            )

            prediction = self.gemini.generate_prediction(
                prompt
            )

            prediction = PredictionValidator.validate(
                prediction
            )

            return prediction

        except Exception as error:

            print("\n" + "=" * 60)
            print("Decision Engine Error")
            print("=" * 60)
            print(error)
            print("=" * 60)

            return PredictionValidator.fallback_prediction()

    # ==========================================================
    # BATCH PREDICTION
    # ==========================================================

    def predict_batch(
        self,
        contexts: list[dict],
    ) -> list[dict]:

        try:

            # ------------------------------------------
            # Build ONE prompt for all messages
            # ------------------------------------------

            prompt = self.prompt_builder.build_batch_prompt(
                contexts
            )

            # ------------------------------------------
            # Gemini returns a JSON ARRAY
            # ------------------------------------------

            predictions = self.gemini.generate_prediction(
                prompt
            )

            # ------------------------------------------
            # Validate every prediction
            # ------------------------------------------

            validated_predictions = []

            for prediction in predictions:

                validated_predictions.append(

                    PredictionValidator.validate(
                        prediction
                    )

                )

            return validated_predictions

        except Exception as error:

            print("\n" + "=" * 60)
            print("Decision Engine Batch Error")
            print("=" * 60)
            print(error)
            print("=" * 60)

            return [

                PredictionValidator.fallback_prediction()

                for _ in contexts

            ]