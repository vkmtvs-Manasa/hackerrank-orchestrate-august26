from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


# ==============================================================
# PATHS
# ==============================================================

PROJECT_ROOT = Path(__file__).resolve().parent

CODE_DIR = PROJECT_ROOT / "code"

DATA_DIR = CODE_DIR / "data"

OUTPUT_PATH = PROJECT_ROOT / "output.csv"


# Make code/ importable
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))


# ==============================================================
# IMPORT EXISTING PIPELINE COMPONENTS
# ==============================================================

from retrieval.evidence_retriever import EvidenceRetriever
from context.context_builder import ContextBuilder
from llm.decision_engine import DecisionEngine


# ==============================================================
# FALLBACK MESSAGE IDs
# ==============================================================

FALLBACK_IDS = {
    "msg_097",
    "msg_089",
    "msg_053",
}


def main():

    print("=" * 70)
    print("RETRY FALLBACK PREDICTIONS")
    print("=" * 70)


    # ==========================================================
    # LOAD OUTPUT
    # ==========================================================

    if not OUTPUT_PATH.exists():

        raise FileNotFoundError(
            f"output.csv not found:\n{OUTPUT_PATH}"
        )


    output = pd.read_csv(
        OUTPUT_PATH
    )


    print(
        f"Loaded output.csv with "
        f"{len(output)} rows."
    )


    # ==========================================================
    # LOAD ORIGINAL DATASET
    # ==========================================================

    messages_path = (
        DATA_DIR /
        "messages_features.csv"
    )


    messages = pd.read_csv(
        messages_path
    )


    print(
        f"Loaded dataset with "
        f"{len(messages)} messages."
    )


    # ==========================================================
    # CHECK FALLBACK IDs EXIST
    # ==========================================================

    existing_ids = set(
        output["message_id"]
    )


    for message_id in FALLBACK_IDS:

        if message_id not in existing_ids:

            raise RuntimeError(
                f"{message_id} is not present "
                "in output.csv."
            )


    # ==========================================================
    # SELECT ONLY FALLBACK MESSAGES
    # ==========================================================

    retry_messages = messages[
        messages["message_id"].isin(
            FALLBACK_IDS
        )
    ].copy()


    # Preserve the desired order
    retry_order = [
        "msg_097",
        "msg_089",
        "msg_053",
    ]


    retry_messages["retry_order"] = (
        retry_messages["message_id"]
        .map(
            {
                message_id: index
                for index, message_id
                in enumerate(retry_order)
            }
        )
    )


    retry_messages = (
        retry_messages
        .sort_values("retry_order")
        .drop(columns=["retry_order"])
    )


    print(
        f"Messages selected for retry: "
        f"{len(retry_messages)}"
    )


    print(
        retry_messages[
            "message_id"
        ].tolist()
    )


    if len(retry_messages) != 3:

        raise RuntimeError(
            "Expected exactly 3 fallback "
            f"messages, found {len(retry_messages)}."
        )


    # ==========================================================
    # INITIALIZE PIPELINE
    # ==========================================================

    retriever = EvidenceRetriever()

    context_builder = ContextBuilder()

    decision_engine = DecisionEngine()


    # ==========================================================
    # BUILD CONTEXTS
    # ==========================================================

    contexts = []

    evidences = []

    original_messages = []


    for _, row in retry_messages.iterrows():

        message = row.to_dict()

        original_messages.append(
            message
        )


        print(
            f"\nBuilding context for "
            f"{message['message_id']}..."
        )


        evidence = retriever.retrieve(
            message
        )

        evidences.append(
            evidence
        )


        context = (
            context_builder.build_context(
                message,
                evidence
            )
        )

        contexts.append(
            context
        )


    # ==========================================================
    # CALL LLM ON ONLY 3 MESSAGES
    # ==========================================================

    print("\nCalling GPT OSS 20B for 3 fallback messages...")

    predictions = (
        decision_engine.predict_batch(
            contexts
        )
    )


    # ==========================================================
    # CHECK RESPONSE COUNT
    # ==========================================================

    if len(predictions) != 3:

        raise RuntimeError(
            "Expected 3 predictions, "
            f"received {len(predictions)}."
        )


    # ==========================================================
    # UPDATE ONLY SUCCESSFUL RETRIES
    # ==========================================================

    updated_count = 0

    for (
        message,
        evidence,
        prediction
    ) in zip(
        original_messages,
        evidences,
        predictions
    ):

        message_id = (
            message["message_id"]
        )


        # ------------------------------------------------------
        # Evidence IDs
        # ------------------------------------------------------

        evidence_ids = [

            item["message_id"]

            for item in evidence

            if item.get("message_id")

        ]


        evidence_message_ids = (

            ";".join(
                evidence_ids
            )

            if evidence_ids

            else "none"
        )


        # ------------------------------------------------------
        # Determine whether retry actually succeeded
        # ------------------------------------------------------

        reason = str(
            prediction.get(
                "reason",
                ""
            )
        )


        is_fallback = (
            "Fallback prediction"
            in reason
        )


        if is_fallback:

            print(
                f"\n⚠ {message_id} "
                "still returned fallback."
            )

            print(
                "Keeping the existing prediction."
            )

            continue


        # ------------------------------------------------------
        # Find corresponding output row
        # ------------------------------------------------------

        output_index = output.index[
            output["message_id"]
            == message_id
        ]


        if len(output_index) != 1:

            raise RuntimeError(
                f"Expected exactly one output "
                f"row for {message_id}, found "
                f"{len(output_index)}."
            )


        index = output_index[0]


        # ------------------------------------------------------
        # Replace ONLY this row
        # ------------------------------------------------------

        output.loc[
            index,
            "action"
        ] = prediction[
            "action"
        ]


        output.loc[
            index,
            "message_type"
        ] = prediction[
            "message_type"
        ]


        output.loc[
            index,
            "reason"
        ] = prediction[
            "reason"
        ]


        output.loc[
            index,
            "confidence"
        ] = prediction[
            "confidence"
        ]


        output.loc[
            index,
            "evidence_message_ids"
        ] = evidence_message_ids


        updated_count += 1


        print(
            f"✓ {message_id} "
            "successfully updated."
        )


    # ==========================================================
    # SAVE OUTPUT
    # ==========================================================

    output.to_csv(
        OUTPUT_PATH,
        index=False
    )


    # ==========================================================
    # FINAL CHECK
    # ==========================================================

    final_output = pd.read_csv(
        OUTPUT_PATH
    )


    print("\n" + "=" * 70)

    print(
        "Fallback Retry Completed"
    )

    print("=" * 70)

    print(
        f"Rows                  : "
        f"{len(final_output)}"
    )

    print(
        f"Unique message IDs    : "
        f"{final_output['message_id'].nunique()}"
    )

    print(
        f"Rows successfully updated: "
        f"{updated_count}"
    )


    remaining_fallbacks = (
        final_output["reason"]
        .astype(str)
        .str.contains(
            "Fallback prediction",
            case=False,
            na=False
        )
        .sum()
    )


    print(
        f"Remaining fallbacks   : "
        f"{remaining_fallbacks}"
    )

    print(
        f"\nOutput saved to:\n"
        f"{OUTPUT_PATH}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()