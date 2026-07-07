import json
import os
import time
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional

from aios.services.base import ServiceLifecycle
from aios.services.model import ModelService


class DocumentationAgent(ServiceLifecycle):
    """AI Documentation Agent querying the DocumentationIndex."""

    __test__ = False

    def __init__(
        self,
        model_service: Optional[ModelService] = None,
        index_path: str = "docs/index.json",
    ) -> None:
        self.model_service = model_service
        self.index_path = index_path
        self.index: Dict[str, Any] = {}
        self._is_initialized = False

    def initialize(self) -> None:
        if os.path.exists(self.index_path):
            try:
                with open(self.index_path, "r", encoding="utf-8") as f:
                    self.index = json.load(f)
                self._is_initialized = True
            except Exception:
                self.index = {}
        else:
            self.index = {}

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def _fuzzy_score(self, query: str, target: str) -> float:
        query = query.lower().strip()
        target = target.lower().strip()
        if not query or not target:
            return 0.0
        if query == target:
            return 1.0
        if query in target:
            return 0.8 + (len(query) / len(target)) * 0.19
        return SequenceMatcher(None, query, target).ratio()

    def search_class(self, query: str) -> List[Dict[str, Any]]:
        results = []
        index_data = self.index.get("index_data", {})
        for filepath, data in index_data.items():
            for cls in data.get("classes", []):
                score = self._fuzzy_score(query, cls["name"])
                if score > 0.4:
                    results.append(
                        {
                            "type": "class",
                            "name": cls["name"],
                            "file": filepath,
                            "docstring": cls.get("docstring", ""),
                            "bases": cls.get("bases", []),
                            "decorators": cls.get("decorators", []),
                            "is_dataclass": cls.get("is_dataclass", False),
                            "is_enum": cls.get("is_enum", False),
                            "methods": cls.get("methods", []),
                            "score": score,
                        }
                    )
        return sorted(results, key=lambda x: x["score"], reverse=True)

    def search_function(self, query: str) -> List[Dict[str, Any]]:
        results = []
        index_data = self.index.get("index_data", {})
        for filepath, data in index_data.items():
            for func in data.get("functions", []):
                score = self._fuzzy_score(query, func["name"])
                if score > 0.4:
                    results.append(
                        {
                            "type": "function",
                            "name": func["name"],
                            "file": filepath,
                            "docstring": func.get("docstring", ""),
                            "arguments": func.get("arguments", []),
                            "return_type": func.get("return_type"),
                            "decorators": func.get("decorators", []),
                            "score": score,
                        }
                    )
            for cls in data.get("classes", []):
                for method in cls.get("methods", []):
                    score = self._fuzzy_score(query, method["name"])
                    if score > 0.4:
                        results.append(
                            {
                                "type": "method",
                                "name": f"{cls['name']}.{method['name']}",
                                "class": cls["name"],
                                "file": filepath,
                                "docstring": method.get("docstring", ""),
                                "arguments": method.get("arguments", []),
                                "return_type": method.get("return_type"),
                                "decorators": method.get("decorators", []),
                                "score": score,
                            }
                        )
        return sorted(results, key=lambda x: x["score"], reverse=True)

    def search_service(self, query: str) -> List[Dict[str, Any]]:
        results = []
        scan_results = self.index.get("scan_results", {})
        for svc in scan_results.get("services", []):
            score = self._fuzzy_score(query, svc["name"])
            if score > 0.4:
                results.append(
                    {"type": "service", "name": svc["name"], "file": svc["path"], "score": score}
                )
        return sorted(results, key=lambda x: x["score"], reverse=True)

    def search_module(self, query: str) -> List[Dict[str, Any]]:
        results = []
        scan_results = self.index.get("scan_results", {})
        for mod in scan_results.get("modules", []):
            score = self._fuzzy_score(query, mod)
            if score > 0.4:
                results.append({"type": "module", "name": mod, "score": score})
        return sorted(results, key=lambda x: x["score"], reverse=True)

    def search_file(self, query: str) -> List[Dict[str, Any]]:
        results = []
        index_data = self.index.get("index_data", {})
        for filepath in index_data.keys():
            basename = os.path.basename(filepath)
            score = max(self._fuzzy_score(query, filepath), self._fuzzy_score(query, basename))
            if score > 0.4:
                results.append({"type": "file", "name": filepath, "score": score})
        return sorted(results, key=lambda x: x["score"], reverse=True)

    def search_symbol(self, query: str) -> List[Dict[str, Any]]:
        classes = self.search_class(query)
        funcs = self.search_function(query)
        services = self.search_service(query)
        modules = self.search_module(query)
        files = self.search_file(query)
        all_res = classes + funcs + services + modules + files
        return sorted(all_res, key=lambda x: x["score"], reverse=True)

    def _get_dependencies(self, filepath: str) -> List[str]:
        index_data = self.index.get("index_data", {})
        file_data = index_data.get(filepath, {})
        return file_data.get("imports", [])

    def _get_dependents(self, filepath: str) -> List[str]:
        dependents = []
        dotted_parts = []
        parts = filepath.replace("\\", "/").split("/")
        if "src" in parts:
            idx = parts.index("src")
            dotted_parts = parts[idx + 1 :]
        elif "core" in parts:
            idx = parts.index("core")
            dotted_parts = parts[idx + 1 :]
        else:
            dotted_parts = parts

        if dotted_parts and dotted_parts[-1].endswith(".py"):
            dotted_parts[-1] = dotted_parts[-1][:-3]
        dotted_path = ".".join(dotted_parts)

        index_data = self.index.get("index_data", {})
        for path, data in index_data.items():
            if path == filepath:
                continue
            for imp in data.get("imports", []):
                if imp == dotted_path or imp.startswith(dotted_path + "."):
                    dependents.append(path)
                    break
        return dependents

    def ask(self, query: str) -> str:
        if not self._is_initialized:
            return (
                "Documentation index is not loaded. "
                "Please build documentation using 'aios docs build' first."
            )

        query_lower = query.lower()

        is_undoc_query = (
            "no documentation" in query_lower
            or "lack documentation" in query_lower
            or "undocumented" in query_lower
        )
        if is_undoc_query:
            report = self.index.get("intel_report", {})
            undoc_classes = report.get("undocumented_classes", [])
            undoc_funcs = report.get("undocumented_functions", [])

            res_lines = ["### Undocumented Modules & Symbols Report", ""]
            if undoc_classes:
                res_lines.append("#### Undocumented Classes:")
                for uc in undoc_classes[:15]:
                    res_lines.append(f"- class `{uc['class']}` in `{uc['file']}`")
                if len(undoc_classes) > 15:
                    res_lines.append(f"- ... and {len(undoc_classes) - 15} more classes.")
            else:
                res_lines.append("✓ No undocumented classes found.")

            res_lines.append("")
            if undoc_funcs:
                res_lines.append("#### Undocumented Functions:")
                for uf in undoc_funcs[:15]:
                    res_lines.append(f"- def `{uf['function']}` in `{uf['file']}`")
                if len(undoc_funcs) > 15:
                    res_lines.append(f"- ... and {len(undoc_funcs) - 15} more functions.")
            else:
                res_lines.append("✓ No undocumented functions found.")
            return "\n".join(res_lines)

        if "lack tests" in query_lower or "untested" in query_lower or "no tests" in query_lower:
            index_data = self.index.get("index_data", {})
            scan_results = self.index.get("scan_results", {})
            tests = [t["path"] for t in scan_results.get("tests", [])]

            untested_files = []
            for filepath in index_data.keys():
                if "tests" in filepath or "test_" in filepath:
                    continue
                basename = os.path.basename(filepath)
                test_name = f"test_{basename}"
                has_test = any(test_name in t or basename in t for t in tests)
                if not has_test:
                    untested_files.append(filepath)

            res_lines = ["### Untested Modules & Functions Report", ""]
            if untested_files:
                res_lines.append(
                    "The following files lack dedicated test suites under `core/tests/`:"
                )
                for uf in untested_files[:15]:
                    res_lines.append(f"- `{uf}`")
                if len(untested_files) > 15:
                    res_lines.append(f"- ... and {len(untested_files) - 15} more files.")
            else:
                res_lines.append("✓ All scanned modules have corresponding test suites.")
            return "\n".join(res_lines)

        is_recent_query = (
            "changed recently" in query_lower
            or "recent changes" in query_lower
            or "recently changed" in query_lower
        )
        if is_recent_query:
            index_data = self.index.get("index_data", {})
            file_mtimes = []
            for path in index_data.keys():
                if os.path.exists(path):
                    mtime = os.path.getmtime(path)
                    file_mtimes.append((path, mtime))
            file_mtimes.sort(key=lambda x: x[1], reverse=True)

            res_lines = ["### Recently Changed Files", ""]
            for path, mtime in file_mtimes[:10]:
                time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime))
                res_lines.append(f"- `{path}` (Modified: {time_str})")
            return "\n".join(res_lines)

        if "dependency graph" in query_lower or "dependencies flow" in query_lower:
            dep_mermaid = self.index.get("dep_mermaid", "")
            res_lines = [
                "### Dependency Graph Overview",
                "",
                "The repository follows a clean-architecture pattern with dependencies "
                "flowing inward.",
                "",
                "```mermaid",
                dep_mermaid[:1000] + "\n..." if len(dep_mermaid) > 1000 else dep_mermaid,
                "```",
                "",
                "See `docs/DependencyGraph.md` for the full imports diagram.",
            ]
            return "\n".join(res_lines)

        symbol_query = query
        words_to_strip = [
            "explain class",
            "explain service",
            "explain module",
            "explain",
            "where is",
            "how does",
            "show",
        ]
        for word in words_to_strip:
            if query_lower.startswith(word):
                symbol_query = query[len(word) :].strip()
                break

        matches = self.search_symbol(symbol_query)
        if not matches:
            if self.model_service:
                scan_res = self.index.get("scan_results", {})
                packages = scan_res.get("packages", [])
                prompt = (
                    f"You are the AI OS Documentation Agent. Answer this question "
                    f"about the project: '{query}'.\n"
                    f"The project structure contains these packages: {packages}."
                )
                try:
                    return self.model_service.execute_prompt(prompt)
                except Exception as e:
                    return f"Failed to generate explanation: {e}"
            return f"No matching symbols or files found for '{symbol_query}'."

        best_match = matches[0]
        filepath = best_match.get("file") or best_match.get("name")
        name = best_match.get("name")
        entity_type = best_match.get("type", "symbol")

        docstring = best_match.get("docstring", "")
        if not docstring and entity_type == "file":
            index_data = self.index.get("index_data", {})
            file_data = index_data.get(filepath, {})
            for c in file_data.get("classes", []):
                if c.get("docstring"):
                    docstring = f"Contains class {c['name']}: {c['docstring']}"
                    break

        dependencies = self._get_dependencies(filepath) if filepath else []
        dependents = self._get_dependents(filepath) if filepath else []

        public_apis = []
        related_classes = []
        if filepath:
            index_data = self.index.get("index_data", {})
            file_data = index_data.get(filepath, {})
            for c in file_data.get("classes", []):
                related_classes.append(c["name"])
                for m in c.get("methods", []):
                    if not m["name"].startswith("_"):
                        public_apis.append(f"{c['name']}.{m['name']}")
            for f in file_data.get("functions", []):
                if not f["name"].startswith("_"):
                    public_apis.append(f["name"])

        doc_links = [
            "- [API Reference](docs/API.md)",
            "- [Services Listing](docs/Services.md)",
            "- [Architecture Overview](docs/Architecture.md)",
        ]

        metadata_str = (
            f"**Symbol**: `{name}` ({entity_type})\n"
            f"**File Location**: `{filepath}`\n"
            f"**Summary**: {docstring or '*No docstring provided.*'}\n"
            f"**Dependencies**: {', '.join(dependencies) if dependencies else '*None*'}\n"
            f"**Dependents**: {', '.join(dependents) if dependents else '*None*'}\n"
            f"**Public APIs**: {', '.join(public_apis[:10]) if public_apis else '*None*'}\n"
            f"**Related Classes**: {', '.join(related_classes) if related_classes else '*None*'}\n"
            f"**Documentation Links**:\n" + "\n".join(doc_links)
        )

        if self.model_service:
            prompt = (
                f"You are the AI OS Documentation Agent. Provide a premium, technical, "
                f"yet concise explanation of the following codebase entity: '{name}' "
                f"based on the gathered metadata:\n\n"
                f"{metadata_str}\n\n"
                f"Include its role in the system, its relationship to other modules, "
                f"and how it is used."
            )
            try:
                explanation = self.model_service.execute_prompt(prompt)
                return (
                    f"### Explanation: {name}\n\n{explanation}\n\n"
                    f"---\n\n### Metadata Overview\n\n{metadata_str}"
                )
            except Exception:
                pass

        return f"### Entity Profile: {name}\n\n{metadata_str}"
