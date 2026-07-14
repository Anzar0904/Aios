# Conversational Memory Guide

This document describes how conversational memory tracks discussion history, references, and session states.

## 1. Overview
Conversational Memory manages active conversation states and maps referenced entities during interactions. By maintaining memory of past statements and actions, it provides a natural user experience, resolving context references, pronouns, and supporting follow-up questions.

## 2. Conversation States
The system maintains:
* **Active Session ID**: Tracks the current interactive conversation.
* **Message History**: Stores the sequence of user and assistant messages.
* **Referenced Objects**: Tracks projects, workflows, tasks, and goals discussed.
* **Historical Sessions**: Restores past conversation contexts.

## 3. Memory Integration
* **Semantic Memory indexing**: Conversation messages and summaries are indexed into the `conversation_memory` semantic vector repository.
* **Knowledge Graph Audit Trail**: Resolved intents and executed plans are linked to the active `Conversation` node inside the Universal Knowledge Graph using relationships like `REQUESTED` and `PLANNED`.

## 4. Usage
To see past conversation sessions, type `/history` in interactive mode.
To create a new conversation session, type `/conversation new`.
To resume a conversation session, type `/conversation resume <session_id>`.
To delete a conversation session, type `/conversation delete <session_id>`.
