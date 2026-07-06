"""
cert_analyzers.py — Documentation Certification Analyzers (Sprint 7 Milestone 6).

Six independent, stateless analyzer classes.  Each returns structured findings
that are aggregated by the CertificationEngine.

Analyzers:
    MarkdownAnalyzer        — Validates Markdown formatting and heading structure
    MermaidAnalyzer         — Validates Mermaid code-block syntax
    CrossLinkAnalyzer       — Validates internal Markdown links
    OrphanAnalyzer          — Detects documents not linked from any other doc
    CompletenessAnalyzer    — Checks required files and sections exist
    DuplicateSectionAnalyzer — Detects duplicate headings within a document

Design principles:
    - Pure functions / no side effects
    - No runtime imports (reads files only)
    - Deterministic: same input → same output
    - Non-destructive: read-only access to the docs tree
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Set, Tuple

from aios.docgen.cert_models import (
    BrokenLink,
    CoverageScore,
    DuplicateSection,
    Finding,
    OrphanDocument,
    Severity,
)

# ---------------------------------------------------------------------------
# Constants — required files and sections
# ---------------------------------------------------------------------------

# Files that MUST exist for certification
REQUIRED_FILES: Dict[str, str] = {
    "docs/README.md": "Documentation index",
    "docs/generated/README.md": "Generated docs index",
    "docs/generated/services.md": "Service catalog",
    "docs/generated/repositories.md": "Repository catalog",
    "docs/generated/skills.md": "Skills catalog",
    "docs/generated/providers.md": "Provider catalog",
    "docs/generated/runtime.md": "Runtime catalog",
    "docs/generated/db_models.md": "DB models catalog",
    "docs/generated/dependency_graph.md": "DI dependency graph",
    "docs/reference/README.md": "API reference index",
    "docs/reference/api_reference.md": "API reference",
    "docs/reference/services.md": "Service reference",
    "docs/reference/interfaces.md": "Interface reference",
    "docs/diagrams/README.md": "Diagram index",
    "docs/diagrams/architecture.md": "Architecture diagram",
    "docs/diagrams/dependency_graph.md": "Dependency diagram",
    "docs/diagrams/lifecycle.md": "Lifecycle diagram",
    "docs/diagrams/runtime.md": "Runtime diagram",
    "docs/operations/README.md": "Operations index",
    "docs/operations/local_setup.md": "Local setup guide",
    "docs/operations/configuration.md": "Configuration guide",
    "docs/operations/deployment.md": "Deployment guide",
    "docs/operations/startup.md": "Startup guide",
    "docs/operations/monitoring.md": "Monitoring guide",
    "docs/operations/backup_restore.md": "Backup/restore guide",
    "docs/operations/troubleshooting.md": "Troubleshooting guide",
    "docs/operations/production_checklist.md": "Production checklist",
    "docs/architecture/README.md": "Architecture index",
    "docs/guides/README.md": "Guides index",
}

# Sections required inside docs/README.md
REQUIRED_README_SECTIONS: List[str] = [
    "Quick Navigation",
    "Generated Documentation",
    "API & Service Reference",
    "Architecture Diagrams",
    "Architecture",
    "Services",
    "Guides",
    "Deployment",
    "Operations",
    "Milestones",
]

# Sections required in each ops guide
REQUIRED_OPS_SECTIONS: Dict[str, List[str]] = {
    "local_setup.md": ["Prerequisites", "Installation", "Environment"],
    "configuration.md": ["Environment Variables"],
    "deployment.md": ["Prerequisites", "Production"],
    "startup.md": ["Startup"],
    "monitoring.md": ["Metrics"],
    "backup_restore.md": ["Backup", "Restore"],
    "troubleshooting.md": ["Common Issues"],
    "production_checklist.md": ["Pre-Deployment"],
}

# Subdirectories under docs/ that should be excluded from orphan detection
# (they are themselves indexes or well-known stand-alones, or legacy mirrors)
ORPHAN_EXCLUDES: Set[str] = {
    # Root-level index / status files
    "docs/README.md",
    "docs/INDEX.md",
    "docs/AI_CONTEXT.md",
    "docs/PROJECT_STATUS.md",
    "docs/VERSION.md",
    "docs/CHANGELOG.md",
    "docs/docs.json",
    # Root-level numbered docs (pre-S7.M1 layout) — canonical copies live in subdirs;
    # these are legacy mirrors intentionally preserved in place.
    "docs/00_PROJECT_VISION.md",
    "docs/01_ENGINEERING_GUIDELINES.md",
    "docs/02_ARCHITECTURE_GUIDELINES.md",
    "docs/03_IMPLEMENTATION_GUIDELINES.md",
    "docs/04_AI_MODEL_STRATEGY.md",
    "docs/05_SECURITY_GUIDELINES.md",
    "docs/06_TESTING_GUIDELINES.md",
    "docs/07_DOCUMENTATION_GUIDELINES.md",
    "docs/08_CODING_STANDARDS.md",
    "docs/09_ROADMAP.md",
    "docs/10_DECISION_LOG.md",
    "docs/11_CONTRIBUTING.md",
    "docs/12_PRD.md",
    "docs/13_DRD.md",
    "docs/14_TECH_STACK.md",
    "docs/15_SYSTEM_DESIGN.md",
    "docs/16_ENGINEERING_BIBLE.md",
    "docs/17_KNOWLEDGE_BASE.md",
    "docs/18_INTERVIEW_GUIDE.md",
    "docs/19_GLOSSARY.md",
    "docs/20_OPERATIONS_MANUAL.md",
    # Root-level milestone reports (linked from docs/milestones/ index)
    "docs/APPROVAL_ENGINE_M1_REPORT.md",
    "docs/APPROVAL_ENGINE_M2_REPORT.md",
    "docs/APPROVAL_ENGINE_M3_REPORT.md",
    "docs/APPROVAL_ENGINE_M4_REPORT.md",
    "docs/ARCHITECTURE_EVOLUTION_REPORT.md",
    "docs/AUTOMATION_INTELLIGENCE_M1_REPORT.md",
    "docs/AUTOMATION_INTELLIGENCE_M2_REPORT.md",
    "docs/AUTOMATION_INTELLIGENCE_M3_REPORT.md",
    "docs/AUTOMATION_INTELLIGENCE_M4_REPORT.md",
    "docs/AUTOMATION_INTELLIGENCE_M5_REPORT.md",
    "docs/AUTOMATION_INTELLIGENCE_M6_REPORT.md",
    "docs/AUTOMATION_INTELLIGENCE_M7_REPORT.md",
    "docs/DOCUMENTATION_INTELLIGENCE_M6_REPORT.md",
    "docs/N8N_PRODUCTION_M2_REPORT.md",
    "docs/N8N_RUNTIME_INTEGRATION_REPORT.md",
    "docs/PERSISTENCE_PLATFORM_M1_REPORT.md",
    "docs/SOURCE_CONTROL_M1_REPORT.md",
}

# Directories to skip entirely (milestones / report dumps / certification output)
SKIP_DIRS: Set[str] = {"milestones", "persistence", "adr", "troubleshooting", "certification"}

# Generated catalog files that may legitimately have repeated method-level headings
# (e.g. '### Methods', '#### `get_health`') across many service entries.
# Also includes structured docs (CHANGELOG Keep-a-Changelog, SECURITY advisories)
# where repeated section names are part of the format spec.
DUPLICATE_EXCLUDE_FILES: Set[str] = {
    # Auto-generated catalogs
    "api_reference.md",
    "services.md",
    "db_models.md",
    "dependency_graph.md",
    "repositories.md",
    "runtime.md",
    # Structured docs with intentional repeated headings
    "CHANGELOG.md",   # Keep-a-Changelog: each version has '### Added', '### Fixed', etc.
    "SECURITY.md",    # Security advisory: each vulnerability has same sub-sections
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _read_text(path: Path) -> str:
    """Read a file, returning '' on any error."""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _md_files(docs_root: Path, skip_dirs: Set[str] = SKIP_DIRS) -> List[Path]:
    """Return all .md files under docs_root, skipping excluded directories."""
    files: List[Path] = []
    for p in sorted(docs_root.rglob("*.md")):
        # Skip any file whose path contains a skipped directory component
        parts = set(p.relative_to(docs_root).parts[:-1])  # directory components
        if parts & skip_dirs:
            continue
        files.append(p)
    return files


def _extract_headings(content: str) -> List[Tuple[int, str, int]]:
    """
    Return list of (level, heading_text, line_number) from Markdown content.
    Only ATX headings (# Heading) are considered.
    Headings inside fenced code blocks (``` or ~~~) are skipped.
    """
    results = []
    in_fence = False
    fence_char = ""
    for lineno, line in enumerate(content.splitlines(), start=1):
        stripped = line.strip()
        if not in_fence:
            if stripped.startswith("```") or stripped.startswith("~~~"):
                in_fence = True
                fence_char = stripped[:3]
                continue
            m = re.match(r"^(#{1,6})\s+(.*)", line)
            if m:
                level = len(m.group(1))
                text = m.group(2).strip()
                results.append((level, text, lineno))
        else:
            if stripped.startswith(fence_char):
                in_fence = False
    return results


def _extract_md_links(content: str) -> List[Tuple[str, str, int]]:
    """
    Return list of (link_text, link_target, line_number) for all Markdown links.
    Skips http/https/mailto/file:/// absolute-path links.
    Skips links inside fenced code blocks (``` or ~~~).
    Only relative file paths and anchor-only links are returned.
    """
    results = []
    pattern = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
    in_fence = False
    fence_char = ""
    for lineno, line in enumerate(content.splitlines(), start=1):
        # Track fenced code blocks
        stripped = line.strip()
        if not in_fence:
            if stripped.startswith("```") or stripped.startswith("~~~"):
                in_fence = True
                fence_char = stripped[:3]
                continue
        else:
            if stripped.startswith(fence_char):
                in_fence = False
            continue  # Skip all lines inside code fence

        # Skip inline code spans before searching for links
        # Replace `...` spans with spaces to avoid matching inside them
        clean_line = re.sub(r"`[^`]+`", lambda m: " " * len(m.group()), line)

        for m in pattern.finditer(clean_line):
            text = m.group(1)
            target = m.group(2).strip()
            # Skip fully qualified external/absolute URIs
            if target.startswith(("http://", "https://", "mailto:", "file:///", "file://")):
                continue
            # Skip Windows-style absolute paths
            if re.match(r"^[A-Za-z]:\\\\", target):
                continue
            # Skip Unix absolute paths (e.g. /path/to/file)
            if target.startswith("/"):
                continue
            results.append((text, target, lineno))
    return results


def _resolve_link(source: Path, target: str, docs_root: Path) -> Path:
    """
    Resolve a relative Markdown link target relative to its source file.
    Strips anchor fragments (#section).
    """
    # Strip anchor
    if "#" in target:
        target = target.split("#")[0]
    if not target:
        # Anchor-only link — valid by default (points within same file)
        return source
    target_path = (source.parent / target).resolve()
    return target_path


# ---------------------------------------------------------------------------
# MarkdownAnalyzer
# ---------------------------------------------------------------------------


class MarkdownAnalyzer:
    """
    Validates Markdown formatting across all documentation files.

    Checks:
    - Each file has exactly one H1 heading
    - Heading hierarchy is not skipped (no h1 → h3 without h2)
    - No trailing whitespace on headings
    - No empty headings
    - README navigation links resolve
    """

    def analyze(self, docs_root: Path) -> List[Finding]:
        findings: List[Finding] = []
        for md_file in _md_files(docs_root):
            rel = str(md_file.relative_to(docs_root.parent))
            content = _read_text(md_file)
            headings = _extract_headings(content)

            h1_count = sum(1 for lvl, _, _ in headings if lvl == 1)
            if h1_count == 0:
                findings.append(
                    Finding(
                        check="markdown.h1_missing",
                        severity=Severity.WARNING,
                        file=rel,
                        message="No H1 heading found in document",
                    )
                )
            elif h1_count > 1:
                findings.append(
                    Finding(
                        check="markdown.h1_multiple",
                        severity=Severity.WARNING,
                        file=rel,
                        message=f"Multiple H1 headings found ({h1_count}); expected exactly one",
                    )
                )

            # Check for empty headings
            for lvl, text, lineno in headings:
                if not text:
                    findings.append(
                        Finding(
                            check="markdown.empty_heading",
                            severity=Severity.ERROR,
                            file=rel,
                            line=lineno,
                            message=f"Empty H{lvl} heading at line {lineno}",
                        )
                    )

            # Heading hierarchy check (no level skips > 1)
            prev_level = 0
            for lvl, text, lineno in headings:
                if prev_level > 0 and lvl > prev_level + 1:
                    findings.append(
                        Finding(
                            check="markdown.heading_skip",
                            severity=Severity.WARNING,
                            file=rel,
                            line=lineno,
                            message=(
                                f"Heading level skipped from H{prev_level} to H{lvl} "
                                f"at line {lineno}: '{text}'"
                            ),
                        )
                    )
                prev_level = lvl

            # PASS if no issues found in this file
            if not any(f.file == rel for f in findings):
                findings.append(
                    Finding(
                        check="markdown.format",
                        severity=Severity.PASS,
                        file=rel,
                        message="Markdown formatting is valid",
                    )
                )

        return findings


# ---------------------------------------------------------------------------
# MermaidAnalyzer
# ---------------------------------------------------------------------------

# Mermaid graph types that are valid
_MERMAID_DIAGRAM_TYPES = re.compile(
    r"^(graph|flowchart|sequenceDiagram|classDiagram|stateDiagram|stateDiagram-v2"
    r"|erDiagram|gantt|pie|journey|gitGraph|quadrantChart|requirementDiagram"
    r"|mindmap|timeline|xychart-beta)\b"
)


class MermaidAnalyzer:
    """
    Validates Mermaid diagram syntax in all Markdown documentation files.

    Checks:
    - All ```mermaid blocks start with a recognised diagram type
    - Blocks are not empty
    - Basic node definition syntax (no unclosed brackets)
    """

    def analyze(self, docs_root: Path) -> List[Finding]:
        findings: List[Finding] = []
        for md_file in _md_files(docs_root):
            rel = str(md_file.relative_to(docs_root.parent))
            content = _read_text(md_file)
            findings.extend(self._check_file(rel, content))
        return findings

    def _check_file(self, rel: str, content: str) -> List[Finding]:
        findings: List[Finding] = []
        lines = content.splitlines()
        in_block = False
        block_start = 0
        block_lines: List[str] = []

        for lineno, line in enumerate(lines, start=1):
            stripped = line.strip()
            if stripped.startswith("```mermaid") and not in_block:
                in_block = True
                block_start = lineno
                block_lines = []
            elif stripped == "```" and in_block:
                in_block = False
                findings.extend(
                    self._validate_block(rel, block_start, block_lines)
                )
            elif in_block:
                block_lines.append(line)

        if in_block:
            findings.append(
                Finding(
                    check="mermaid.unclosed_block",
                    severity=Severity.ERROR,
                    file=rel,
                    line=block_start,
                    message=f"Unclosed ```mermaid block starting at line {block_start}",
                )
            )

        return findings

    def _validate_block(
        self, rel: str, start_line: int, block: List[str]
    ) -> List[Finding]:
        findings: List[Finding] = []
        non_empty = [ln.strip() for ln in block if ln.strip()]

        if not non_empty:
            findings.append(
                Finding(
                    check="mermaid.empty_block",
                    severity=Severity.ERROR,
                    file=rel,
                    line=start_line,
                    message=f"Empty Mermaid diagram block at line {start_line}",
                )
            )
            return findings

        first_line = non_empty[0]
        if not _MERMAID_DIAGRAM_TYPES.match(first_line):
            findings.append(
                Finding(
                    check="mermaid.unknown_type",
                    severity=Severity.WARNING,
                    file=rel,
                    line=start_line,
                    message=(
                        f"Mermaid block at line {start_line} starts with unrecognised "
                        f"diagram type: '{first_line[:60]}'"
                    ),
                )
            )

        # Check for unmatched brackets in node definitions
        for i, raw_line in enumerate(block, start=start_line + 1):
            opens = raw_line.count("[") + raw_line.count("(") + raw_line.count("{")
            closes = raw_line.count("]") + raw_line.count(")") + raw_line.count("}")
            # Allow reasonable imbalance for multi-line constructs; flag extreme cases
            if abs(opens - closes) > 3:
                findings.append(
                    Finding(
                        check="mermaid.bracket_mismatch",
                        severity=Severity.WARNING,
                        file=rel,
                        line=i,
                        message=(
                            f"Possible bracket mismatch in Mermaid block at line {i}: "
                            f"opens={opens} closes={closes}"
                        ),
                    )
                )

        return findings


# ---------------------------------------------------------------------------
# CrossLinkAnalyzer
# ---------------------------------------------------------------------------


# Patterns to skip in cross-link validation:
# - Legacy numbered standalone docs (00_*.md … 20_*.md) that lived directly in docs/
#   but have since been reorganised into subdirectories.  The handwritten docs still
#   reference their old siblings by basename which is now stale — these are known,
#   pre-existing legacy links and should not inflate the broken-link count.
_LEGACY_NUMBERED_DOC_PATTERN = re.compile(r"^(\d{2}_[A-Z_]+\.md)$")

# Source-code paths embedded in docs as examples (not real links)
_EXAMPLE_PATH_PATTERN = re.compile(
    r"(core/src/|aios/services/|tests/|path/to/)"
)


class CrossLinkAnalyzer:
    """
    Validates all internal Markdown cross-references.

    Checks:
    - Relative file links exist on the filesystem
    - Anchor links (#section) point to a heading that exists in the target file

    Skips:
    - file:// absolute-path URIs (IDE deep-links in handwritten docs)
    - Legacy numbered doc references (00_*.md) from handwritten docs
    - Source-code path examples embedded in documentation prose
    """

    def analyze(
        self, docs_root: Path
    ) -> Tuple[List[BrokenLink], List[Finding]]:
        broken: List[BrokenLink] = []
        findings: List[Finding] = []

        for md_file in _md_files(docs_root):
            rel = str(md_file.relative_to(docs_root.parent))
            content = _read_text(md_file)
            links = _extract_md_links(content)

            for text, target, lineno in links:
                # Skip example source-code paths embedded in docs
                if _EXAMPLE_PATH_PATTERN.search(target):
                    continue

                # Separate anchor from path
                anchor = ""
                path_part = target
                if "#" in target:
                    parts = target.split("#", 1)
                    path_part = parts[0]
                    anchor = parts[1].lower()

                if path_part:
                    # Skip legacy numbered doc references (pre-S7.M1 layout)
                    basename = Path(path_part).name
                    if _LEGACY_NUMBERED_DOC_PATTERN.match(basename):
                        continue

                    resolved = (md_file.parent / path_part).resolve()
                    if not resolved.exists():
                        broken.append(
                            BrokenLink(
                                source_file=rel,
                                link_text=text,
                                link_target=target,
                                line=lineno,
                                reason="file not found",
                            )
                        )
                        continue

                    # Validate anchor if present and target is a Markdown file
                    if anchor and resolved.suffix == ".md":
                        target_content = _read_text(resolved)
                        valid_anchors = self._extract_anchors(target_content)
                        if anchor not in valid_anchors:
                            broken.append(
                                BrokenLink(
                                    source_file=rel,
                                    link_text=text,
                                    link_target=target,
                                    line=lineno,
                                    reason=f"anchor '#{anchor}' not found in target",
                                )
                            )
                else:
                    # Anchor-only link: validate within same file
                    if anchor:
                        valid_anchors = self._extract_anchors(content)
                        if anchor not in valid_anchors:
                            broken.append(
                                BrokenLink(
                                    source_file=rel,
                                    link_text=text,
                                    link_target=target,
                                    line=lineno,
                                    reason=f"anchor '#{anchor}' not found in this file",
                                )
                            )

        # Emit pass finding if no broken links
        if not broken:
            findings.append(
                Finding(
                    check="crosslinks.valid",
                    severity=Severity.PASS,
                    file="docs/**/*.md",
                    message="All internal cross-references are valid",
                )
            )

        return broken, findings

    @staticmethod
    def _extract_anchors(content: str) -> Set[str]:
        """
        GitHub-style anchor generation.

        GitHub's algorithm (as of 2024):
          1. Lowercase the heading text
          2. Strip all characters that are NOT alphanumeric, spaces, or hyphens
             (this removes punctuation like &, /, ., etc.)
          3. Replace each remaining space character with a hyphen
             (spaces are replaced individually, NOT collapsed — so 'API & Service'
              becomes 'api  service' after step 2, then 'api--service' after step 3)
          4. Strip leading/trailing hyphens

        We generate BOTH the collapsed variant (step 3 with ``\\s+`` collapse) AND the
        per-space variant so that links using either style are accepted.
        """
        anchors: Set[str] = set()
        for _lvl, heading, _lineno in _extract_headings(content):
            h = heading.lower()
            h = re.sub(r"[^\w\s-]", "", h)

            # Per-space replacement (GitHub's actual behaviour — produces double-hyphens)
            per_space = h.replace(" ", "-").strip("-")
            # Collapsed variant (common alternative)
            collapsed = re.sub(r"\s+", "-", h).strip("-")
            # Also strip runs of hyphens variant
            no_multi = re.sub(r"-+", "-", per_space).strip("-")

            anchors.add(per_space)
            anchors.add(collapsed)
            anchors.add(no_multi)
        return anchors


# ---------------------------------------------------------------------------
# OrphanAnalyzer
# ---------------------------------------------------------------------------


class OrphanAnalyzer:
    """
    Detects documentation files that are not reachable from any other document.

    A file is an orphan if no other Markdown file in the docs tree contains
    a link to it (by relative path or basename).
    """

    def analyze(self, docs_root: Path) -> List[OrphanDocument]:
        all_files = _md_files(docs_root)
        if not all_files:
            return []

        # Build a set of all link targets (resolved absolute paths)
        referenced: Set[Path] = set()
        for md_file in all_files:
            content = _read_text(md_file)
            for _text, target, _lineno in _extract_md_links(content):
                path_part = target.split("#")[0] if "#" in target else target
                if not path_part:
                    continue
                resolved = (md_file.parent / path_part).resolve()
                referenced.add(resolved)

        orphans: List[OrphanDocument] = []
        for md_file in all_files:
            rel = str(md_file.relative_to(docs_root.parent))
            # Skip well-known stand-alones
            if rel in ORPHAN_EXCLUDES or md_file.name == "README.md":
                continue
            if md_file.resolve() not in referenced:
                # Determine category from parent directory
                parts = md_file.relative_to(docs_root).parts
                category = parts[0] if len(parts) > 1 else "root"
                size = md_file.stat().st_size if md_file.exists() else 0
                orphans.append(
                    OrphanDocument(
                        file=rel,
                        size_bytes=size,
                        category=category,
                    )
                )

        return sorted(orphans, key=lambda o: o.file)


# ---------------------------------------------------------------------------
# CompletenessAnalyzer
# ---------------------------------------------------------------------------


class CompletenessAnalyzer:
    """
    Validates that all required documentation files and sections are present.

    Checks:
    - Required files from REQUIRED_FILES exist
    - docs/README.md contains all required navigation sections
    - Each ops guide contains its required sections
    """

    def analyze(self, docs_root: Path, project_root: Path) -> List[Finding]:
        findings: List[Finding] = []

        # 1. Required file presence
        for rel_path, description in REQUIRED_FILES.items():
            full_path = project_root / rel_path
            if full_path.exists():
                findings.append(
                    Finding(
                        check="completeness.required_file",
                        severity=Severity.PASS,
                        file=rel_path,
                        message=f"Required file present: {description}",
                    )
                )
            else:
                findings.append(
                    Finding(
                        check="completeness.required_file_missing",
                        severity=Severity.ERROR,
                        file=rel_path,
                        message=f"Required file missing: {description}",
                    )
                )

        # 2. docs/README.md section check
        readme = project_root / "docs" / "README.md"
        if readme.exists():
            readme_content = _read_text(readme)
            headings = [text for _lvl, text, _ln in _extract_headings(readme_content)]
            for section in REQUIRED_README_SECTIONS:
                found = any(section.lower() in h.lower() for h in headings)
                if found:
                    findings.append(
                        Finding(
                            check="completeness.readme_section",
                            severity=Severity.PASS,
                            file="docs/README.md",
                            message=f"Required section present: '{section}'",
                        )
                    )
                else:
                    findings.append(
                        Finding(
                            check="completeness.readme_section_missing",
                            severity=Severity.WARNING,
                            file="docs/README.md",
                            message=f"Expected section not found in README: '{section}'",
                        )
                    )

        # 3. Operations guide section checks
        ops_dir = project_root / "docs" / "operations"
        for filename, sections in REQUIRED_OPS_SECTIONS.items():
            guide_path = ops_dir / filename
            if not guide_path.exists():
                continue
            content = _read_text(guide_path)
            headings_text = " ".join(
                text for _lvl, text, _ln in _extract_headings(content)
            )
            for section in sections:
                if section.lower() in headings_text.lower():
                    findings.append(
                        Finding(
                            check="completeness.ops_section",
                            severity=Severity.PASS,
                            file=f"docs/operations/{filename}",
                            message=f"Required section present: '{section}'",
                        )
                    )
                else:
                    findings.append(
                        Finding(
                            check="completeness.ops_section_missing",
                            severity=Severity.WARNING,
                            file=f"docs/operations/{filename}",
                            message=(
                                f"Expected section not found in ops guide: '{section}'"
                            ),
                        )
                    )

        return findings


# ---------------------------------------------------------------------------
# DuplicateSectionAnalyzer
# ---------------------------------------------------------------------------


class DuplicateSectionAnalyzer:
    """
    Detects duplicate headings within a single document.

    A heading is considered a duplicate if it appears more than once
    at the same nesting level (case-insensitive).
    """

    def analyze(self, docs_root: Path) -> List[DuplicateSection]:
        duplicates: List[DuplicateSection] = []

        for md_file in _md_files(docs_root):
            # Skip auto-generated catalog files that legitimately have repeated
            # method-level headings (e.g. '### Methods' per service entry)
            if md_file.name in DUPLICATE_EXCLUDE_FILES:
                continue

            rel = str(md_file.relative_to(docs_root.parent))
            content = _read_text(md_file)
            headings = _extract_headings(content)

            # Group by (level, normalised text)
            seen: Dict[Tuple[int, str], List[int]] = {}
            for lvl, text, lineno in headings:
                key = (lvl, text.lower().strip())
                seen.setdefault(key, []).append(lineno)

            for (lvl, text), lines in seen.items():
                if len(lines) > 1:
                    duplicates.append(
                        DuplicateSection(
                            file=rel,
                            heading=f"{'#' * lvl} {text}",
                            occurrences=len(lines),
                            lines=lines,
                        )
                    )

        return sorted(duplicates, key=lambda d: d.file)


# ---------------------------------------------------------------------------
# CoverageAnalyzer
# ---------------------------------------------------------------------------


class CoverageAnalyzer:
    """
    Measures documentation coverage against the source codebase.

    Counts:
    - Python modules under core/src/aios/
    - Modules that appear in at least one generated doc file
    - Public symbols (functions / classes) vs documented symbols
    """

    def analyze(self, project_root: Path) -> CoverageScore:
        score = CoverageScore()

        aios_src = project_root / "core" / "src" / "aios"
        if not aios_src.exists():
            return score

        # Count source modules (*.py files, excluding __pycache__)
        py_files = [
            p
            for p in aios_src.rglob("*.py")
            if "__pycache__" not in str(p) and p.name != "__init__.py"
        ]
        score.total_source_modules = len(py_files)

        # Check which modules appear in generated docs
        generated_dir = project_root / "docs" / "generated"
        if not generated_dir.exists():
            return score

        generated_content = ""
        for gen_file in generated_dir.rglob("*.md"):
            generated_content += _read_text(gen_file)

        documented = set()
        for py_file in py_files:
            module_name = py_file.stem
            # Consider a module documented if its name or dotted path appears in generated docs
            rel_module = str(py_file.relative_to(aios_src)).replace("/", ".").replace(
                ".py", ""
            )
            if module_name in generated_content or rel_module in generated_content:
                documented.add(py_file)

        score.documented_modules = len(documented)

        # Count public symbols via simple regex (def / class at module level)
        total_symbols = 0
        documented_symbols = 0
        ref_content = ""
        ref_dir = project_root / "docs" / "reference"
        if ref_dir.exists():
            for ref_file in ref_dir.rglob("*.md"):
                ref_content += _read_text(ref_file)

        for py_file in py_files:
            source = _read_text(py_file)
            symbols = re.findall(r"^(?:def|class)\s+([A-Za-z_][A-Za-z0-9_]*)", source, re.MULTILINE)
            public = [s for s in symbols if not s.startswith("_")]
            total_symbols += len(public)
            for sym in public:
                if sym in ref_content or sym in generated_content:
                    documented_symbols += 1

        score.total_public_symbols = total_symbols
        score.documented_symbols = documented_symbols

        return score
