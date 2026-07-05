# Candidate Ranking Architecture

This document describes candidate ranking signals, freshness decay, and scoring configurations.

---

## 1. Multi-Signal Scoring

Candidates are ranked using a weighted linear combination of three signals:
* **Similarity Score ($S_{sim}$)**: Cosine similarity score returned from vector retrieval.
* **Importance Score ($S_{imp}$)**: Integer priority value (0 to 10) parsed from metadata payloads.
* **Freshness Score ($S_{fresh}$)**: Calculates time decay relative to the current time.

$$Score = w_{sim} \cdot S_{sim} + w_{imp} \cdot S_{imp} + w_{fresh} \cdot S_{fresh}$$

---

## 2. Exponential Freshness Decay

Freshness is computed using exponential decay:

$$S_{fresh} = e^{-\lambda \cdot \Delta t}$$

Where:
* $\Delta t$ is the difference in seconds between current time and the payload's `created_at` timestamp.
* $\lambda$ is the decay constant, configured by default to `0.00001` (halving freshness value approximately every 19 hours).
* Negative time differences are bounded to `0.0`.
