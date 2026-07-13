"""
cert_renderers.py — Markdown Renderers for Documentation Certification (Sprint 7 M6).

Each render_* function takes a CertificationResult and returns a complete
Markdown string ready to write to docs/certification/.

All renderers are pure functions: same input → same output (deterministic).
"""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aios.docgen.cert_models import CertificationResult

from aios.docgen.cert_models import CertificationStatus, Severity

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def _ts(epoch: float) -> str:
    return datetime.datetime.utcfromtimestamp(epoch).strftime(_TIMESTAMP_FORMAT)


def _status_badge(status: CertificationStatus) -> str:
    badges = {
        CertificationStatus.CERTIFIED: "✅ CERTIFIED",
        CertificationStatus.CONDITIONAL: "⚠️  CONDITIONAL",
        CertificationStatus.FAILED: "❌ FAILED",
    }
    return badges.get(status, "❓ UNKNOWN")


def _score_bar(score: float, width: int = 20) -> str:
    """Render a text progress bar for a 0–100 score."""
    filled = int(score / 100 * width)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {score:.1f}%"


def _grade_emoji(grade: str) -> str:
    return {
        "A+": "🏆",
        "A": "🥇",
        "B+": "🥈",
        "B": "🥉",
        "C": "📊",
        "D": "⚠️",
        "F": "❌",
    }.get(grade, "❓")


def _sev_icon(severity: Severity) -> str:
    return {
        Severity.ERROR: "❌",
        Severity.WARNING: "⚠️",
        Severity.INFO: "ℹ️",
        Severity.PASS: "✅",
    }.get(severity, "❓")


# ---------------------------------------------------------------------------
# README
# ---------------------------------------------------------------------------


def render_certification_readme(result: "CertificationResult") -> str:
    ts = _ts(result.generated_at)
    score = result.quality.health_score
    grade = result.quality.grade
    status = _status_badge(result.status)

    lines = [
        "# Documentation Certification Suite",
        "",
        "> **Sprint 7 Milestone 6 — Documentation Certification**  ",
        f"> *Generated: {ts} · Score: {score}/100 · Grade: {grade} {_grade_emoji(grade)}*",
        "",
        f"**Overall Status:** {status}",
        "",
        "---",
        "",
        "## 📊 Score Summary",
        "",
        "| Dimension | Score | Weight |",
        "|-----------|-------|--------|",
        f"| Documentation Coverage | {result.quality.coverage.score:.1f}% | 25% |",
        f"| Cross-reference Coverage | {result.quality.cross_reference.score:.1f}% | 20% |",
        f"| Completeness | {result.quality.completeness.score:.1f}% | 30% |",
        f"| Consistency | {result.quality.consistency.score:.1f}% | 25% |",
        f"| **Health Score** | **{score:.1f}%** | — |",
        "",
        "---",
        "",
        "## 📋 Report Index",
        "",
        "| Report | Description |",
        "|--------|-------------|",
        "| [certification_report.md](certification_report.md) | Full certification findings and validation results |",
        "| [completeness_report.md](completeness_report.md) | Required files and section presence |",
        "| [consistency_report.md](consistency_report.md) | Markdown formatting and Mermaid syntax |",
        "| [broken_links.md](broken_links.md) | All broken internal cross-references |",
        "| [orphan_documents.md](orphan_documents.md) | Unreferenced documentation files |",
        "| [quality_score.md](quality_score.md) | Detailed quality scoring and grade |",
        "",
        "---",
        "",
        "## 🔍 Quick Statistics",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Documents Scanned | {result.total_docs_scanned} |",
        f"| Total Findings | {len(result.findings)} |",
        f"| Errors | {result.error_count} |",
        f"| Warnings | {result.warning_count} |",
        f"| Passes | {result.pass_count} |",
        f"| Broken Links | {len(result.broken_links)} |",
        f"| Orphan Documents | {len(result.orphan_documents)} |",
        f"| Duplicate Sections | {len(result.duplicate_sections)} |",
        "",
        "---",
        "",
        "## ⚙️ Regeneration",
        "",
        "```bash",
        "python -m aios.docgen.cert_main",
        "```",
        "",
        "---",
        "",
        f"*Documentation Certification: Sprint 7 Milestone 6 · Personal AI OS · {ts[:10]}*",
    ]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Certification Report
