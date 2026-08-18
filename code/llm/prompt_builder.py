# """
# Builds the final prompt that will be sent to the Gemini model.
# """

# from __future__ import annotations

# from pathlib import Path
# import json


# class PromptBuilder:
#     """
#     Creates the final prompt for the Gemini model.
#     """

#     def __init__(self) -> None:

#         prompt_path = (
#             Path(__file__).resolve().parent
#             / "prompt_template.txt"
#         )

#         with open(
#             prompt_path,
#             "r",
#             encoding="utf-8",
#         ) as file:

#             self.system_prompt = file.read()

#     # ==========================================================
#     # SINGLE MESSAGE PROMPT
#     # ==========================================================

#     def build_prompt(
#         self,
#         context: dict,
#     ) -> str:
#         """
#         Build the prompt for ONE message.
#         """

#         prompt = f"""
# {self.system_prompt}

# ========================================================
# CURRENT MESSAGE
# ========================================================

# {json.dumps(context.get("current_message", {}), indent=2)}

# ========================================================
# USER CONTEXT
# ========================================================

# {json.dumps(context.get("user_context", {}), indent=2)}

# ========================================================
# GROUP CONTEXT
# ========================================================

# {json.dumps(context.get("group_context", {}), indent=2)}

# ========================================================
# BUSINESS CONTEXT
# ========================================================

# {json.dumps(context.get("business_context", {}), indent=2)}

# ========================================================
# USER-BUSINESS RELATIONSHIP
# ========================================================

# {json.dumps(context.get("relationship_context", {}), indent=2)}

# ========================================================
# EVIDENCE SUMMARY
# ========================================================

# {json.dumps(context.get("evidence_summary", {}), indent=2)}

# ========================================================
# TOP HISTORICAL EVIDENCE
# ========================================================

# {json.dumps(context.get("historical_evidence", []), indent=2)}

# ========================================================
# IMPORTANT
# ========================================================

# Return ONLY valid JSON.

# Do not include:

# - Markdown
# - Triple backticks
# - Explanations
# - Notes
# - Headings

# The response must be directly parseable using json.loads().
# """

#         return prompt

#     # ==========================================================
#     # BATCH PROMPT
#     # ==========================================================

#     def build_batch_prompt(
#         self,
#         contexts: list[dict],
#     ) -> str:
#         """
#         Build ONE prompt for multiple WhatsApp messages.
#         """

#         prompt = f"""
# {self.system_prompt}

# ========================================================
# TASK
# ========================================================

# You are given MULTIPLE WhatsApp messages.

# Each message has its own complete context.

# Predict the routing decision for EACH message independently.

# Treat every message separately.

# ========================================================
# OUTPUT FORMAT
# ========================================================

# Return ONLY a JSON ARRAY.

# Example:

# [
#     {{
#         "message_id":"msg_001",
#         "action":"notify",
#         "message_type":"urgent",
#         "reason":"...",
#         "confidence":0.95
#     }},
#     {{
#         "message_id":"msg_002",
#         "action":"digest",
#         "message_type":"promotion",
#         "reason":"...",
#         "confidence":0.81
#     }}
# ]

# ========================================================
# MESSAGES
# ========================================================
# """

#         for i, context in enumerate(contexts, start=1):

#             prompt += f"""

# ########################################################
# MESSAGE {i}
# ########################################################

# CURRENT MESSAGE

# {json.dumps(context.get("current_message", {}), indent=2)}

# USER CONTEXT

# {json.dumps(context.get("user_context", {}), indent=2)}

# GROUP CONTEXT

# {json.dumps(context.get("group_context", {}), indent=2)}

# BUSINESS CONTEXT

# {json.dumps(context.get("business_context", {}), indent=2)}

# USER-BUSINESS RELATIONSHIP

# {json.dumps(context.get("relationship_context", {}), indent=2)}

# EVIDENCE SUMMARY

# {json.dumps(context.get("evidence_summary", {}), indent=2)}

# TOP HISTORICAL EVIDENCE

