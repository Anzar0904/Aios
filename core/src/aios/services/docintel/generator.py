import os
from typing import Any, Dict


class MarkdownGenerator:
    """Formats scan indices and intelligence reports into Markdown documents inside /docs."""

    def __init__(self, output_dir: str) -> None:
        self.output_dir = os.path.abspath(output_dir)

    def generate(
        self, scan_results: Dict[str, Any], intel_report: Dict[str, Any], mermaid_graph: str
    ) -> None:
        """Saves target markdown folders and files in the destination directory."""
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "Architecture"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "API"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "Services"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "Providers"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "Graphs"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "Reports"), exist_ok=True)

        self._write_readme(scan_results)
        self._write_architecture(mermaid_graph)
        self._write_services(scan_results)
        self._write_providers(scan_results)
        self._write_reports(intel_report)

    def _write_readme(self, scan_results: Dict[str, Any]) -> None:
        content = [
            "# AI OS Codebase Index",
            "",
            "Welcome to the automatically generated documentation directory for Personal AI OS.",
            "",
            "## Repository Structure Overview",
            f"- **Packages Detected**: {len(scan_results.get('packages', []))}",
            f"- **Modules Scanned**: {len(scan_results.get('modules', []))}",
            f"- **Core Services**: {len(scan_results.get('services', []))}",
            f"- **Active Providers**: {len(scan_results.get('providers', []))}",
            f"- **Test Suites**: {len(scan_results.get('tests', []))}",
            ""
        ]
        self._save_file("README.md", "\n".join(content))

    def _write_architecture(self, mermaid_graph: str) -> None:
        content = [
            "# System Architecture Graph",
            "",
            "The following flowchart represents automatically extracted module dependencies:",
            "",
            "```mermaid",
            mermaid_graph,
            "```",
            ""
        ]
        self._save_file("Architecture/Architecture.md", "\n".join(content))

    def _write_services(self, scan_results: Dict[str, Any]) -> None:
        lines = ["# Core Services Listing", ""]
        for svc in scan_results.get("services", []):
            lines.append(f"- **{svc['name']}** (Path: `file:///{svc['path']}`)")
        self._save_file("Services/Services.md", "\n".join(lines))

    def _write_providers(self, scan_results: Dict[str, Any]) -> None:
        lines = ["# Active Providers Listing", ""]
        for prov in scan_results.get("providers", []):
            lines.append(f"- **{prov['name']}** (Path: `file:///{prov['path']}`)")
        self._save_file("Providers/Providers.md", "\n".join(lines))

    def _write_reports(self, intel_report: Dict[str, Any]) -> None:
        lines = [
            "# Documentation Intelligence Analysis Report",
            f"**Subsystem Code Quality Score**: {intel_report.get('score', 100)}/100",
            "",
            "## Undocumented Classes",
        ]
        for c in intel_report.get("undocumented_classes", []):
            lines.append(f"- class `{c['class']}` in file `{c['file']}`")

        lines.extend(["", "## Undocumented Functions"])
        for f in intel_report.get("undocumented_functions", []):
            lines.append(f"- def `{f['function']}` in file `{f['file']}`")

        lines.extend(["", "## Complex Methods (Approximated Complexity > 8)"])
        for m in intel_report.get("high_complexity_methods", []):
            lines.append(
                f"- `{m['class']}.{m['method']}` "
                f"(Complexity: `{m['complexity']}`) in `{m['file']}`"
            )

        lines.extend(["", "## Inline TODOs and FIXMEs"])
        for todo in intel_report.get("todos_fixmes", []):
            lines.append(
                f"- **{todo['type']}** at line {todo['line']} in "
                f"`{todo['file']}`: *{todo['content']}*"
            )

        self._save_file("Reports/Code_Intelligence_Report.md", "\n".join(lines))

    def _save_file(self, subpath: str, content: str) -> None:
        full_path = os.path.join(self.output_dir, subpath)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