# ---------------------------------------------------------------------------


def render_certification_report(result: "CertificationResult") -> str:
    ts = _ts(result.generated_at)
    score = result.quality.health_score
    grade = result.quality.grade
    status = _status_badge(result.status)

    lines = [
        "# Documentation Certification Report",
        "",
        "> **Sprint 7 Milestone 6 — Documentation Certification**  ",
        f"> *Generated: {ts} · Elapsed: {result.elapsed_seconds:.2f}s*",
        "",
        "---",
        "",
        "## 1. Certification Verdict",
        "",
        "| Attribute | Value |",
        "|-----------|-------|",
        f"| Status | {status} |",
        f"| Health Score | {score}/100 |",
        f"| Grade | {grade} {_grade_emoji(grade)} |",
        f"| Documents Scanned | {result.total_docs_scanned} |",
        f"| Generated At | {ts} |",
        "",
        "---",
        "",
        "## 2. Score Breakdown",
        "",
        "```",
        f"Coverage      {_score_bar(result.quality.coverage.score)}",
        f"Cross-Refs    {_score_bar(result.quality.cross_reference.score)}",
        f"Completeness  {_score_bar(result.quality.completeness.score)}",
        f"Consistency   {_score_bar(result.quality.consistency.score)}",
        "─────────────────────────────────────",
        f"Health Score  {_score_bar(score)}",
        "```",
        "",
        "---",
        "",
        "## 3. Validation Summary",
        "",
        "| Check Category | Errors | Warnings | Passes |",
        "|----------------|--------|----------|--------|",
    ]

    # Group findings by check prefix
    categories: dict = {}
    for f in result.findings:
        cat = f.check.split(".")[0]
        categories.setdefault(cat, {"errors": 0, "warnings": 0, "passes": 0})
        if f.severity == Severity.ERROR:
            categories[cat]["errors"] += 1
        elif f.severity == Severity.WARNING:
            categories[cat]["warnings"] += 1
        elif f.severity == Severity.PASS:
            categories[cat]["passes"] += 1

    for cat, counts in sorted(categories.items()):
        lines.append(
            f"| {cat.title()} | {counts['errors']} | {counts['warnings']} | {counts['passes']} |"
        )

    lines += [
        "",
        f"**Totals:** {result.error_count} errors · {result.warning_count} warnings · {result.pass_count} passes",
        "",
        "---",
        "",
        "## 4. All Findings",
        "",
        "### 4.1 Errors",
        "",
    ]

    errors = [f for f in result.findings if f.severity == Severity.ERROR]
    if errors:
        lines += [
            "| File | Check | Message |",
            "|------|-------|---------|",
        ]
        for f in sorted(errors, key=lambda x: (x.file, x.check)):
            line_ref = f" (L{f.line})" if f.line else ""
            lines.append(f"| `{f.file}{line_ref}` | `{f.check}` | {f.message} |")
    else:
        lines.append("*No errors found.* ✅")

    lines += [
        "",
        "### 4.2 Warnings",
        "",
    ]

    warnings = [f for f in result.findings if f.severity == Severity.WARNING]
    if warnings:
        lines += [
            "| File | Check | Message |",
            "|------|-------|---------|",
        ]
        for f in sorted(warnings, key=lambda x: (x.file, x.check)):
            line_ref = f" (L{f.line})" if f.line else ""
            lines.append(f"| `{f.file}{line_ref}` | `{f.check}` | {f.message} |")
    else:
        lines.append("*No warnings found.* ✅")

    lines += [
        "",
        "---",
        "",
        "## 5. Structural Findings",
        "",
        "| Category | Count |",
        "|----------|-------|",
        f"| Broken Links | {len(result.broken_links)} |",
        f"| Orphan Documents | {len(result.orphan_documents)} |",
        f"| Duplicate Sections | {len(result.duplicate_sections)} |",
        "",
        "See [broken_links.md](broken_links.md), [orphan_documents.md](orphan_documents.md) for details.",
        "",
        "---",
        "",
        "## 6. Certification Criteria",
        "",
        "| Criterion | Threshold | Status |",
        "|-----------|-----------|--------|",
        f"| Health Score ≥ 80 | 80/100 | {'✅ Met' if score >= 80 else '❌ Not Met'} |",
        f"| Zero critical errors | 0 | {'✅ Met' if result.error_count == 0 else f'❌ {result.error_count} errors'} |",
        f"| Broken links ≤ 5 | ≤ 5 | {'✅ Met' if len(result.broken_links) <= 5 else f'⚠️ {len(result.broken_links)} broken'} |",
        f"| Orphan docs ≤ 10% | ≤ 10% | {'✅ Met' if result.quality.cross_reference.orphan_rate <= 10 else '⚠️ Exceeded'} |",
        "",
        "---",
        "",
        f"*Certification Report: Sprint 7 Milestone 6 · Personal AI OS · {ts[:10]}*",
    ]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Completeness Report
