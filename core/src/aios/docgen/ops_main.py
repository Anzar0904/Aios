"""
Operations Guide Generator CLI — python -m aios.docgen.ops_main

Generates deployment and operations guides into docs/operations/.
"""

import sys
from pathlib import Path

from aios.docgen.ops_engine import OperationsGeneratorEngine


def main() -> int:
    """CLI entry point for operations guide generator."""
    try:
        project_root = Path.cwd()
        engine = OperationsGeneratorEngine(project_root=project_root)
        result = engine.run()

        # Print summary
        print("=" * 60)
        print("AIOS Operations Guide Generator — Sprint 7 Milestone 5")
        print("=" * 60)
        print(f"Status:       {result.status.upper()}")
        print(f"Elapsed:      {result.elapsed:.2f}s")
        print(f"Output:       {project_root / 'docs' / 'operations'}")
        print()
        print(f"Guides Generated: {result.guides_generated}")
        print()
        print(f"Files Generated ({len(result.files_written)}):")
        for file_path in sorted(result.files_written):
            path = Path(file_path)
            size = path.stat().st_size if path.exists() else 0
            rel_path = path.relative_to(project_root)
            print(f"  [{size:8} B]  {rel_path}")
        print("=" * 60)

        if result.errors:
            print("\nErrors:")
            for error in result.errors:
                print(f"  - {error}")
            return 1

        return 0

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
