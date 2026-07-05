"""
aios/docgen/__main__.py — CLI entry point.

Run with:
    python -m aios.docgen [--project-root /path/to/aios] [--verbose]
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="python -m aios.docgen",
        description="AIOS Documentation Generator (Sprint 7 M2)",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Path to the AIOS project root (default: auto-detect)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable debug logging"
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )

    from aios.docgen.engine import DocGeneratorEngine

    engine = DocGeneratorEngine(project_root=args.project_root)
    result = engine.run()

    # Print summary
    print(f"\n{'='*60}")
    print("AIOS Documentation Generator — Sprint 7 Milestone 2")
    print(f"{'='*60}")
    print(f"Status:       {result.status.value.upper()}")
    print(f"Elapsed:      {result.elapsed_seconds:.2f}s")
    print(f"Output:       {engine.output_dir}")
    print()
    print("Discovery Summary:")
    print(f"  Services:          {result.services_count}")
    print(f"  Repositories:      {result.repositories_count}")
    print(f"  Skills:            {result.skills_count}")
    print(f"  Providers:         {result.providers_count}")
    print(f"  Runtime Comps:     {result.runtime_count}")
    print(f"  DB Models:         {result.db_models_count}")
    print(f"  DI Bindings:       {result.di_bindings_count}")
    print()
    print(f"Files Generated ({result.total_files}):")
    for f in result.files:
        print(f"  [{f.size_bytes:>8} B]  {f.path}")

    if result.warnings:
        print(f"\nWarnings ({len(result.warnings)}):")
        for w in result.warnings:
            print(f"  ⚠  {w}")

    if result.errors:
        print(f"\nErrors ({len(result.errors)}):")
        for e in result.errors:
            print(f"  ✗  {e}")

    print(f"{'='*60}\n")

    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())
