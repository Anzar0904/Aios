# Rate Limiting & Back-Off Spec
**Sprint 11 · Milestone 2** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define token-bucket configurations, requests delay variables, and HTTP 429 response handling policies.
* **Scope**: Governs rate-limit controllers, back-off timers, and error recovery queues.
* **Audience**: DBAs, Backend Developers, and System Architects.
* **Related Documents**:
  * [research/security_model.md](file:///Users/anzarakhtar/aios/docs/research/security_model.md) - Security path guards.
  * [research/source_discovery/crawler_architecture.md](file:///Users/anzarakhtar/aios/docs/research/source_discovery/crawler_architecture.md) - Crawler structures.

---

## 1. Token-Bucket Rate Limiting

To prevent getting blocked or causing high load on target hosts, the crawling engine enforces **Token-Bucket Rate Limiting** per domain:
* **Bucket Capacity**: Maximum of **5 tokens** per domain bucket.
* **Refill Rate**: **1 token** refilled every **2 seconds**.
* **Request Throttle**: Each worker thread must acquire a token before initiating an HTTP connection. If no tokens are available, the thread sleeps until a token refills.

---

## 2. Jittered Request Delays

To prevent requests from appearing like automated scripts (which triggers blocking):
* **Delay Range**: The crawler injects a random delay between **1.0 and 3.0 seconds** between consecutive requests to the same domain.
* **Jitter Formula**:
  $$\text{Delay} = \text{Base Delay} + \text{random}(0.0, 1.0) \times \text{Jitter Factor}$$

---

## 3. HTTP 429 Too Many Requests Mitigation

When a target server returns an HTTP 429 status (Rate Limit Exceeded):
1. **Read Retry-After**: The HTTP adapter checks for the `Retry-After` header. If present, it uses that value as the wait duration.
2. **Exponential Back-off**: If the header is missing, the worker thread applies exponential back-off:
   $$\text{Wait Duration} = 2^{\text{attempt}} \times \text{Baseline Duration} + \text{jitter}$$
3. **Queue Pause**: The system pauses all active tasks targeting that domain. If a domain hits the retry limit (e.g. 5 failures), the crawler marks the tasks as blocked, alerting the developer.