# ---------------------------------------------------------------------------


def render_completeness_report(result: "CertificationResult") -> str:
    ts = _ts(result.generated_at)
    comp = result.quality.completeness

    lines = [
        "# Documentation Completeness Report",
        "",
        f"> *Generated: {ts}*",
        "",
        "---",
        "",
        "## Summary",
        "",
        "| Dimension | Present | Required | Score |",
        "|-----------|---------|----------|-------|",
        f"| Required Files | {comp.present_files} | {comp.total_required_files} | {comp.file_completeness:.1f}% |",
        f"| README Sections | {comp.present_sections} | {comp.total_required_sections} | {comp.section_completeness:.1f}% |",
        f"| **Completeness Score** | | | **{comp.score:.1f}%** |",
        "",
        "---",
        "",
        "## Required Files",
        "",
    ]

    # Required file results
    file_findings = [f for f in result.findings if f.check.startswith("completeness.required_file")]
    missing_files = [f for f in file_findings if f.severity == Severity.ERROR]
    present_files = [f for f in file_findings if f.severity == Severity.PASS]

    if present_files:
        lines += [
            "### ✅ Present",
            "",
            "| File | Description |",
            "|------|-------------|",
        ]
        for f in sorted(present_files, key=lambda x: x.file):
            lines.append(f"| `{f.file}` | {f.message.replace('Required file present: ', '')} |")
        lines.append("")

    if missing_files:
        lines += [
            "### ❌ Missing",
            "",
            "| File | Description |",
            "|------|-------------|",
        ]
        for f in sorted(missing_files, key=lambda x: x.file):
            lines.append(f"| `{f.file}` | {f.message.replace('Required file missing: ', '')} |")
        lines.append("")

    lines += [
        "---",
        "",
        "## README Navigation Sections",
        "",
    ]

    # README section results
    section_findings = [
        f for f in result.findings if f.check.startswith("completeness.readme_section")
    ]
    [f for f in section_findings if f.severity == Severity.PASS]
    [f for f in section_findings if f.severity == Severity.WARNING]

    lines += [
        "| Section | Status |",
        "|---------|--------|",
    ]
    for f in sorted(section_findings, key=lambda x: x.message):
        icon = "✅" if f.severity == Severity.PASS else "⚠️"
        section_name = (
            f.message.replace("Required section present: ", "")
            .replace("Expected section not found in README: ", "")
            .strip("'")
        )
        lines.append(f"| {section_name} | {icon} |")

    lines += [
        "",
        "---",
        "",
        "## Operations Guide Completeness",
        "",
    ]

    # Ops guide section results
    ops_findings = [f for f in result.findings if f.check.startswith("completeness.ops_section")]
    ops_by_file: dict = {}
    for f in ops_findings:
        ops_by_file.setdefault(f.file, []).append(f)

    for filepath, findings in sorted(ops_by_file.items()):
        filename = filepath.split("/")[-1]
        lines.append(f"### {filename}")
        lines.append("")
        lines += ["| Section | Status |", "|---------|--------|"]
        for f in sorted(findings, key=lambda x: x.message):
            icon = "✅" if f.severity == Severity.PASS else "⚠️"
            section = (
                f.message.replace("Required section present: ", "")
                .replace("Expected section not found in ops guide: ", "")
                .strip("'")
            )
            lines.append(f"| {section} | {icon} |")
        lines.append("")

    if comp.missing_files:
        lines += [
            "---",
            "",
            "## Missing Files Summary",
            "",
        ]
        for mf in sorted(comp.missing_files):
            lines.append(f"- `{mf}`")
        lines.append("")

    lines += [
        "---",
        "",
        f"*Completeness Report: Sprint 7 Milestone 6 · {ts[:10]}*",
    ]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Consistency Report
