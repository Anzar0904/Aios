"""
cert_models.py — Data models for Documentation Certification (Sprint 7 Milestone 6).

All domain objects used by the certification analyzers and renderers.
No runtime imports; purely structural data models.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class Severity(str, Enum):
    """Severity level of a certification finding."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    PASS = "pass"


class CertificationStatus(str, Enum):
    """Overall certification outcome."""

    CERTIFIED = "certified"
    CONDITIONAL = "conditional"
    FAILED = "failed"


# ---------------------------------------------------------------------------
# Finding models
# ---------------------------------------------------------------------------


@dataclass
class Finding:
    """A single validation finding (error, warning, or pass)."""

    check: str  # name of the check
    severity: Severity  # error / warning / info / pass
    file: str  # relative path of the affected doc
    message: str  # human-readable description
    line: Optional[int] = None  # line number if applicable
    detail: Optional[str] = None  # extra context


@dataclass
class BrokenLink:
    """A broken internal or cross-reference link."""

    source_file: str
    link_text: str
    link_target: str
    line: Optional[int] = None
    reason: str = "target not found"


@dataclass
class OrphanDocument:
    """A document that is not referenced from any other document."""

    file: str
    size_bytes: int
    category: str  # generated / reference / architecture / etc.


@dataclass
class DuplicateSection:
    """A heading that appears more than once within a single document."""

    file: str
    heading: str
    occurrences: int
    lines: List[int] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Score models
# ---------------------------------------------------------------------------


@dataclass
class CoverageScore:
    """Documentation Coverage metrics."""

    total_source_modules: int = 0
    documented_modules: int = 0
    total_public_symbols: int = 0
    documented_symbols: int = 0

    @property
    def module_coverage(self) -> float:
        if self.total_source_modules == 0:
            return 100.0
        return round(self.documented_modules / self.total_source_modules * 100, 1)

    @property
    def symbol_coverage(self) -> float:
        if self.total_public_symbols == 0:
            return 100.0
        return round(self.documented_symbols / self.total_public_symbols * 100, 1)

    @property
    def score(self) -> float:
        return round((self.module_coverage + self.symbol_coverage) / 2, 1)


@dataclass
class CrossReferenceScore:
    """Cross-reference Coverage metrics."""

    total_internal_links: int = 0
    valid_links: int = 0
    broken_links: int = 0
    orphan_documents: int = 0
    total_documents: int = 0

    @property
    def link_validity_rate(self) -> float:
        if self.total_internal_links == 0:
            return 100.0
        return round(self.valid_links / self.total_internal_links * 100, 1)

    @property
    def orphan_rate(self) -> float:
        if self.total_documents == 0:
            return 0.0
        return round(self.orphan_documents / self.total_documents * 100, 1)

    @property
    def score(self) -> float:
        link_score = self.link_validity_rate
        orphan_score = max(0.0, 100.0 - self.orphan_rate * 2)
        return round((link_score + orphan_score) / 2, 1)


@dataclass
class CompletenessScore:
    """Documentation Completeness metrics."""

    total_required_sections: int = 0
    present_sections: int = 0
    missing_sections: List[str] = field(default_factory=list)
    total_required_files: int = 0
    present_files: int = 0
    missing_files: List[str] = field(default_factory=list)

    @property
    def section_completeness(self) -> float:
        if self.total_required_sections == 0:
            return 100.0
        return round(self.present_sections / self.total_required_sections * 100, 1)

    @property
    def file_completeness(self) -> float:
        if self.total_required_files == 0:
            return 100.0
        return round(self.present_files / self.total_required_files * 100, 1)

    @property
    def score(self) -> float:
        return round((self.section_completeness + self.file_completeness) / 2, 1)


