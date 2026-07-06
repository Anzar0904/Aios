# Research Intelligence — Security & Trust Model
**Sprint 11 · Milestone 1 (Foundation)** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define URL validation checks, process sandboxing, credential isolation, and safety limits for external retrievals.
* **Scope**: Governs HTTP client settings, scraper sub-runtimes, and key storage.
* **Audience**: Security Auditors, System Architects, and Integration Developers.
* **Related Documents**:
  * [05_SECURITY_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/05_SECURITY_GUIDELINES.md) - Core system security.
  * [research/research_intelligence.md](file:///Users/anzarakhtar/aios/docs/research/research_intelligence.md) - Conceptual vision.

---

## 1. Outbound URL Validation & SSRF Guards

When an agent triggers a web scraping or search request, the **Research Intelligence** module runs **SSRF (Server-Side Request Forgery) checks** on the target URI before initiating network calls:

```python
# Pseudo-implementation of URL validation
def validate_target_url(target_url: str) -> bool:
    parsed = urlparse(target_url)
    if parsed.scheme not in ('http', 'https'):
        return False  # Block local file:// or system gopher:// schemes
        
    try:
        resolved_ip = socket.gethostbyname(parsed.hostname)
    except socket.gaierror:
        return False
        
    # Block local loopback and private IP ranges
    ip = ip_address(resolved_ip)
    if ip.is_loopback or ip.is_private or ip.is_link_local:
        raise SecurityBoundaryViolation(f"Blocked request targeting private address: {resolved_ip}")
        
    return True
```

* **Scheme Restrictions**: Only standard `http` and `https` protocols are allowed.
* **IP Restrictions**: The system resolves domains to IPs and blocks requests to loopback (`127.0.0.1`), private ranges (`10.x.x.x`, `192.168.x.x`), and link-local addresses, preventing SSRF attacks targeting local services (like Redis or MinIO).

---

## 2. Scraping Sandboxes & Resource Limits

To prevent malicious sites from executing browser exploits or causing memory exhaustion:
* **Playwright Isolation**: Headless browsers run under a restricted sandboxed process with no access to local cookie jars, keychain systems, or filesystem paths outside the temporary workspace.
* **Size & Timeout Limits**:
  * Max download size: **10MB** per document.
  * Network fetch timeout: **15 seconds** per request.
* **Header Sanitization**: User-Agent and connection headers are generalized, stripping details that could link queries to the developer's identity.

---

## 3. Credential Isolation

* **Search API Keys**: External search keys (e.g. Google Search API, Bing Web Search) are stored in the database using SQLCipher (AES-256-GCM). Plaintext keys are never written to log files or injected into agent prompts.
* **Safe REPL Operations**: Agents run search tools within the `TaskExecutor`, allowing developers to monitor queries and cancel requests in real time.
