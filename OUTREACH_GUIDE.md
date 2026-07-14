# Outreach Guide

The Outreach Engine handles procedural drafting of outbound business communications across different messaging channels.

---

## 1. Outreach Channels

| Channel | Template Purpose | Output Format |
|---|---|---|
| `cold_email` | Introduces automation capabilities and suggests discovery meetings. | Subject + Body |
| `follow_up` | Polite second-touch hook for unresponsive prospects. | Re: Subject + Body |
| `linkedin` | Brief, professional connection request. | Body (<300 chars) |
| `discovery` | Formulates questions to prep for upcoming kickoff calls. | Subject + Questionnaire |
| `meeting_request` | Dispatches scheduling links and context updates. | Subject + Link Invite |

---

## 2. Local Model Routing

When drafting outreaches, the Outreach Engine queries the **Model Router**:
- Checks if the active project defines model preferences (e.g. `qwen3.5` or `gemma3:12b` for `Agency` project).
- Routes the drafting task to the optimal model.
- Speeds up delivery times and keeps processing local on dev machines.

---

## 3. Invocation Commands

```bash
# Display outreach history log
aios agency outreach

# Draft a cold email outreach for a lead
aios agency outreach generate <lead_id> cold_email

# Draft a LinkedIn connection message for a lead
aios agency outreach generate <lead_id> linkedin
```
