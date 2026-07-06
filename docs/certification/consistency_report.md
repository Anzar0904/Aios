# Documentation Consistency Report

> *Generated: 2026-07-06T11:40:19Z*

---

## Summary

| Check | Count |
|-------|-------|
| Markdown Errors | 0 |
| Mermaid Errors | 0 |
| Formatting Warnings | 25 |
| Duplicate Sections | 9 |
| **Consistency Score** | **65.0%** |

---

## Markdown Formatting

**0 errors · 25 warnings · 143 passes**

### Warnings

| File | Line | Check | Message |
|------|------|-------|---------|
| `docs/03_IMPLEMENTATION_GUIDELINES.md` | — | `markdown.h1_multiple` | Multiple H1 headings found (2); expected exactly one |
| `docs/07_DOCUMENTATION_GUIDELINES.md` | — | `markdown.h1_multiple` | Multiple H1 headings found (2); expected exactly one |
| `docs/20_OPERATIONS_MANUAL.md` | — | `markdown.h1_multiple` | Multiple H1 headings found (2); expected exactly one |
| `docs/20_OPERATIONS_MANUAL.md` | 57 | `markdown.heading_skip` | Heading level skipped from H1 to H3 at line 57: '2.2 Active Configuration (`config/config.toml`)' |
| `docs/architecture/KERNEL_SPECIFICATION.md` | 2 | `markdown.heading_skip` | Heading level skipped from H1 to H3 at line 2: 'Personal AI OS — Version 0.1 (MVP)' |
| `docs/deployment/OPERATIONS_MANUAL.md` | — | `markdown.h1_multiple` | Multiple H1 headings found (2); expected exactly one |
| `docs/deployment/OPERATIONS_MANUAL.md` | 57 | `markdown.heading_skip` | Heading level skipped from H1 to H3 at line 57: '2.2 Active Configuration (`config/config.toml`)' |
| `docs/deployment/README.md` | — | `markdown.h1_multiple` | Multiple H1 headings found (6); expected exactly one |
| `docs/guides/DOCUMENTATION_GUIDELINES.md` | — | `markdown.h1_multiple` | Multiple H1 headings found (2); expected exactly one |
| `docs/guides/ENGINEERING_CONSTITUTION.md` | 2 | `markdown.heading_skip` | Heading level skipped from H1 to H3 at line 2: 'Personal AI OS — Version 1.0' |
| `docs/guides/IMPLEMENTATION_GUIDELINES.md` | — | `markdown.h1_multiple` | Multiple H1 headings found (2); expected exactly one |
| `docs/operations/backup_restore.md` | — | `markdown.h1_multiple` | Multiple H1 headings found (8); expected exactly one |
| `docs/operations/backup_restore.md` | 133 | `markdown.heading_skip` | Heading level skipped from H1 to H3 at line 133: 'Qdrant Restore' |
| `docs/operations/backup_restore.md` | 146 | `markdown.heading_skip` | Heading level skipped from H1 to H3 at line 146: 'Configuration Restore' |
| `docs/operations/deployment.md` | — | `markdown.h1_multiple` | Multiple H1 headings found (5); expected exactly one |
| `docs/operations/deployment.md` | 62 | `markdown.heading_skip` | Heading level skipped from H1 to H3 at line 62: '4. Configure Environment' |
| `docs/operations/deployment.md` | 82 | `markdown.heading_skip` | Heading level skipped from H1 to H3 at line 82: '5. Run Database Migrations' |
| `docs/operations/deployment.md` | 95 | `markdown.heading_skip` | Heading level skipped from H1 to H3 at line 95: '7. Verify Deployment' |
| `docs/operations/local_setup.md` | — | `markdown.h1_multiple` | Multiple H1 headings found (11); expected exactly one |
| `docs/operations/local_setup.md` | 39 | `markdown.heading_skip` | Heading level skipped from H1 to H3 at line 39: '3. Start External Services' |
| `docs/operations/local_setup.md` | 92 | `markdown.heading_skip` | Heading level skipped from H1 to H3 at line 92: '5. Configure AIOS' |
| `docs/operations/monitoring.md` | — | `markdown.h1_multiple` | Multiple H1 headings found (5); expected exactly one |
| `docs/operations/startup.md` | — | `markdown.h1_multiple` | Multiple H1 headings found (6); expected exactly one |
| `docs/operations/troubleshooting.md` | — | `markdown.h1_multiple` | Multiple H1 headings found (14); expected exactly one |
| `docs/runtime/RUNTIME_INTELLIGENCE_DIAGNOSTICS.md` | 3 | `markdown.heading_skip` | Heading level skipped from H1 to H3 at line 3: 'Diagnostics State: HEALTHY' |

