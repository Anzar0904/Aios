# Text Chunking Engine Architecture

This document describes the design, metadata fields, and chunking strategies of the Chunking Service.

---

## 1. Engine Responsibilities

The `ChunkingService` splits long text documents into smaller chunks suitable for vector index insertion and context window restrictions. It creates structured `ChunkResult` outputs.

---

## 2. Strategies Supported

### 2.1 Fixed-size Character Chunking
* Splits text using a fixed character size count (e.g. `200` characters) with a configurable character overlap (e.g. `20` characters).
* Suitable for basic lookups and uniform text blocks.

### 2.2 Paragraph Chunking
* Inspects double newline occurrences (`\n\n`) to parse semantic paragraphs.
* Preserves paragraph boundaries for clean semantic boundaries.

### 2.3 Sliding Window Chunking
* Slides a window of character size over the text, moving by a fixed step size.
* Ensures overlapping data splits across chunks to prevent semantic boundary loss.

### 2.4 Token-Aware Chunking
* Estimates token counts using character-to-token ratios (approx. 4 characters per token).
* Aggregates words up to the maximum token budget count and flushes the chunk.
* Does not run expensive tokenizer libraries natively to keep the engine lightweight.