# ---------------------------------------------------------------------------


def render_consistency_report(result: "CertificationResult") -> str:
    ts = _ts(result.generated_at)
    cons = result.quality.consistency

    lines = [
        "# Documentation Consistency Report",
        "",
        f"> *Generated: {ts}*",
        "",
        "---",
        "",
        "## Summary",
        "",
        "| Check | Count |",
        "|-------|-------|",
        f"| Markdown Errors | {cons.markdown_errors} |",
        f"| Mermaid Errors | {cons.mermaid_errors} |",
        f"| Formatting Warnings | {cons.formatting_warnings} |",
        f"| Duplicate Sections | {cons.duplicate_sections} |",
        f"| **Consistency Score** | **{cons.score:.1f}%** |",
        "",
        "---",
        "",
        "## Markdown Formatting",
        "",
    ]

    md_findings = [f for f in result.findings if f.check.startswith("markdown.")]
    md_errors = [f for f in md_findings if f.severity == Severity.ERROR]
    md_warns = [f for f in md_findings if f.severity == Severity.WARNING]
    md_passes = [f for f in md_findings if f.severity == Severity.PASS]

    lines.append(
        f"**{len(md_errors)} errors · {len(md_warns)} warnings · {len(md_passes)} passes**"
    )
    lines.append("")

    if md_errors:
        lines += [
            "### Errors",
            "",
            "| File | Line | Check | Message |",
            "|------|------|-------|---------|",
        ]
        for f in sorted(md_errors, key=lambda x: (x.file, x.line or 0)):
            lines.append(f"| `{f.file}` | {f.line or '—'} | `{f.check}` | {f.message} |")
        lines.append("")

    if md_warns:
        lines += [
            "### Warnings",
            "",
            "| File | Line | Check | Message |",
            "|------|------|-------|---------|",
        ]
        for f in sorted(md_warns, key=lambda x: (x.file, x.line or 0)):
            lines.append(f"| `{f.file}` | {f.line or '—'} | `{f.check}` | {f.message} |")
        lines.append("")

    lines += [
        "---",
        "",
        "## Mermaid Syntax",
        "",
    ]

    mermaid_findings = [f for f in result.findings if f.check.startswith("mermaid.")]
    mermaid_errors = [f for f in mermaid_findings if f.severity == Severity.ERROR]
    mermaid_warns = [f for f in mermaid_findings if f.severity == Severity.WARNING]

    lines.append(f"**{len(mermaid_errors)} errors · {len(mermaid_warns)} warnings**")
    lines.append("")

    if mermaid_errors or mermaid_warns:
        lines += [
            "| File | Line | Check | Message |",
            "|------|------|-------|---------|",
        ]
        for f in sorted(mermaid_findings, key=lambda x: (x.file, x.line or 0)):
            if f.severity in (Severity.ERROR, Severity.WARNING):
                lines.append(f"| `{f.file}` | {f.line or '—'} | `{f.check}` | {f.message} |")
        lines.append("")
    else:
        lines += ["*All Mermaid blocks are syntactically valid.* ✅", ""]

    lines += [
        "---",
        "",
        "## Duplicate Sections",
        "",
    ]

    if result.duplicate_sections:
        lines += [
            "| File | Heading | Occurrences | Lines |",
            "|------|---------|-------------|-------|",
        ]
        for dup in sorted(result.duplicate_sections, key=lambda d: (d.file, d.heading)):
            lines_str = ", ".join(str(ln) for ln in dup.lines)
            lines.append(f"| `{dup.file}` | `{dup.heading}` | {dup.occurrences} | {lines_str} |")
        lines.append("")
    else:
        lines += ["*No duplicate sections detected.* ✅", ""]

    lines += [
        "---",
        "",
        f"*Consistency Report: Sprint 7 Milestone 6 · {ts[:10]}*",
    ]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Broken Links
# ---------------------------------------------------------------------------