---

## Mermaid Syntax

**0 errors · 0 warnings**

*All Mermaid blocks are syntactically valid.* ✅

---

## Duplicate Sections

| File | Heading | Occurrences | Lines |
|------|---------|-------------|-------|
| `docs/03_IMPLEMENTATION_GUIDELINES.md` | `## 2. scope` | 2 | 26, 110 |
| `docs/07_DOCUMENTATION_GUIDELINES.md` | `## document metadata` | 2 | 6, 68 |
| `docs/CHANGELOG.md` | `### added` | 5 | 9, 39, 47, 55, 62 |
| `docs/generated/db_models.md` | `### affectedcomponent` | 2 | 1087, 1106 |
| `docs/generated/db_models.md` | `### affectedfile` | 2 | 1144, 1164 |
| `docs/generated/db_models.md` | `### executionmetrics` | 2 | 2870, 2891 |
| `docs/generated/db_models.md` | `### executionresult` | 2 | 2943, 2965 |
| `docs/generated/db_models.md` | `### executionsession` | 2 | 2987, 3012 |
| `docs/generated/db_models.md` | `### intentresult` | 2 | 3629, 3647 |
| `docs/generated/db_models.md` | `### reasoningcontext` | 2 | 4497, 7151 |
| `docs/generated/db_models.md` | `### validationsummary` | 2 | 5922, 5943 |
| `docs/guides/DOCUMENTATION_GUIDELINES.md` | `## document metadata` | 2 | 6, 68 |
| `docs/guides/IMPLEMENTATION_GUIDELINES.md` | `## 2. scope` | 2 | 26, 110 |
| `docs/reference/api_reference.md` | `### constructor` | 5 | 3634, 4942, 5744, 6785, 6911 |
| `docs/reference/api_reference.md` | `### lifecycle` | 15 | 685, 1930, 3640, 4527, 4580, 4906, 4982, 5708, 5762, 6256, 6627, 6681, 6801, 6887, 6953 |
| `docs/reference/api_reference.md` | `### methods` | 119 | 149, 251, 311, 370, 583, 639, 711, 787, 871, 1004, 1062, 1178, 1276, 1373, 1435, 1463, 1483, 1517, 1609, 1637, 1712, 1766, 1855, 1956, 2003, 2025, 2109, 2142, 2184, 2256, 2352, 2412, 2462, 2514, 2588, 2645, 2761, 2831, 2903, 3031, 3087, 3116, 3419, 3481, 3509, 3563, 3664, 3747, 3775, 3829, 4017, 4088, 4143, 4186, 4280, 4439, 4468, 4547, 4600, 4739, 4856, 4880, 4948, 5018, 5052, 5072, 5138, 5171, 5301, 5321, 5341, 5394, 5446, 5474, 5531, 5570, 5590, 5610, 5651, 5750, 5798, 5834, 5870, 5906, 5926, 6018, 6078, 6116, 6223, 6274, 6315, 6342, 6511, 6594, 6657, 6717, 6791, 6837, 6917, 6989, 7120, 7193, 7226, 7320, 7340, 7386, 7439, 7524, 7553, 7610, 7668, 7726, 7755, 7852, 7911, 8009, 8093, 8226, 8282 |
| `docs/reference/api_reference.md` | `#### `__init__` (initialization)` | 13 | 687, 1932, 3642, 4529, 4582, 4908, 4984, 5710, 5764, 6258, 6683, 6803, 6955 |
| `docs/reference/api_reference.md` | `#### `archive`` | 3 | 179, 1096, 2679 |
| `docs/reference/api_reference.md` | `#### `cancel`` | 2 | 765, 5214 |
| `docs/reference/api_reference.md` | `#### `commit`` | 2 | 3949, 4627 |
| `docs/reference/api_reference.md` | `#### `connect`` | 2 | 4950, 5752 |
| `docs/reference/api_reference.md` | `#### `consume`` | 3 | 3089, 7526, 7728 |
| `docs/reference/api_reference.md` | `#### `create_session`` | 5 | 2258, 2905, 5627, 7228, 7476 |
| `docs/reference/api_reference.md` | `#### `delete_memory`` | 2 | 3891, 7037 |
| `docs/reference/api_reference.md` | `#### `delete`` | 2 | 4714, 5685 |
| `docs/reference/api_reference.md` | `#### `execute`` | 2 | 741, 4602 |
| `docs/reference/api_reference.md` | `#### `generate_recommendations`` | 3 | 5054, 5908, 6793 |
| `docs/reference/api_reference.md` | `#### `generate_reports`` | 2 | 6060, 6767 |
| `docs/reference/api_reference.md` | `#### `generate_rollback_plan`` | 2 | 2977, 8157 |
| `docs/reference/api_reference.md` | `#### `get_all_types`` | 4 | 3809, 5376, 5428, 7419 |
| `docs/reference/api_reference.md` | `#### `get_configuration`` | 4 | 3797, 5364, 5416, 7407 |
| `docs/reference/api_reference.md` | `#### `get_diagnostics`` | 9 | 2394, 3453, 5020, 5106, 5976, 6028, 6673, 6727, 7175 |
| `docs/reference/api_reference.md` | `#### `get_health`` | 6 | 2386, 3445, 5098, 6020, 6719, 7167 |
| `docs/reference/api_reference.md` | `#### `get_history`` | 7 | 817, 1224, 4228, 6542, 7955, 8039, 8113 |
| `docs/reference/api_reference.md` | `#### `get_manager`` | 3 | 5836, 5872, 6080 |
| `docs/reference/api_reference.md` | `#### `get_profile`` | 2 | 2763, 4741 |
| `docs/reference/api_reference.md` | `#### `get_provider`` | 3 | 2414, 3579, 5074 |
| `docs/reference/api_reference.md` | `#### `get_recommendations`` | 8 | 1465, 2005, 3461, 5303, 5572, 6052, 6751, 7322 |
| `docs/reference/api_reference.md` | `#### `get_registry`` | 4 | 5808, 5844, 5880, 6088 |
| `docs/reference/api_reference.md` | `#### `get_session`` | 5 | 803, 1210, 6528, 6877, 7244 |
| `docs/reference/api_reference.md` | `#### `get_statistics`` | 8 | 1833, 2378, 3437, 6044, 6743, 6945, 7102, 7159 |
| `docs/reference/api_reference.md` | `#### `get_stats`` | 2 | 5852, 5888 |
| `docs/reference/api_reference.md` | `#### `get_telemetry`` | 3 | 5090, 6036, 6735 |
| `docs/reference/api_reference.md` | `#### `heartbeat`` | 2 | 5241, 7297 |
| `docs/reference/api_reference.md` | `#### `history`` | 3 | 205, 1126, 2709 |
| `docs/reference/api_reference.md` | `#### `initialize` (initialization)` | 11 | 693, 1938, 3648, 4914, 4990, 5716, 5770, 6629, 6689, 6809, 6961 |
| `docs/reference/api_reference.md` | `#### `log_error`` | 3 | 5028, 5114, 6659 |
| `docs/reference/api_reference.md` | `#### `publish_execution_report`` | 2 | 3005, 7642 |
| `docs/reference/api_reference.md` | `#### `publish_generation_report`` | 2 | 1686, 7702 |
| `docs/reference/api_reference.md` | `#### `record`` | 3 | 151, 1064, 2647 |
| `docs/reference/api_reference.md` | `#### `register_provider`` | 5 | 1180, 2426, 3565, 4549, 6276 |
| `docs/reference/api_reference.md` | `#### `restore`` | 3 | 192, 1111, 2694 |
| `docs/reference/api_reference.md` | `#### `searchmetadata`` | 3 | 226, 1151, 2734 |
| `docs/reference/api_reference.md` | `#### `start_session`` | 2 | 1639, 7441 |
| `docs/reference/api_reference.md` | `#### `start` (runtime)` | 9 | 4920, 4996, 5722, 5776, 6635, 6695, 6815, 6889, 6967 |
| `docs/reference/api_reference.md` | `#### `statistics`` | 3 | 218, 1141, 2724 |
| `docs/reference/api_reference.md` | `#### `stop` (cleanup)` | 9 | 4926, 5002, 5728, 5782, 6641, 6701, 6821, 6895, 6973 |
| `docs/reference/api_reference.md` | `#### `store_execution_summary`` | 2 | 2991, 7628 |
| `docs/reference/api_reference.md` | `#### `update`` | 4 | 165, 1080, 2663, 4698 |
| `docs/reference/services.md` | `#### constructor` | 5 | 3420, 4695, 5465, 6476, 6611 |
| `docs/reference/services.md` | `#### lifecycle methods` | 15 | 553, 1764, 3431, 4294, 4345, 4661, 4739, 5431, 5487, 5963, 6324, 6376, 6501, 6585, 6657 |
| `docs/reference/services.md` | `#### public methods` | 119 | 27, 127, 185, 242, 453, 507, 577, 651, 733, 864, 920, 1034, 1130, 1225, 1285, 1311, 1329, 1361, 1451, 1477, 1550, 1602, 1689, 1788, 1833, 1853, 1935, 1966, 2006, 2076, 2170, 2228, 2276, 2326, 2398, 2453, 2567, 2635, 2705, 2831, 2885, 2912, 3213, 3273, 3299, 3351, 3453, 3534, 3560, 3612, 3798, 3867, 3920, 3961, 4053, 4210, 4237, 4312, 4363, 4500, 4615, 4637, 4705, 4773, 4805, 4823, 4887, 4918, 5046, 5064, 5082, 5133, 5183, 5209, 5264, 5301, 5319, 5337, 5376, 5475, 5521, 5555, 5589, 5623, 5641, 5731, 5789, 5825, 5930, 5979, 6018, 6043, 6210, 6291, 6352, 6410, 6491, 6535, 6621, 6691, 6820, 6891, 6922, 7014, 7032, 7076, 7127, 7210, 7237, 7292, 7348, 7404, 7431, 7526, 7583, 7679, 7761, 7892, 7946 |
| `docs/reference/services.md` | `##### `__init__` (initialization)` | 13 | 555, 1766, 3433, 4296, 4347, 4663, 4741, 5433, 5489, 5965, 6378, 6503, 6659 |
| `docs/reference/services.md` | `##### `archive`` | 3 | 57, 954, 2487 |
| `docs/reference/services.md` | `##### `cancel`` | 2 | 631, 4961 |
| `docs/reference/services.md` | `##### `commit`` | 2 | 3732, 4390 |
| `docs/reference/services.md` | `##### `connect`` | 2 | 4707, 5477 |
| `docs/reference/services.md` | `##### `consume`` | 3 | 2887, 7212, 7406 |
| `docs/reference/services.md` | `##### `create_session`` | 5 | 2078, 2707, 5354, 6924, 7164 |
| `docs/reference/services.md` | `##### `delete_memory`` | 2 | 3674, 6739 |
| `docs/reference/services.md` | `##### `delete`` | 2 | 4477, 5410 |
| `docs/reference/services.md` | `##### `execute`` | 2 | 607, 4365 |
| `docs/reference/services.md` | `##### `generate_recommendations`` | 3 | 4807, 5625, 6493 |
| `docs/reference/services.md` | `##### `generate_reports`` | 2 | 5773, 6460 |
| `docs/reference/services.md` | `##### `generate_rollback_plan`` | 2 | 2779, 7825 |
| `docs/reference/services.md` | `##### `get_all_types`` | 4 | 3594, 5117, 5167, 7109 |
| `docs/reference/services.md` | `##### `get_configuration`` | 4 | 3582, 5105, 5155, 7097 |
| `docs/reference/services.md` | `##### `get_diagnostics`` | 9 | 2212, 3247, 4775, 4857, 5691, 5741, 6368, 6420, 6875 |
| `docs/reference/services.md` | `##### `get_health`` | 6 | 2204, 3239, 4849, 5733, 6412, 6867 |
| `docs/reference/services.md` | `##### `get_history`` | 7 | 681, 1080, 4003, 6241, 7627, 7709, 7781 |
| `docs/reference/services.md` | `##### `get_manager`` | 3 | 5557, 5591, 5791 |
| `docs/reference/services.md` | `##### `get_profile`` | 2 | 2569, 4502 |
| `docs/reference/services.md` | `##### `get_provider`` | 3 | 2230, 3367, 4825 |
| `docs/reference/services.md` | `##### `get_recommendations`` | 8 | 1313, 1835, 3255, 5048, 5303, 5765, 6444, 7016 |
| `docs/reference/services.md` | `##### `get_registry`` | 4 | 5531, 5565, 5599, 5799 |
| `docs/reference/services.md` | `##### `get_session`` | 5 | 667, 1066, 6227, 6575, 6940 |
| `docs/reference/services.md` | `##### `get_statistics`` | 8 | 1669, 2196, 3231, 5757, 6436, 6649, 6804, 6859 |
| `docs/reference/services.md` | `##### `get_stats`` | 2 | 5573, 5607 |
| `docs/reference/services.md` | `##### `get_telemetry`` | 3 | 4841, 5749, 6428 |
| `docs/reference/services.md` | `##### `heartbeat`` | 2 | 4988, 6993 |
| `docs/reference/services.md` | `##### `history`` | 3 | 83, 984, 2517 |
| `docs/reference/services.md` | `##### `initialize` (initialization)` | 11 | 561, 1772, 3439, 4669, 4747, 5439, 5495, 6326, 6384, 6509, 6665 |
| `docs/reference/services.md` | `##### `log_error`` | 3 | 4783, 4865, 6354 |
| `docs/reference/services.md` | `##### `publish_execution_report`` | 2 | 2807, 7324 |
| `docs/reference/services.md` | `##### `publish_generation_report`` | 2 | 1526, 7382 |
| `docs/reference/services.md` | `##### `record`` | 3 | 29, 922, 2455 |
| `docs/reference/services.md` | `##### `register_provider`` | 5 | 1036, 2242, 3353, 4314, 5981 |
| `docs/reference/services.md` | `##### `restore`` | 3 | 70, 969, 2502 |
| `docs/reference/services.md` | `##### `searchmetadata`` | 3 | 104, 1009, 2542 |
| `docs/reference/services.md` | `##### `start_session`` | 2 | 1479, 7129 |
| `docs/reference/services.md` | `##### `start` (runtime)` | 9 | 4675, 4753, 5445, 5501, 6332, 6390, 6515, 6587, 6671 |
| `docs/reference/services.md` | `##### `statistics`` | 3 | 96, 999, 2532 |
| `docs/reference/services.md` | `##### `stop` (cleanup)` | 9 | 4681, 4759, 5451, 5507, 6338, 6396, 6521, 6595, 6677 |
| `docs/reference/services.md` | `##### `store_execution_summary`` | 2 | 2793, 7310 |
| `docs/reference/services.md` | `##### `update`` | 4 | 43, 938, 2471, 4461 |
| `docs/services/SECURITY.md` | `### resolution strategy` | 2 | 12, 37 |
| `docs/services/SECURITY.md` | `### vulnerability context` | 2 | 9, 34 |

---

*Consistency Report: Sprint 7 Milestone 6 · 2026-07-06*
