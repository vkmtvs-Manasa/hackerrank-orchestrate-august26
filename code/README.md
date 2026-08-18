# WhatsApp Notification Router — Code

## Overview

This directory contains the implementation for the WhatsApp Notification Router — an AI-powered system that classifies incoming WhatsApp messages into one of three actions: `notify`, `digest`, or `mute`.

The system uses message content and multimodal media (text, images, voice notes) together with personalized user, group, and business context and retrieved historical evidence to produce explainable routing decisions.

Key features

- Retrieval-augmented inference using historical evidence
- Multimodal processing (text, OCR on images, ASR on voice notes)
- LLM-based reasoning with validation and fallback handling
- Batch processing and checkpointing for long runs

---

## Architecture

High-level pipeline:

1. Ingest incoming messages from `dataset/messages.csv`.
2. Retrieve relevant historical evidence and build context (user, group, business, relationships).
3. Construct a compact LLM prompt with message + context + evidence summary.
4. Send prompt to the decision engine (Groq API → GPT-OSS-20B) and parse the JSON response.
5. Validate predictions and apply fallbacks when needed.
6. Write predictions to `output.csv`.

---

## Project structure

```
code/
├── context/
│   └── context_builder.py          # Build message-specific context
├── data/
│   ├── evidence_pool_clean.csv     # cleaned evidence pool for retrieval
│   ├── messages_features.csv       # processed message features
│   └── sample_message_features.csv # examples used for local evaluation
├── llm/
│   ├── decision_engine.py          # orchestrates prompt/LLM/validation
│   ├── groq_client.py              # HTTP client + retry handling for Groq
│   ├── prompt_builder.py           # builds structured prompts and templates
│   ├── prompt_template.txt         # canonical prompt used for inference
│   └── validator.py                # validates and normalizes model output
├── retrieval/
│   └── evidence_retriever.py       # retrieval logic (BM25/embeddings/etc)
├── evaluation/
│   └── main.py                     # entrypoint to run the full pipeline
├── test_context.py                 # unit / integration tests for context builder
├── retry_fallback.py               # retry tool for fallback predictions
└── README.md                       # (this file)
```

---

## Getting started

Prerequisites

- Python 3.10+
- pip

Install runtime dependencies:

```bash
pip install -r requirements.txt
# or the core packages:
pip install pandas python-dotenv groq
```

Configuration

1. Create a `.env` file in the repository root with the following variables:

```
GROQ_API_KEY="your_groq_api_key_here"
# Any other keys used by your LLM provider
```

2. Confirm the dataset is present under the `dataset/` folder (this repo includes the required CSVs and a `media/` subfolder).

Running the pipeline

From the repository root, run:

```bash
python code/evaluation/main.py
```

This will process messages in batches, call the LLM, validate results, and write `output.csv` in the repository root (or a path configured in the pipeline).

Checkpointing & retry

- The pipeline saves intermediate results after each completed batch so work is not lost on interruptions.
- Use `python code/retry_fallback.py` to retry specific fallback predictions without re-running the entire dataset.

---

## Prediction format

The pipeline produces `output.csv` with one row per incoming message. Columns (in exact order):

- `message_id` — incoming message ID
- `action` — one of `notify`, `digest`, or `mute`
- `message_type` — best-fit message category (e.g., `text`, `image`, `voice`, `scam`, `promotion`)
- `reason` — short human-readable explanation for the decision
- `confidence` — numeric value between `0.0` and `1.0`
- `evidence_message_ids` — semicolon-separated historical message IDs used as evidence, or `none`

Example row:

```
msg_001,notify,payment,"Time-sensitive payment notification.",0.94,msg_010;msg_021
```

---

## Design notes

- The system intentionally limits the number of evidence items in the prompt to control token usage.
- Validation steps ensure the model returns a well-formed JSON object. If validation fails, a safe fallback prediction is recorded and retriable via `retry_fallback.py`.
- The retrieval module is pluggable — you may switch between simple keyword/BM25 retrieval or vector embeddings.

---

## Development & testing

- Add unit tests next to modules (e.g., `test_context.py`).
- Use small batches when debugging to limit API usage.
- Sanitize user-supplied inputs and avoid logging secrets to the chat transcript (see repository README).

---

## Environment & security

- Read API keys from environment variables only — never commit secrets.
- The repo contains an `AGENTS.md` describing chat transcript logging; ensure you sanitize logs before submission.

---

## Troubleshooting

- Rate limits: `groq_client.py` implements retries with exponential backoff.
- Malformed responses: inspect `code/llm/validator.py` and enable verbose logging to capture raw model outputs.

---

## Contributing

Contributions are welcome. Please follow these guidelines:

1. Create feature branches for changes.
2. Add or update tests for any new behavior.
3. Keep README and prompts in sync with implementation.

---

## License

Specify the project license here if applicable.

---

If you want, I can also:
- Add a requirements.txt (based on imports used in the code),
- Update the repository-level README to match these changes, or
- Create a short HOWTO for running locally with a small sample dataset.
