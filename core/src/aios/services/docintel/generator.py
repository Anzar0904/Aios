import os
from typing import Any, Dict


class MarkdownGenerator:
    """Formats scan indices and dependency graphs into Markdown documents inside /docs."""

    def __init__(self, output_dir: str) -> None:
        self.output_dir = os.path.abspath(output_dir)

    def generate(
        self,
        scan_results: Dict[str, Any],
        index_data: Dict[str, Dict[str, Any]],
        intel_report: Dict[str, Any],
        dep_mermaid: str,
        pkg_mermaid: str,
        svc_mermaid: str,
    ) -> None:
        """Saves target markdown folders and files in the destination directory."""
        # Create all required folders
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "Architecture"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "API"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "Services"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "Providers"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "Reports"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "README"), exist_ok=True)

        # 1. Generate README.md
        self._write_readme(scan_results)

        # 2. Generate Architecture.md
        self._write_architecture(pkg_mermaid, svc_mermaid)

        # 3. Generate Services.md
        self._write_services(scan_results)

        # 4. Generate Providers.md
        self._write_providers(scan_results)

        # 5. Generate API.md
        self._write_api(index_data)

        # 6. Generate DependencyGraph.md
        self._write_dependency_graph(dep_mermaid)

        # 7. Generate Code Intelligence Report
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
            f"- **Configuration Files**: {len(scan_results.get('configuration_files', []))}",
            f"- **Documentation Files**: {len(scan_results.get('documentation', []))}",
            "",
            "## Documentation Pages Map",
            "- [Architecture.md](Architecture.md): Package and service relation diagrams.",
            "- [Services.md](Services.md): Scanned core services list.",
            "- [Providers.md](Providers.md): Active AI integration providers.",
            "- [API.md](API.md): Class, method, and function specifications.",
            "- [DependencyGraph.md](DependencyGraph.md): Comprehensive module imports flowchart.",
            "- [Reports/Code_Completeness_Report.md]"
            "(Reports/Code_Completeness_Report.md): Documentation completeness metrics.",
            "",
        ]
        text = "\n".join(content)
        self._save_file("README.md", text)
        self._save_file("README/README.md", text)

    def _write_architecture(self, pkg_mermaid: str, svc_mermaid: str) -> None:
        content = [
            "# System Architecture Graphs",
            "",
            "## Package Relationships Graph",
            "```mermaid",
            pkg_mermaid,
            "```",
            "",
            "## Core Services Relationships Graph",
            "```mermaid",
            svc_mermaid,
            "```",
            "",
        ]
        text = "\n".join(content)
        self._save_file("Architecture.md", text)
        self._save_file("Architecture/Architecture.md", text)

    def _write_services(self, scan_results: Dict[str, Any]) -> None:
        lines = ["# Core Services Listing", ""]
        for svc in scan_results.get("services", []):
            lines.append(f"- **{svc['name']}** (Path: `file:///{svc['path']}`)")
        text = "\n".join(lines)
        self._save_file("Services.md", text)
        self._save_file("Services/Services.md", text)

    def _write_providers(self, scan_results: Dict[str, Any]) -> None:
        lines = ["# Active Providers Listing", ""]
        for prov in scan_results.get("providers", []):
            lines.append(f"- **{prov['name']}** (Path: `file:///{prov['path']}`)")
        text = "\n".join(lines)
        self._save_file("Providers.md", text)
        self._save_file("Providers/Providers.md", text)

    def _write_api(self, index_data: Dict[str, Dict[str, Any]]) -> None:
        lines = ["# API Documentation Reference", ""]

        for file_path, data in index_data.items():
            if "error" in data or (not data.get("classes") and not data.get("functions")):
                continue

            lines.append(f"## Module: {file_path}")
            lines.append("")

            # Classes
            for cls in data.get("classes", []):
                lines.append(f"### class `{cls['name']}`")
                if cls.get("bases"):
                    lines.append(f"- **Inherits from**: {', '.join(cls['bases'])}")
                if cls.get("decorators"):
                    lines.append(f"- **Decorators**: `{'`, `'.join(cls['decorators'])}`")
                if cls.get("is_dataclass"):
                    lines.append("- **Type**: Dataclass")
                if cls.get("is_enum"):
                    lines.append("- **Type**: Enum")
                lines.append("")
                if cls.get("docstring"):
                    lines.append(f"> {cls['docstring']}")
                    lines.append("")

                if cls.get("methods"):
                    lines.append("**Methods:**")
                    lines.append("")
                    for m in cls["methods"]:
                        arg_str = ", ".join(
                            f"{a['name']}: {a['type']}" if a["type"] else a["name"]
                            for a in m["arguments"]
                        )
                        ret = f" -> {m['return_type']}" if m["return_type"] else ""
                        lines.append(f"- `def {m['name']}({arg_str}){ret}`")
                        if m.get("docstring"):
                            lines.append(f"  * {m['docstring']}")
                    lines.append("")

            # Functions
            for func in data.get("functions", []):
                lines.append(f"### def `{func['name']}`")
                arg_str = ", ".join(
                    f"{a['name']}: {a['type']}" if a["type"] else a["name"]
                    for a in func["arguments"]
                )
                ret = f" -> {func['return_type']}" if func["return_type"] else ""
                lines.append(f"- `def {func['name']}({arg_str}){ret}`")
                if func.get("decorators"):
                    lines.append(f"- **Decorators**: `{'`, `'.join(func['decorators'])}`")
                if func.get("docstring"):
                    lines.append(f"> {func['docstring']}")
                lines.append("")

        text = "\n".join(lines)
        self._save_file("API.md", text)
        self._save_file("API/API.md", text)

    def _write_dependency_graph(self, dep_mermaid: str) -> None:
        content = [
            "# Dependency Flow Graph",
            "",
            "The following flowchart shows dot-module import relationships:",
            "",
            "```mermaid",
            dep_mermaid,
            "```",
            "",
        ]
        text = "\n".join(content)
        self._save_file("DependencyGraph.md", text)

    def _write_reports(self, intel_report: Dict[str, Any]) -> None:
        lines = [
            "# Documentation Intelligence Analysis Report",
            f"**Completeness Score**: {intel_report.get('score', 100)}/100",
            "",
            "## Undocumented Classes",
        ]
        for c in intel_report.get("undocumented_classes", []):
            lines.append(f"- class `{c['class']}` in file `{c['file']}`")

        lines.extend(["", "## Undocumented Functions"])
        for f in intel_report.get("undocumented_functions", []):
            lines.append(f"- def `{f['function']}` in file `{f['file']}`")

        lines.extend(["", "## Inline TODOs and FIXMEs"])
        for todo in intel_report.get("todos_fixmes", []):
            lines.append(
                f"- **{todo['type']}** at line {todo['line']} in "
                f"`{todo['file']}`: *{todo['content']}*"
            )

        self._save_file("Reports/Code_Completeness_Report.md", "\n".join(lines))

    def _save_file(self, subpath: str, content: str) -> None:
        full_path = os.path.join(self.output_dir, subpath)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