@dataclass
class ConsistencyScore:
    """Documentation Consistency metrics."""

    total_headings_checked: int = 0
    consistent_headings: int = 0
    markdown_errors: int = 0
    mermaid_errors: int = 0
    duplicate_sections: int = 0
    formatting_warnings: int = 0

    @property
    def heading_consistency_rate(self) -> float:
        if self.total_headings_checked == 0:
            return 100.0
        return round(self.consistent_headings / self.total_headings_checked * 100, 1)

    @property
    def score(self) -> float:
        """
        Consistency score (0–100).

        Uses capped proportional deductions so that structural duplicates in
        large auto-generated catalogs (e.g. repeated 'Parameters' headings in
        api_reference.md) do not bottom out the score.

        Deductions:
          - Each markdown_error:      up to 5 pts (capped at 25 pts total)
          - Each mermaid_error:       up to 5 pts (capped at 25 pts total)
          - Each formatting_warning:  up to 1 pt  (capped at 15 pts total)
          - Duplicate sections:       up to 5 pts per unique file (capped at 20 pts)
        """
        md_penalty = min(self.markdown_errors * 5, 25)
        mermaid_penalty = min(self.mermaid_errors * 5, 25)
        warn_penalty = min(self.formatting_warnings * 1, 15)
        # duplicate_sections stores count of unique affected files
        dup_penalty = min(self.duplicate_sections * 5, 20)
        total_penalty = md_penalty + mermaid_penalty + warn_penalty + dup_penalty
        return round(max(0.0, 100.0 - total_penalty), 1)


@dataclass
class QualityScore:
    """Overall documentation quality score."""

    coverage: CoverageScore = field(default_factory=CoverageScore)
    cross_reference: CrossReferenceScore = field(default_factory=CrossReferenceScore)
    completeness: CompletenessScore = field(default_factory=CompletenessScore)
    consistency: ConsistencyScore = field(default_factory=ConsistencyScore)

    # Weights (must sum to 1.0)
    WEIGHT_COVERAGE: float = 0.25
    WEIGHT_CROSS_REF: float = 0.20
    WEIGHT_COMPLETENESS: float = 0.30
    WEIGHT_CONSISTENCY: float = 0.25

    @property
    def health_score(self) -> float:
        """Weighted composite documentation health score (0–100)."""
        raw = (
            self.coverage.score * self.WEIGHT_COVERAGE
            + self.cross_reference.score * self.WEIGHT_CROSS_REF
            + self.completeness.score * self.WEIGHT_COMPLETENESS
            + self.consistency.score * self.WEIGHT_CONSISTENCY
        )
        return round(raw, 1)

    @property
    def grade(self) -> str:
        s = self.health_score
        if s >= 95:
            return "A+"
        elif s >= 90:
            return "A"
        elif s >= 85:
            return "B+"
        elif s >= 80:
            return "B"
        elif s >= 70:
            return "C"
        elif s >= 60:
            return "D"
        else:
            return "F"

    @property
    def status(self) -> CertificationStatus:
        s = self.health_score
        if s >= 80:
            return CertificationStatus.CERTIFIED
        elif s >= 60:
            return CertificationStatus.CONDITIONAL
        else:
            return CertificationStatus.FAILED


# ---------------------------------------------------------------------------
# Certification result
# ---------------------------------------------------------------------------


@dataclass
class CertificationResult:
    """Complete result of a documentation certification run."""

    status: CertificationStatus = CertificationStatus.FAILED
    quality: QualityScore = field(default_factory=QualityScore)

    # Findings by category
    findings: List[Finding] = field(default_factory=list)
    broken_links: List[BrokenLink] = field(default_factory=list)
    orphan_documents: List[OrphanDocument] = field(default_factory=list)
    duplicate_sections: List[DuplicateSection] = field(default_factory=list)

    # Run metadata
    elapsed_seconds: float = 0.0
    generated_at: float = field(default_factory=time.time)
    docs_root: str = ""
    total_docs_scanned: int = 0
    files_written: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    # Statistics snapshot (serialised summary for reports)
    stats: Dict[str, int] = field(default_factory=dict)

    @property
    def error_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.ERROR)

    @property
    def warning_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.WARNING)

    @property
    def pass_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.PASS)
