# WhatsApp Notification Router - Architecture

## Goal

Build an AI-powered notification routing system that decides whether an incoming WhatsApp message should be:

- Notify
- Digest
- Mute

using multimodal understanding and personalized context.

---

## High-Level Pipeline

Incoming Message
        ↓
Message Understanding
        ↓
Context Retrieval
        ↓
Reasoning Engine
        ↓
Output Generation

---

## Modules

### 1. Message Loader

### 2. User Context Retriever

### 3. Group Context Retriever

### 4. Business Context Retriever

### 5. History Retriever

### 6. Image Processor

### 7. Voice Processor

### 8. Decision Engine

### 9. Output Writer

---

## Data Sources

- messages.csv
- users.csv
- groups.csv
- group_members.csv
- business_accounts.csv
- user_business_history.csv
- message_history.csv
- message_events.csv
- images.csv
- voice_notes.csv

---

## Development Plan

- [ ] Understand dataset
- [ ] Build retrieval layer
- [ ] Build multimodal processing
- [ ] Build reasoning engine
- [ ] Generate output.csv