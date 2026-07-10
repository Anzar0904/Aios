# Configuration Guide

This guide describes how to configure the AI OS subsystems.

---

## 1. Onboarding Wizard (`aios setup`)
Run the interactive onboarding flow:
```bash
aios setup
```
This guides you through setting:
- **AI LLM Provider**: Defaults to OpenRouter.
- **GitHub**: Set your username and access token.
- **Supabase**: Set URL and service role key.
- **Vercel**: Set API token.

---

## 2. Configuration Schema
All configurations are stored in `config/config.toml`. Credentials are saved securely with `0600` owner-only permissions inside `.agent/` subdirectory JSON files.
