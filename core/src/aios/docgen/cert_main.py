"""
cert_main.py — Documentation Certification CLI (Sprint 7 Milestone 6).

Run with:
    python -m aios.docgen.cert_main [--project-root /path/to/aios] [--verbose]

Generates docs/certification/ with:
    README.md
    certification_report.md
    completeness_report.md
    consistency_report.md
    broken_links.md
    orphan_documents.md
    quality_score.md
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path


def main() -> int:
    """CLI entry point for documentation certification."""
    parser = argparse.ArgumentParser(
        prog="python -m aios.docgen.cert_main",
        description="AIOS Documentation Certification Generator (Sprint 7 M6)",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Path to the AIOS project root (default: auto-detect from cwd)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )

    try:
        from aios.docgen.cert_engine import CertificationEngine

        project_root = args.project_root or Path.cwd()
        engine = CertificationEngine(project_root=project_root)
        result = engine.run()

        # Print summary
        print()
        print("=" * 62)
        print("AIOS Documentation Certification — Sprint 7 Milestone 6")
        print("=" * 62)
        print(f"Status:          {result.status.value.upper()}")
        print(
            f"Health Score:    {result.quality.health_score:.1f}/100  (Grade: {result.quality.grade})"
        )
        print(f"Elapsed:         {result.elapsed_seconds:.2f}s")
        print(f"Output:          {engine.output_dir}")
        print()
        print("Score Breakdown:")
        print(f"  Coverage:      {result.quality.coverage.score:.1f}%")
        print(f"  Cross-Refs:    {result.quality.cross_reference.score:.1f}%")
        print(f"  Completeness:  {result.quality.completeness.score:.1f}%")
        print(f"  Consistency:   {result.quality.consistency.score:.1f}%")
        print()
        print("Findings:")
        print(f"  Documents Scanned:  {result.total_docs_scanned}")
        print(f"  Errors:             {result.error_count}")
        print(f"  Warnings:           {result.warning_count}")
        print(f"  Passes:             {result.pass_count}")
        print(f"  Broken Links:       {len(result.broken_links)}")
        print(f"  Orphan Documents:   {len(result.orphan_documents)}")
        print(f"  Duplicate Sections: {len(result.duplicate_sections)}")
        print()
        print(f"Files Written ({len(result.files_written)}):")
        project_root_resolved = project_root.resolve()
        for fp in sorted(result.files_written):
            p = Path(fp)
            size = p.stat().st_size if p.exists() else 0
            try:
                rel = p.relative_to(project_root_resolved)
            except ValueError:
                rel = p
            print(f"  [{size:8} B]  {rel}")

        if result.errors:
            print(f"\nErrors ({len(result.errors)}):")
            for e in result.errors:
                print(f"  ✗  {e}")

        print("=" * 62)
        print()

        return 0 if result.status.value in ("certified", "conditional") else 1

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        if "--verbose" in sys.argv or "-v" in sys.argv:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
