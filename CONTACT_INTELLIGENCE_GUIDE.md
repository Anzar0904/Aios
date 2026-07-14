# Contact Intelligence Guide

The Contact Intelligence Layer manages records of clients, partners, decision-makers, and companies to coordinate targeted communications.

---

## 1. Contact Registry

Tracks individual profiles linked to companies:

```yaml
contact_id: unique-uuid-identifier
name: Sarah Connor
email: sarah.connor@cyberdyne.ai
phone: +1-408-555-0199
company_id: cyberdyne-company-id
role: VP of Operations
linkedin: https://linkedin.com/in/sarah-connor-cyberdyne
status: active
source: Inbound Referral
notes: Interested in deployment pipelines and custom automations.
tags:
  - decision_maker
  - tech
```

---

## 2. Company Registry

Tracks organization profiles, including their industries, sizes, location, decision makers list, and client statuses:

```yaml
company_id: unique-uuid-identifier
name: Cyberdyne Systems
industry: Robotics & AI
website: https://cyberdyne.ai
size: 500-1000
location: Sunnyvale, CA
services:
  - Automation
  - AI Development
decision_makers:
  - sarah-connor-contact-id
client_status: active
projects:
  - project-alpha-id
```

---

## 3. Knowledge Graph Linkages

- When a contact is registered, it receives a `person` entity.
- When a company is registered, it receives a `company` entity.
- An edge of type `WORKS_FOR` is constructed from `person` to `company`.
- Meetings involving these participants generate `ATTENDED` edges linking the participant's `person` node to the `meeting` node.
