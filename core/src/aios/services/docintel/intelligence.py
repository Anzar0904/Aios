import re
from typing import Any, Dict


class DocumentationIntelligenceEngine:
    """Analyzes AST summaries to identify complexity issues and technical debt."""

    def analyze(self, index_data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        report = {
            "undocumented_classes": [],
            "undocumented_functions": [],
            "high_complexity_methods": [],
            "large_classes": [],
            "todos_fixmes": [],
            "score": 100
        }

        for file_path, data in index_data.items():
            if "error" in data:
                continue

            for cls in data.get("classes", []):
                # Check undocumented class
                if not cls.get("docstring"):
                    report["undocumented_classes"].append({
                        "file": file_path,
                        "class": cls["name"]
                    })
                    report["score"] = max(0, report["score"] - 2)

                # Check large class
                if cls.get("line_count", 0) > 200:
                    report["large_classes"].append({
                        "file": file_path,
                        "class": cls["name"],
                        "lines": cls["line_count"]
                    })
                    report["score"] = max(0, report["score"] - 3)

                for method in cls.get("methods", []):
                    # Check complex method
                    if method.get("complexity_approx", 1) > 8:
                        report["high_complexity_methods"].append({
                            "file": file_path,
                            "class": cls["name"],
                            "method": method["name"],
                            "complexity": method["complexity_approx"]
                        })
                        report["score"] = max(0, report["score"] - 2)

            for func in data.get("functions", []):
                # Check undocumented function
                if not func.get("docstring"):
                    report["undocumented_functions"].append({
                        "file": file_path,
                        "function": func["name"]
                    })
                    report["score"] = max(0, report["score"] - 1)

            # Detect TODOs/FIXMEs in comments or file contents
            self._scan_todos_fixmes(file_path, report)

        return report

    def _scan_todos_fixmes(self, file_path: str, report: Dict[str, Any]) -> None:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line_idx, line in enumerate(f, 1):
                    match = re.search(r"#\s*(TODO|FIXME|XXX)\b(.*)", line, re.IGNORECASE)
                    if match:
                        report["todos_fixmes"].append({
                            "file": file_path,
                            "line": line_idx,
                            "type": match.group(1).upper(),
                            "content": match.group(2).strip()
                        })
                        report["score"] = max(0, report["score"] - 1)
        except Exception:
            pass

