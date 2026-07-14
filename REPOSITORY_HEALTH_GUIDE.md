# Repository Health Engine Guide

The Repository Health Engine calculates overall health scores for tracked repositories.

---

## 1. Health Scoring Algorithm

The repository health score is evaluated on a scale of `0` to `100` (where 100 represents a flawless environment). Points are deducted according to the following penalties:

### Issue Penalty
$$\text{Deduction} = \text{Open Issues} \times 5$$
Each unresolved issue decreases the health rating by 5 points.

### CI Build Failure Penalty
$$\text{Deduction} = \text{Failed CI Runs} \times 15$$
Each broken workflow run decreases the health rating by 15 points.

### PR Risk Average Penalty
$$\text{Deduction} = \text{Average PR Risk Score} \times 0.5$$
The risk rating average of all open PRs determines this penalty.

---

## 2. Health Check Execution

To recalculate and display the health score:

```bash
aios github health
```
