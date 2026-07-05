# Qdrant Transport Architecture

This document describes the design, retry policies, error mapping, and low-level SDK wrapping of the Qdrant Transport layer in the Personal AI OS.

---

## 1. Transport Pattern Responsibility

The `QdrantTransport` is the **only** layer allowed to import `qdrant_client`. It wraps the raw SDK, manages the network connection, and handles connection failures, timeouts, and API retries.

---

## 2. Low-Level Connection Management

The connection is managed by `QdrantConnectionManager`:
* **Lazy Initialization**: Connects on the first query request to allow the OS to boot even if Qdrant is temporarily offline.
* **HTTP / gRPC**: Currently communicates using the HTTP/REST client, with full compatibility built-in for gRPC (prefer_grpc=False by default).
* **Failure Count**: Measures subsequent socket exceptions to flag the service status as degraded or offline.

---

## 3. Resilience & Retries

The `QdrantTransportImpl` interceptor wraps API calls in a retry loop:
* **Exponential Backoff**: If an operation fails, it sleeps for a progressive duration (e.g. `0.05s * 2^attempt`) and retries up to the configured retry count (default `3`).
* **Error Translation**: Low-level network faults, HTTP response conflicts (like 409 already exists), and connection timeouts are translated into clean system exceptions.
* **Latency Telemetry**: Measures operation durations in milliseconds and updates a rolling memory buffer of execution statistics.
