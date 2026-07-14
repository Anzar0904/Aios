# Agency Dashboard Guide

The Agency CRM Dashboard (`aios agency` or `aios agency dashboard`) provides a comprehensive health view of the agency's commercial pipeline.

---

## 1. Dashboard Layout

The dashboard presents information across three main widgets:

### Main Summary Panel
Calculates aggregate health metrics:
- **Active Leads count**: Total active prospects.
- **Closed Clients count**: Total active closed business relations.
- **Active Proposals count**: Pending commercial documents.
- **Weighted Pipeline Value**: Total pipeline expected revenue.
- **Pipeline Health Score**: Aggregate funnel conversion rating.

### Revenue Forecast Table
Breaks down the financials:
- **Expected Revenue**: Funnel stages multiplied by conversion probabilities.
- **Closed Revenue**: Realized contract values from won leads/accepted proposals.
- **Total Pipeline Value**: Sum of expected values of all active deals.

### Pending Follow-Ups Schedule
Details the upcoming or overdue client actions. Overdue events are colored in **bold red**.

---

## 2. Calculation Models

### Funnel Health Score Calculation
- Funnel starts at health `100`.
- Dropped to `50` if there are no leads (empty funnel).
- Dropped to `60` if there are no active leads (stagnant pipeline).

---

## 3. Invocation Commands

```bash
# Render the main agency dashboard
aios agency

# Render the revenue pipeline details
aios agency pipeline
```
