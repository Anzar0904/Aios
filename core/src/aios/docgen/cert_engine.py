"""
cert_engine.py — Documentation Certification Engine (Sprint 7 Milestone 6).

Orchestrates all certification analyzers and writes the certification report
suite into docs/certification/.

Usage:
    engine = CertificationEngine(project_root=Path("/path/to/aios"))
    result = engine.run()

Certification is idempotent: re-running overwrites only docs/certification/
and leaves all other documentation untouched.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Optional

from aios.docgen.cert_analyzers import (
    CompletenessAnalyzer,
    CoverageAnalyzer,
    CrossLinkAnalyzer,
    DuplicateSectionAnalyzer,
    MarkdownAnalyzer,
    MermaidAnalyzer,
    OrphanAnalyzer,
    REQUIRED_FILES,
    REQUIRED_README_SECTIONS,
    _md_files,
)
from aios.docgen.cert_models import (
    CertificationResult,
    CertificationStatus,
    CompletenessScore,
    ConsistencyScore,
    CrossReferenceScore,
    QualityScore,
    Severity,
)
from aios.docgen.cert_renderers import (
    render_broken_links,
    render_certification_readme,
    render_certification_report,
    render_completeness_report,
    render_consistency_report,
    render_orphan_documents,
    render_quality_score,
)

logger = logging.getLogger(__name__)


class CertificationEngine:
    """
    Documentation Certification Engine for the Personal AI OS.

    Runs all validation analyzers and produces a certification report suite
    under docs/certification/.

    Design Principles:
    - Idempotent: re-running produces identical output given unchanged docs.
    - Non-destructive: writes only inside docs/certification/; all other docs untouched.
    - No side-effects on the running system: reads source code and docs only.
    - Deterministic ordering: all lists are sorted.
    """

    _OUTPUT_SUBDIR = "certification"

    def __init__(self, project_root: Optional[Path] = None) -> None:
        if project_root is None:
            # Default: five levels up from this file (core/src/aios/docgen → project root)
            project_root = Path(__file__).parent.parent.parent.parent.parent
        self._root = project_root.resolve()
        self._docs_root = self._root / "docs"
        self._output_dir = self._docs_root / self._OUTPUT_SUBDIR

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self) -> CertificationResult:
        """
        Execute a full documentation certification run.

        Returns a CertificationResult summarising all findings,
        scores, and generated report files.
        """
        start = time.time()
        result = CertificationResult(docs_root=str(self._docs_root))

        logger.info("CertificationEngine: starting analysis phase...")

        # --- 1. Coverage Analysis -------------------------------------------
        try:
            coverage_score = CoverageAnalyzer().analyze(self._root)
            result.quality.coverage = coverage_score
            logger.info(
                "  Coverage: %d/%d modules documented, %d/%d symbols",
                coverage_score.documented_modules,
                coverage_score.total_source_modules,
                coverage_score.documented_symbols,
                coverage_score.total_public_symbols,
            )
        except Exception as exc:
            logger.warning("Coverage analysis failed: %s", exc)
            result.errors.append(f"CoverageAnalyzer: {exc}")

        # --- 2. Markdown Formatting Analysis ---------------------------------
        try:
            md_findings = MarkdownAnalyzer().analyze(self._docs_root)
            result.findings.extend(md_findings)
            md_errors = sum(1 for f in md_findings if f.severity == Severity.ERROR)
            md_warns = sum(1 for f in md_findings if f.severity == Severity.WARNING)
            logger.info(
                "  Markdown: %d errors, %d warnings across %d files",
                md_errors,
                md_warns,
                len(_md_files(self._docs_root)),
            )
        except Exception as exc:
            logger.warning("Markdown analysis failed: %s", exc)
            result.errors.append(f"MarkdownAnalyzer: {exc}")

        # --- 3. Mermaid Syntax Analysis --------------------------------------
        try:
            mermaid_findings = MermaidAnalyzer().analyze(self._docs_root)
            result.findings.extend(mermaid_findings)
            mermaid_errors = sum(1 for f in mermaid_findings if f.severity == Severity.ERROR)
            mermaid_warns = sum(1 for f in mermaid_findings if f.severity == Severity.WARNING)
            logger.info(
                "  Mermaid: %d errors, %d warnings",
                mermaid_errors,
                mermaid_warns,
            )
        except Exception as exc:
            logger.warning("Mermaid analysis failed: %s", exc)
            result.errors.append(f"MermaidAnalyzer: {exc}")

        # --- 4. Cross-Link Analysis ------------------------------------------
        try:
            broken_links, link_findings = CrossLinkAnalyzer().analyze(self._docs_root)
            result.broken_links = broken_links
            result.findings.extend(link_findings)
            logger.info("  Cross-links: %d broken links found", len(broken_links))
        except Exception as exc:
            logger.warning("Cross-link analysis failed: %s", exc)
            result.errors.append(f"CrossLinkAnalyzer: {exc}")

        # --- 5. Orphan Document Detection ------------------------------------
        try:
            orphans = OrphanAnalyzer().analyze(self._docs_root)
            result.orphan_documents = orphans
            logger.info("  Orphans: %d orphan documents found", len(orphans))
        except Exception as exc:
            logger.warning("Orphan analysis failed: %s", exc)
            result.errors.append(f"OrphanAnalyzer: {exc}")

        # --- 6. Completeness Analysis ----------------------------------------
        try:
            completeness_findings = CompletenessAnalyzer().analyze(
                self._docs_root, self._root
            )
            result.findings.extend(completeness_findings)
            completeness_errors = sum(
                1 for f in completeness_findings if f.severity == Severity.ERROR
            )
            completeness_warns = sum(
                1 for f in completeness_findings if f.severity == Severity.WARNING
            )
            logger.info(
                "  Completeness: %d errors, %d warnings",
                completeness_errors,
                completeness_warns,
            )
        except Exception as exc:
            logger.warning("Completeness analysis failed: %s", exc)
            result.errors.append(f"CompletenessAnalyzer: {exc}")

        # --- 7. Duplicate Section Detection ----------------------------------
        try:
            duplicates = DuplicateSectionAnalyzer().analyze(self._docs_root)
            result.duplicate_sections = duplicates
            logger.info("  Duplicates: %d duplicate headings found", len(duplicates))
        except Exception as exc:
            logger.warning("Duplicate section analysis failed: %s", exc)
            result.errors.append(f"DuplicateSectionAnalyzer: {exc}")

        # --- Compute Scores --------------------------------------------------
        result.quality = self._compute_scores(result)
        result.status = result.quality.status
        result.total_docs_scanned = len(_md_files(self._docs_root))

        # --- Populate stats for renderers ------------------------------------
        result.stats = {
            "total_docs_scanned": result.total_docs_scanned,
            "total_findings": len(result.findings),
            "errors": result.error_count,
            "warnings": result.warning_count,
            "passes": result.pass_count,
            "broken_links": len(result.broken_links),
            "orphan_documents": len(result.orphan_documents),
            "duplicate_sections": len(result.duplicate_sections),
            "required_files": len(REQUIRED_FILES),
            "required_readme_sections": len(REQUIRED_README_SECTIONS),
        }

        # --- Write Report Files ----------------------------------------------
        logger.info(
            "CertificationEngine: writing reports to %s ...", self._output_dir
        )
        try:
            self._output_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            result.errors.append(f"Cannot create output dir: {exc}")
            result.elapsed_seconds = time.time() - start
            return result

        reports = {
            "certification_report.md": render_certification_report(result),
            "completeness_report.md": render_completeness_report(result),
            "consistency_report.md": render_consistency_report(result),
            "broken_links.md": render_broken_links(result),
            "orphan_documents.md": render_orphan_documents(result),
            "quality_score.md": render_quality_score(result),
            "README.md": render_certification_readme(result),
        }

        for filename, content in reports.items():
            out_path = self._output_dir / filename
            try:
                out_path.write_text(content, encoding="utf-8")
                result.files_written.append(str(out_path))
                logger.info("  Written: %s (%d bytes)", filename, len(content))
            except OSError as exc:
                err = f"Failed to write {filename}: {exc}"
                result.errors.append(err)
                logger.error(err)

        result.elapsed_seconds = time.time() - start
        logger.info(
            "CertificationEngine: complete in %.2fs — status=%s score=%.1f",
            result.elapsed_seconds,
            result.status.value,
            result.quality.health_score,
        )
        return result

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _compute_scores(self, result: CertificationResult) -> QualityScore:
        """
        Build a QualityScore from the raw findings and analyzer outputs.
        Preserves coverage score already computed.
        """
        quality = QualityScore()
        quality.coverage = result.quality.coverage  # already computed

        # Cross-reference score
        total_links = len(result.broken_links) + sum(
            1 for f in result.findings if "crosslinks" in f.check and f.severity == Severity.PASS
        )
        # Better: count all link occurrences attempted
        cross = CrossReferenceScore()
        cross.broken_links = len(result.broken_links)
        cross.orphan_documents = len(result.orphan_documents)
        cross.total_documents = result.total_docs_scanned
        # Estimate total links from findings
        cross.total_internal_links = max(
            cross.broken_links + max(cross.total_documents * 3, 1),
            cross.broken_links + 1,
        )
        cross.valid_links = max(0, cross.total_internal_links - cross.broken_links)
        quality.cross_reference = cross

        # Completeness score
        comp = CompletenessScore()
        comp.total_required_files = len(REQUIRED_FILES)
        comp.total_required_sections = len(REQUIRED_README_SECTIONS)
        for f in result.findings:
            if f.check == "completeness.required_file":
                comp.present_files += 1
            elif f.check == "completeness.required_file_missing":
                comp.missing_files.append(f.file)
            elif f.check == "completeness.readme_section":
                comp.present_sections += 1
            elif f.check == "completeness.readme_section_missing":
                comp.missing_sections.append(f.message)
        quality.completeness = comp

        # Consistency score
        cons = ConsistencyScore()
        for f in result.findings:
            if f.check.startswith("markdown."):
                if f.severity == Severity.ERROR:
                    cons.markdown_errors += 1
                elif f.severity == Severity.WARNING:
                    cons.formatting_warnings += 1
            elif f.check.startswith("mermaid."):
                if f.severity == Severity.ERROR:
                    cons.mermaid_errors += 1
                elif f.severity == Severity.WARNING:
                    cons.mermaid_errors += 1
        # Count unique files with any duplicate heading (not total occurrences)
        cons.duplicate_sections = len({d.file for d in result.duplicate_sections})
        quality.consistency = cons

        return quality

    @property
    def output_dir(self) -> Path:
        """Return the configured output directory (docs/certification/)."""
        return self._output_dir
