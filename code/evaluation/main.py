"""
Main evaluation pipeline for the WhatsApp Notification Router.

This version supports RESUMING from an existing output.csv.

Already completed predictions are loaded from output.csv.
The pipeline automatically starts from the next incomplete batch.

Example:
    72 completed messages
    batch_size = 3

    72 / 3 = 24 completed batches

    Next run starts from Batch 25.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import pandas as pd


# ------------------------------------------------------------------
# Add "code" directory to Python path
# ------------------------------------------------------------------

CODE_DIR = Path(__file__).resolve().parents[1]

if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))


# ------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------

from retrieval.evidence_retriever import EvidenceRetriever
from context.context_builder import ContextBuilder
from llm.decision_engine import DecisionEngine


def main():

    # ==============================================================
    # PATHS
    # ==============================================================

    code_root = Path(__file__).resolve().parents[1]

    project_root = code_root.parent

    processed_dataset = code_root / "data"

    output_path = project_root / "output.csv"


    # ==============================================================
    # LOAD MESSAGES
    # ==============================================================

    messages = pd.read_csv(
        processed_dataset / "messages_features.csv"
    )

    print("=" * 70)

    print(
        f"Loaded {len(messages)} messages"
    )

    print("=" * 70)


    # ==============================================================
    # INITIALIZE COMPONENTS
    # ==============================================================

    retriever = EvidenceRetriever()

    context_builder = ContextBuilder()

    decision_engine = DecisionEngine()


    # ==============================================================
    # BATCH SETTINGS
    # ==============================================================

    batch_size = 3

    total_batches = (
        len(messages) + batch_size - 1
    ) // batch_size


    # ==============================================================
    # LOAD PREVIOUS OUTPUT
    # ==============================================================

    all_predictions = []


    if output_path.exists():

        print(
            "\nExisting output.csv found."
        )

        previous_output = pd.read_csv(
            output_path
        )

        all_predictions = (
            previous_output
            .to_dict(orient="records")
        )

        print(
            f"Loaded "
            f"{len(all_predictions)} "
            f"previously completed predictions."
        )

    else:

        print(
            "\nNo existing output.csv found."
        )

        print(
            "Starting from Batch 1."
        )


    # ==============================================================
    # VALIDATE PREVIOUS OUTPUT
    # ==============================================================

    completed_messages = len(
        all_predictions
    )


    # Never allow more predictions than messages
    if completed_messages > len(messages):

        raise RuntimeError(
            f"output.csv contains "
            f"{completed_messages} predictions, "
            f"but dataset contains only "
            f"{len(messages)} messages."
        )


    # We expect completed output to consist of
    # complete batches, except for the final batch.
    if (
        completed_messages != 0
        and completed_messages % batch_size != 0
        and completed_messages != len(messages)
    ):

        raise RuntimeError(
            "\noutput.csv contains "
            f"{completed_messages} predictions.\n\n"
            "This does not represent a complete "
            "batch for the current batch size of "
            f"{batch_size}.\n\n"
            "Do NOT continue automatically because "
            "doing so could duplicate or skip messages.\n\n"
            "Please inspect output.csv first."
        )


    # ==============================================================
    # DETERMINE RESUME BATCH
    # ==============================================================

    start_batch = (
        completed_messages // batch_size
    )


    if completed_messages == len(messages):

        print(
            "\nAll messages are already processed."
        )

        print(
            f"Total predictions: "
            f"{completed_messages}"
        )

        print(
            f"Output file:\n"
            f"{output_path}"
        )

        return


    print(
        f"\nResuming from Batch "
        f"{start_batch + 1}/{total_batches}"
    )

    print(
        f"Remaining messages: "
        f"{len(messages) - completed_messages}"
    )


    # ==============================================================
    # PROCESS REMAINING BATCHES
    # ==============================================================

    for batch_number in range(
        start_batch,
        total_batches
    ):

        start = (
            batch_number * batch_size
        )

        end = min(
            start + batch_size,
            len(messages)
        )

        batch_messages = messages.iloc[
            start:end
        ]


        print("\n" + "=" * 70)

        print(
            f"Processing Batch "
            f"{batch_number + 1}/{total_batches}"
        )

        print(
            f"Messages in this batch: "
            f"{len(batch_messages)}"
        )

        print("=" * 70)


        # ----------------------------------------------------------
        # Build Context
        # ----------------------------------------------------------

        contexts = []

        evidences = []

        original_messages = []


        for _, row in (
            batch_messages.iterrows()
        ):

            message = row.to_dict()

            original_messages.append(
                message
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


        # ----------------------------------------------------------
        # LLM PREDICTION
        # ----------------------------------------------------------

        batch_predictions = (
            decision_engine.predict_batch(
                contexts
            )
        )


        # ----------------------------------------------------------
        # SAVE PREDICTIONS
        # ----------------------------------------------------------

        for (
            message,
            evidence,
            prediction
        ) in zip(
            original_messages,
            evidences,
            batch_predictions
        ):

            try:

                # ----------------------------------------------
                # Evidence IDs
                # ----------------------------------------------

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


                # ----------------------------------------------
                # Append prediction
                # ----------------------------------------------

                all_predictions.append({

                    "message_id":
                        message[
                            "message_id"
                        ],

                    "action":
                        prediction[
                            "action"
                        ],

                    "message_type":
                        prediction[
                            "message_type"
                        ],

                    "reason":
                        prediction[
                            "reason"
                        ],

                    "confidence":
                        prediction[
                            "confidence"
                        ],

                    "evidence_message_ids":
                        evidence_message_ids,

                })


                print(
                    f"✓ "
                    f"{message['message_id']} "
                    f"Completed"
                )


            except Exception as error:

                print(
                    f"✗ Error processing "
                    f"{message['message_id']}"
                )

                print(error)


                # Fallback at pipeline level
                all_predictions.append({

                    "message_id":
                        message[
                            "message_id"
                        ],

                    "action":
                        "digest",

                    "message_type":
                        "unknown",

                    "reason":
                        "Pipeline Error",

                    "confidence":
                        0.0,

                    "evidence_message_ids":
                        "none",

                })


        # ==========================================================
        # SAVE AFTER EVERY BATCH
        # ==========================================================

        output = pd.DataFrame(
            all_predictions
        )


        output.to_csv(
            output_path,
            index=False
        )


        print(
            "\n✓ Saved checkpoint:"
        )

        print(
            f"  {len(all_predictions)} "
            f"predictions saved"
        )

        print(
            f"  {output_path}"
        )


        # ==========================================================
        # WAIT BEFORE NEXT REQUEST
        # ==========================================================

        if batch_number != total_batches - 1:

            print(
                "\nWaiting 1 second before "
                "next batch..."
            )

            time.sleep(1)


    # ==============================================================
    # FINAL OUTPUT
    # ==============================================================

    final_output = pd.DataFrame(
        all_predictions
    )


    final_output.to_csv(
        output_path,
        index=False
    )


    print("\n" + "=" * 70)

    print(
        "Evaluation Completed Successfully"
    )

    print("=" * 70)

    print(
        f"Total Messages Processed : "
        f"{len(all_predictions)}"
    )

    print(
        f"Unique Message IDs       : "
        f"{final_output['message_id'].nunique()}"
    )

    print(
        f"Output saved to:\n"
        f"{output_path}"
    )

    print("=" * 70)


# ------------------------------------------------------------------
# Entry Point
# ------------------------------------------------------------------

if __name__ == "__main__":
    main()