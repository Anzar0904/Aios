# n8n Integration Diagnostics

- **Diagnostics Status**: Awaiting Runtime Configuration
- **Credentials Configured**: True

## Diagnostic Check Log

The following issues were detected:

### [Missing configuration] Neither Email + Password nor API Key/Bearer Token is configured.
**Remediation**: Set the N8N_EMAIL and N8N_PASSWORD, or N8N_API_KEY environment variables in the runtime environment.

### [Server unavailable] Could not connect to n8n server at http://localhost:5678.
**Remediation**: Ensure the self-hosted n8n server is started and listening on the configured port (e.g. run 'n8n start' or check Docker container status).

