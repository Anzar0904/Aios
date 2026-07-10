# Configuration Wizard Onboarding Report

This report outlines the interactive steps, validations, and credentials schema managed by the Setup Onboarding Wizard (`aios setup`).

---

## 1. Onboarding Interactive Steps
The setup wizard guides the developer through configuring the following integrations:

1. **AI Provider**: Prompts for AI Provider name, default model, and API Key.
2. **GitHub**: Prompts for username and Personal Access Token.
3. **Supabase**: Prompts for URL and Service Role Key.
4. **Vercel**: Prompts for Personal Access Token.
5. **Business Profile**: Saves company agency profile name and billing info.

---

## 2. Security & Credentials
All credential configurations are persisted inside `.agent/` subdirectory config files with `0600` owner-only permissions.
- `.agent/credentials/openrouter.json`
- `.agent/github/credentials.json`
- `.agent/supabase/credentials.json`
- `.agent/vercel/credentials.json`
