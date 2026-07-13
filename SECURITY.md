# Security Policy — Personal AI OS

We take the security of Personal AI OS seriously. This document describes our security policy, supported versions, and reporting guidelines.

## Supported Versions

Only the current release candidate and stable release branch receive security updates:

| Version | Supported |
| :--- | :---: |
| 1.0.x | Yes |
| < 1.0.0 | No |

## Security Best Practices
- **Telemetry and API Keys**: Restrict file system permissions of the configuration directory `.agent/` and files (e.g. `config.toml`, `.env`). Make sure they are not readable by other users on shared host systems.
- **Git Ignoring**: The repository standard `.gitignore` strictly blocks folder `.agent/` and local credential files. Do not force-add credentials folders to git tracking.
- **Terminal Execution**: The shell tool executes shell actions within the workspace boundary directory context. Do not bypass CLI sandbox policies.

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it immediately:
1. Do not open a public GitHub issue.
2. Email your report to: `security@aios.org` (mock contact for certification).
3. Include detailed reproduction steps, potential impact, and system configuration.

We will acknowledge receipt within 48 hours and work with you to coordinate a secure release fix.
