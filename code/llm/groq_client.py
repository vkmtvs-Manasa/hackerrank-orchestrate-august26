import json
import os
import time

from dotenv import load_dotenv
from groq import Groq


class GeminiClient:

    def __init__(
        self,
        model: str = "openai/gpt-oss-20b",
    ):

        load_dotenv()

        api_key = os.getenv("Groq_API_KEY")

        if not api_key:
            raise ValueError("Groq_API_KEY not found.")

        self.client = Groq(api_key=api_key)

        self.model = model

    @staticmethod
    def clean_json(text: str):

        text = text.strip()

        if text.startswith("```json"):
            text = text.replace("```json", "", 1)

        if text.startswith("```"):
            text = text.replace("```", "", 1)

        if text.endswith("```"):
            text = text[:-3]

        return text.strip()

    def generate_prediction(
        self,
        prompt: str,
    ) -> dict:

        while True:

            try:

                response = self.client.chat.completions.create(

                    model=self.model,

                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],

                    temperature=0.2,

                )

                response_text = response.choices[0].message.content

                if not response_text:
                    raise ValueError(
                        "Groq returned an empty response."
                    )

                response_text = self.clean_json(
                    response_text
                )

                return json.loads(
                    response_text
                )

            except json.JSONDecodeError as e:

                raise ValueError(
                    f"Groq returned invalid JSON:\n{response_text}"
                ) from e

            except Exception as e:

                error = str(e)

                if (
                    "429" in error
                    or "rate_limit" in error.lower()
                    or "too many requests" in error.lower()
                ):

                    print("\nGroq Error:")
                    print(error)

                    print(
                        "\nWaiting 60 seconds...\n"
                    )

                    time.sleep(60)

                    continue

                raise