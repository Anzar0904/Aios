import ast
import os
from typing import Any, Dict, List


class DocumentationIndexer:
    """Parses Python source files using AST to extract detailed metadata."""

    def parse_file(self, filepath: str) -> Dict[str, Any]:
        """Parses a single file and extracts detailed structural metadata."""
        if not os.path.exists(filepath):
            return {}

        with open(filepath, "r", encoding="utf-8") as f:
            try:
                node = ast.parse(f.read(), filename=filepath)
            except SyntaxError as e:
                return {"error": f"Syntax error: {e}"}

        file_metadata = {"classes": [], "functions": [], "imports": []}

        for item in node.body:
            if isinstance(item, ast.ClassDef):
                class_info = self._parse_class(item)
                file_metadata["classes"].append(class_info)
            elif isinstance(item, ast.FunctionDef):
                func_info = self._parse_function(item)
                file_metadata["functions"].append(func_info)
            elif isinstance(item, (ast.Import, ast.ImportFrom)):
                imports_info = self._parse_imports(item)
                file_metadata["imports"].extend(imports_info)

        return file_metadata

    def _parse_class(self, node: ast.ClassDef) -> Dict[str, Any]:
        docstring = ast.get_docstring(node) or ""
        methods = []
        is_dataclass = any(
            (isinstance(d, ast.Name) and d.id == "dataclass")
            or (
                isinstance(d, ast.Call)
                and isinstance(d.func, ast.Name)
                and d.func.id == "dataclass"
            )
            for d in node.decorator_list
        )

        bases = [self._get_source_segment(b) for b in node.bases]
        is_enum = any("Enum" in base for base in bases)

        decorators = [self._get_source_segment(d) for d in node.decorator_list]

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(self._parse_function(item))

        return {
            "name": node.name,
            "docstring": docstring.strip(),
            "methods": methods,
            "bases": bases,
            "decorators": decorators,
            "is_dataclass": is_dataclass,
            "is_enum": is_enum,
            "line_count": len(node.body),
        }

    def _parse_function(self, node: ast.FunctionDef) -> Dict[str, Any]:
        docstring = ast.get_docstring(node) or ""
        args = []
        for arg in node.args.args:
            arg_type = None
            if arg.annotation:
                arg_type = self._get_source_segment(arg.annotation)
            args.append({"name": arg.arg, "type": arg_type})

        return_type = None
        if node.returns:
            return_type = self._get_source_segment(node.returns)

        decorators = [self._get_source_segment(d) for d in node.decorator_list]

        return {
            "name": node.name,
            "docstring": docstring.strip(),
            "arguments": args,
            "return_type": return_type,
            "decorators": decorators,
            "complexity_approx": self._estimate_complexity(node),
        }

    def _parse_imports(self, node: Any) -> List[str]:
        imports = []
        if isinstance(node, ast.Import):
            for name in node.names:
                imports.append(name.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for name in node.names:
                imports.append(f"{module}.{name.name}")
        return imports

    def _get_source_segment(self, node: Any) -> str:
        """Fallback to unparse or name extraction for type annotations/bases."""
        try:
            return ast.unparse(node)
        except AttributeError:
            if isinstance(node, ast.Name):
                return node.id
            return str(node)

    def _estimate_complexity(self, node: ast.FunctionDef) -> int:
        """Estimates cyclomatic complexity based on branch nodes in AST."""
        branches = 0
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler, ast.BoolOp)):
                branches += 1
        return branches + 1
