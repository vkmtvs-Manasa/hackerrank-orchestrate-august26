# WhatsApp Notification Router

## Overview

This project implements an AI-powered WhatsApp Notification Routing System developed for the HackerRank Hackathon.

The system predicts the most appropriate notification action for every incoming WhatsApp message using:

- Current message information
- User context
- Group context
- Business context
- User-business relationship information
- Retrieved historical evidence
- An LLM-based decision engine

The system uses retrieval-augmented contextual information to provide the LLM with relevant historical interaction evidence before making a routing decision.

---

## Architecture

The overall pipeline is:

```text
WhatsApp Messages
        │
        ▼
Evidence Retrieval
        │
        ▼
Context Builder
        │
        ├── User Context
        ├── Group Context
        ├── Business Context
        ├── Relationship Context
        └── Historical Evidence
        │
        ▼
Prompt Builder
        │
        ▼
Groq API
        │
        ▼
GPT OSS 20B
        │
        ▼
JSON Prediction
        │
        ▼
Prediction Validator
        │
        ▼
output.csv 
---

## Project Structure
```text
code/
│
├── context/
│   └── context_builder.py
│
├── data/
│   ├── evidence pool clean.csv
│   ├── messages_features.csv
│   └── sample_message_features.csv
│
├── llm/
│   ├── decision_engine.py
│   ├── groq_client.py
│   ├── prompt_builder.py
│   ├── prompt_template.txt
│   └── validator.py
│
├── retrieval/
│   └── evidence_retriever.py
│
├── evaluation/
│   └── main.py
│
├── test_context.py
│
├── retry_fallback.py
│
└── README.md
---
## Workflow
```text
The system follows the following pipeline:

1.Load processed messages.
2.Retrieve relevant historical evidence.
3.Build user, group, business, and relationship context.
4.Construct the LLM prompt.
5.Send the contextual prompt to the Groq API.
6.Generate routing predictions using GPT OSS 20B.
7.Parse and validate the JSON response.
8.Attach retrieved evidence message IDs.
9.Save predictions to output.csv.

## Context Construction

For every incoming message, the system builds a structured context containing:

Current message
Timestamp
User information
Group information
Business information
User-business relationship
Historical evidence
Evidence summary

The evidence summary contains aggregated historical interaction information such as:

Messages opened
Messages replied to
Messages dismissed
Messages reported
Messages followed by muting

This contextual information is provided to the LLM to support the routing decision.

## Retrieval

Historical evidence is retrieved before LLM inference.

The retrieved evidence is used to provide information about previous interactions and user behavior.

The prompt includes a limited amount of historical evidence to control prompt size and API token usage.

## LLM

The final evaluation uses the Groq API with:

Model: openai/gpt-oss-20b

The model is instructed to return structured JSON predictions.

For batch processing, multiple messages are sent in a single request and each message is evaluated independently.

## Prediction Format

Each prediction contains:

message_id
action
message_type
reason
confidence

The final CSV additionally contains:

evidence_message_ids

## Requirements
Python 3.10+
pandas
python-dotenv
groq

## Install the dependencies with:

pip install pandas python-dotenv groq

## Environment Variables

Create a .env file in the project root.

Groq_API_KEY="Abxxxxxxxxxxxxxxxxxxx"

## Running the Project

From the project root:

python code/evaluation/main.py

The generated predictions are saved to:

output.csv

## Batch Processing

The evaluation pipeline processes messages in batches.

The final evaluation used:

Batch size: 3

Batch processing reduces the number of individual API requests while allowing the evaluation to handle the complete dataset.

## Checkpoint and Resume

The evaluation pipeline saves output.csv after completed batches.

This provides checkpointing for long-running API-based inference.

If the process is interrupted because of:

API rate limits
Network errors
Process interruption
Other temporary failures

the already generated predictions remain stored in output.csv.

The pipeline can use the existing output to continue the evaluation rather than unnecessarily regenerating completed predictions.

## Rate Limit Handling

The Groq client includes retry handling for API rate-limit responses.

When a rate limit is encountered, the client waits before retrying the request.

Because large contextual prompts can consume a significant number of tokens, checkpointing is used to preserve completed predictions during long-running evaluation.

## Prediction Validation

The decision engine validates the LLM response before adding it to the final output.

The expected prediction fields are:

message_id
action
message_type
reason
confidence

Invalid model responses can result in a fallback prediction so that a single invalid response does not terminate the complete evaluation pipeline.

## Fallback Retry

A separate helper script is included:

retry_fallback.py

This script can be used to retry specific messages that received fallback predictions.

It does not require rerunning the complete dataset.

The script:

1.Loads the existing output.csv.
2.dentifies the selected fallback messages.
3.Rebuilds their contexts.
4.Sends them through the existing decision engine.
5.Replaces only successfully regenerated predictions.
6.Preserves all other predictions.

## Output

The final prediction file is:

output.csv

The required columns are:

message_id
action
message_type
reason
confidence
evidence_message_ids

Each row corresponds to one input message.

Example:

message_id,action,message_type,reason,confidence,evidence_message_ids
msg_001,notify,payment,"Time-sensitive payment notification.",0.94,message_010;message_021
msg_002,mute,scam,"The message contains suspicious information.",0.92,message_031;message_045

## Final Evaluation

The final evaluation generated predictions for all messages in the evaluation dataset.

The final output.csv was checked for:

.Correct number of rows
.Unique message IDs
.Required output columns
.Prediction validity
.Pipeline errors
.Fallback predictions

## Technologies

.Python
.Pandas
.Groq API
.GPT OSS 20B
.JSON
.CSV
.Retrieval-based contextual evidence
.Batch LLM inference