def render_broken_links(result: "CertificationResult") -> str:
    ts = _ts(result.generated_at)
    broken = result.broken_links

    lines = [
        "# Broken Links Report",
        "",
        f"> *Generated: {ts}*",
        "",
        "---",
        "",
        f"**Total broken links found: {len(broken)}**",
        "",
    ]

    if not broken:
        lines += [
            "✅ No broken internal links found. All cross-references are valid.",
            "",
        ]
    else:
        lines += [
            "| Source File | Link Text | Target | Line | Reason |",
            "|-------------|-----------|--------|------|--------|",
        ]
        for link in sorted(broken, key=lambda l: (l.source_file, l.line or 0)):
            line_ref = str(link.line) if link.line else "—"
            lines.append(
                f"| `{link.source_file}` | {link.link_text or '—'} "
                f"| `{link.link_target}` | {line_ref} | {link.reason} |"
            )
        lines.append("")

    # Group by source file
    if broken:
        by_file: dict = {}
        for link in broken:
            by_file.setdefault(link.source_file, []).append(link)

        lines += [
            "---",
            "",
            "## Grouped by Source File",
            "",
        ]
        for source_file in sorted(by_file):
            file_links = by_file[source_file]
            lines.append(f"### `{source_file}` ({len(file_links)} broken)")
            lines.append("")
            for lnk in sorted(file_links, key=lambda l: l.line or 0):
                line_ref = f"L{lnk.line}" if lnk.line else "?"
                lines.append(f"- **{line_ref}** `{lnk.link_target}` — {lnk.reason}")
            lines.append("")

    lines += [
        "---",
        "",
        "## How to Fix",
        "",
        "1. Verify the target file exists at the specified relative path",
        "2. Check if the file was renamed or moved during generation",
        "3. Update the link target to the correct path",
        "4. For anchor links: ensure the heading text matches exactly (case-insensitive)",
        "",
        "---",
        "",
        f"*Broken Links Report: Sprint 7 Milestone 6 · {ts[:10]}*",
    ]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Orphan Documents
# ---------------------------------------------------------------------------


def render_orphan_documents(result: "CertificationResult") -> str:
    ts = _ts(result.generated_at)
    orphans = result.orphan_documents

    lines = [
        "# Orphan Documents Report",
        "",
        f"> *Generated: {ts}*",
        "",
        "---",
        "",
        f"**Total orphan documents found: {len(orphans)}**",
        "",
    ]

    if not orphans:
        lines += [
            "✅ No orphan documents found. All documents are reachable from at least one other document.",
            "",
        ]
    else:
        lines += [
            "| File | Category | Size |",
            "|------|----------|------|",
        ]
        for orphan in sorted(orphans, key=lambda o: o.file):
            size_kb = orphan.size_bytes / 1024
            lines.append(f"| `{orphan.file}` | {orphan.category} | {size_kb:.1f} KB |")
        lines.append("")

        # Group by category
        by_category: dict = {}
        for orphan in orphans:
            by_category.setdefault(orphan.category, []).append(orphan)

        lines += [
            "---",
            "",
            "## Grouped by Category",
            "",
        ]
        for category in sorted(by_category):
            cat_orphans = by_category[category]
            lines.append(f"### {category.title()} ({len(cat_orphans)} documents)")
            lines.append("")
            for orphan in sorted(cat_orphans, key=lambda o: o.file):
                size_kb = orphan.size_bytes / 1024
                lines.append(f"- `{orphan.file}` ({size_kb:.1f} KB)")
            lines.append("")

    lines += [
        "---",
        "",
        "## How to Fix",
        "",
        "Orphan documents are not reachable from any other documentation file.",
        "To resolve:",
        "",
        "1. Add a link to the document from an appropriate index (e.g., section README)",
        "2. Add it to `docs/README.md` navigation table",
        "3. If the document is intentionally standalone, add it to the exclusion list in `cert_analyzers.py`",
        "",
        "> **Note:** Auto-generated files (milestones, persistence reports) are excluded from orphan detection.",
        "",
        "---",
        "",
        f"*Orphan Documents Report: Sprint 7 Milestone 6 · {ts[:10]}*",
    ]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Quality Score
# ---------------------------------------------------------------------------