# {json.dumps(context.get("historical_evidence", [])[:1], indent=2)}

# """

#         prompt += """

# ========================================================
# VERY IMPORTANT
# ========================================================

# Return ONLY valid JSON.

# Return ONLY a JSON ARRAY.

# Return EXACTLY one prediction for every message.

# Each prediction MUST contain:

# - message_id
# - action
# - message_type
# - reason
# - confidence

# Do NOT return markdown.

# Do NOT use triple backticks.

# Do NOT explain anything outside the JSON.

# The output must be directly parseable using json.loads().
# """

#         return prompt

from __future__ import annotations

import json
from pathlib import Path


class PromptBuilder:

    def __init__(self) -> None:

        prompt_path = (
            Path(__file__).resolve().parent
            / "prompt_template.txt"
        )

        if prompt_path.exists():
            self.system_prompt = prompt_path.read_text(
                encoding="utf-8"
            )
        else:
            self.system_prompt = """
You are an AI notification routing assistant.

Analyze each WhatsApp message and determine the appropriate
notification action and message type.
"""

    # ==========================================================
    # SINGLE MESSAGE
    # ==========================================================

    def build_prompt(
        self,
        context: dict,
    ) -> str:
        """
        Build a prompt for a single WhatsApp message.
        """

        prompt = f"""
{self.system_prompt}

You are given one WhatsApp message.

Predict the routing decision.

Return ONLY a valid JSON object.

CURRENT MESSAGE

{json.dumps(
    context.get("current_message", {}),
    indent=2,
)}

USER CONTEXT

{json.dumps(
    context.get("user_context", {}),
    indent=2,
)}

GROUP CONTEXT

{json.dumps(
    context.get("group_context", {}),
    indent=2,
)}

BUSINESS CONTEXT

{json.dumps(
    context.get("business_context", {}),
    indent=2,
)}

RELATIONSHIP CONTEXT

{json.dumps(
    context.get("relationship_context", {}),
    indent=2,
)}

EVIDENCE SUMMARY

{json.dumps(
    context.get("evidence_summary", {}),
    indent=2,
)}

TOP HISTORICAL EVIDENCE

{json.dumps(
    context.get("historical_evidence", [])[:1],
    indent=2,
)}

Return ONLY JSON.

The JSON object must contain:

- message_id
- action
- message_type
- reason
- confidence

No markdown.
No explanations outside the JSON.
"""

        return prompt

    # ==========================================================
    # BATCH
    # ==========================================================

    def build_batch_prompt(
        self,
        contexts: list[dict],
    ) -> str:
        """
        Build ONE prompt for multiple WhatsApp messages.
        """

        prompt = f"""
{self.system_prompt}

You are given multiple WhatsApp messages.

Predict one routing decision for each message independently.

Return ONLY a valid JSON ARRAY.

"""

        for i, context in enumerate(
            contexts,
            start=1,
        ):

            prompt += f"""

========================
MESSAGE {i}
========================

CURRENT MESSAGE

{json.dumps(
    context.get("current_message", {}),
    indent=2,
)}

USER CONTEXT

{json.dumps(
    context.get("user_context", {}),
    indent=2,
)}

GROUP CONTEXT

{json.dumps(
    context.get("group_context", {}),
    indent=2,
)}

BUSINESS CONTEXT

{json.dumps(
    context.get("business_context", {}),
    indent=2,
)}

RELATIONSHIP CONTEXT

{json.dumps(
    context.get("relationship_context", {}),
    indent=2,
)}

EVIDENCE SUMMARY

{json.dumps(
    context.get("evidence_summary", {}),
    indent=2,
)}

TOP HISTORICAL EVIDENCE

{json.dumps(
    context.get("historical_evidence", [])[:1],
    indent=2,
)}

"""

        prompt += """

Return ONLY a valid JSON ARRAY.

Each object must contain:

- message_id
- action
- message_type
- reason
- confidence

No markdown.
No explanations.
Only JSON.

"""

        return prompt