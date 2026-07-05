# Qdrant Platform Diagnostics Report

- **Active Alerts**: []
- **Remediations**: []

---

## 1. Diagnostics Analysis

* **`QDRANT_UNREACHABLE`**: Triggered when connection manager is unable to connect to the Qdrant instance.
  * *Remediation*: "Ensure local native Qdrant service is running at 127.0.0.1:6333."
* **`SSL_VERSION_CONFLICT`**: Triggered when client attempts connection via HTTPS to an HTTP-only Qdrant host.
  * *Remediation*: "Ensure QDRANT_HTTPS is configured correctly. Set HTTPS=False for localhost."