def render_quality_score(result: "CertificationResult") -> str:
    ts = _ts(result.generated_at)
    q = result.quality
    score = q.health_score
    grade = q.grade
    status = _status_badge(result.status)

    lines = [
        "# Documentation Quality Score",
        "",
        f"> *Generated: {ts}*",
        "",
        "---",
        "",
        "## Overall Health Score",
        "",
        "```",
        "  ┌─────────────────────────────────────────────────┐",
        "  │  Documentation Health Score                     │",
        "  │                                                 │",
        f"  │    Score:  {score:>5.1f} / 100                        │",
        f"  │    Grade:  {grade:<5} {_grade_emoji(grade)}                            │",
        f"  │    Status: {result.status.value.upper():<15}              │",
        "  └─────────────────────────────────────────────────┘",
        "```",
        "",
        f"**{status}**",
        "",
        "---",
        "",
        "## Score Breakdown",
        "",
        "```",
        f"Documentation Coverage   {_score_bar(q.coverage.score, 25)}  (Weight: 25%)",
        f"Cross-reference Coverage {_score_bar(q.cross_reference.score, 25)}  (Weight: 20%)",
        f"Completeness             {_score_bar(q.completeness.score, 25)}  (Weight: 30%)",
        f"Consistency              {_score_bar(q.consistency.score, 25)}  (Weight: 25%)",
        "─────────────────────────────────────────────────────────────",
        f"Health Score             {_score_bar(score, 25)}",
        "```",
        "",
        "---",
        "",
        "## Dimension Details",
        "",
        "### 📚 Documentation Coverage (25%)",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Source Modules | {q.coverage.total_source_modules} |",
        f"| Documented Modules | {q.coverage.documented_modules} |",
        f"| Module Coverage | {q.coverage.module_coverage:.1f}% |",
        f"| Public Symbols | {q.coverage.total_public_symbols} |",
        f"| Documented Symbols | {q.coverage.documented_symbols} |",
        f"| Symbol Coverage | {q.coverage.symbol_coverage:.1f}% |",
        f"| **Coverage Score** | **{q.coverage.score:.1f}%** |",
        "",
        "### 🔗 Cross-reference Coverage (20%)",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total Internal Links | {q.cross_reference.total_internal_links} |",
        f"| Valid Links | {q.cross_reference.valid_links} |",
        f"| Broken Links | {q.cross_reference.broken_links} |",
        f"| Link Validity Rate | {q.cross_reference.link_validity_rate:.1f}% |",
        f"| Orphan Documents | {q.cross_reference.orphan_documents} |",
        f"| Orphan Rate | {q.cross_reference.orphan_rate:.1f}% |",
        f"| **Cross-Reference Score** | **{q.cross_reference.score:.1f}%** |",
        "",
        "### ✅ Completeness (30%)",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Required Files | {q.completeness.total_required_files} |",
        f"| Present Files | {q.completeness.present_files} |",
        f"| File Completeness | {q.completeness.file_completeness:.1f}% |",
        f"| Required README Sections | {q.completeness.total_required_sections} |",
        f"| Present Sections | {q.completeness.present_sections} |",
        f"| Section Completeness | {q.completeness.section_completeness:.1f}% |",
        f"| **Completeness Score** | **{q.completeness.score:.1f}%** |",
        "",
        "### 🎨 Consistency (25%)",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Markdown Errors | {q.consistency.markdown_errors} |",
        f"| Mermaid Errors | {q.consistency.mermaid_errors} |",
        f"| Formatting Warnings | {q.consistency.formatting_warnings} |",
        f"| Duplicate Sections | {q.consistency.duplicate_sections} |",
        f"| **Consistency Score** | **{q.consistency.score:.1f}%** |",
        "",
        "---",
        "",
        "## Grading Scale",
        "",
        "| Grade | Score Range | Status |",
        "|-------|-------------|--------|",
        "| A+ | 95–100 | 🏆 Certified |",
        "| A  | 90–94  | 🥇 Certified |",
        "| B+ | 85–89  | 🥈 Certified |",
        "| B  | 80–84  | 🥉 Certified |",
        "| C  | 70–79  | ⚠️ Conditional |",
        "| D  | 60–69  | ⚠️ Conditional |",
        "| F  | 0–59   | ❌ Failed |",
        "",
        "---",
        "",
        f"*Quality Score: Sprint 7 Milestone 6 · Personal AI OS · {ts[:10]}*",
    ]
    return "\n".join(lines) + "\n"
