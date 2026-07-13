"""
refgen_discoverers.py — Enhanced discoverers for API reference generation.

Extracts detailed method signatures, parameters, return types, exceptions,
and lifecycle information from service classes.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import List, Optional

from aios.docgen.discoverers import (
    _base_names,
    _get_docstring,
    _module_name,
    _parse_module,
    _python_files,
)
from aios.docgen.refgen_models import (
    LifecycleMethod,
    MethodSignature,
    ParameterInfo,
    ServiceInterface,
)

# Lifecycle method names to track
LIFECYCLE_METHODS = {
    "init_service": "initialization",
    "cleanup": "cleanup",
    "start": "runtime",
    "stop": "cleanup",
    "initialize": "initialization",
    "shutdown": "cleanup",
    "__init__": "initialization",
}


def _extract_type_annotation(node: Optional[ast.expr]) -> Optional[str]:
    """Convert an AST type annotation to a string representation."""
    if node is None:
        return None

    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Constant):
        return str(node.value)
    elif isinstance(node, ast.Attribute):
        # Handle qualified names like typing.Optional
        parts = []
        current = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return ".".join(reversed(parts))
    elif isinstance(node, ast.Subscript):
        # Handle generic types like List[str], Optional[int]
        base = _extract_type_annotation(node.value)
        if isinstance(node.slice, ast.Tuple):
            args = ", ".join(_extract_type_annotation(e) or "Any" for e in node.slice.elts)
        else:
            args = _extract_type_annotation(node.slice) or "Any"
        return f"{base}[{args}]" if base else None
    elif isinstance(node, ast.Tuple):
        # Handle union types in older Python
        types = [_extract_type_annotation(e) for e in node.elts]
        return f"({', '.join(t for t in types if t)})"
    elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        # Handle Union types with | operator
        left = _extract_type_annotation(node.left)
        right = _extract_type_annotation(node.right)
        return f"{left} | {right}" if left and right else None

    return "Any"


def _extract_default_value(node: Optional[ast.expr]) -> Optional[str]:
    """Extract the default value from a parameter node."""
    if node is None:
        return None

    if isinstance(node, ast.Constant):
        val = node.value
        if isinstance(val, str):
            return f'"{val}"'
        return str(val)
    elif isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Attribute):
        parts = []
        current = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return ".".join(reversed(parts))
    elif isinstance(node, ast.List):
        return "[]"
    elif isinstance(node, ast.Dict):
        return "{}"
    elif isinstance(node, ast.Tuple):
        return "()"
    elif isinstance(node, ast.Call):
        func = _extract_type_annotation(node.func)
        return f"{func}()" if func else None

    return "..."


def _extract_parameters(func_node: ast.FunctionDef | ast.AsyncFunctionDef) -> List[ParameterInfo]:
    """Extract parameter information from a function node."""
    params = []
    args = func_node.args

    # Regular arguments
    defaults_offset = len(args.args) - len(args.defaults)
    for i, arg in enumerate(args.args):
        if arg.arg == "self" or arg.arg == "cls":
            continue

        default_idx = i - defaults_offset
        default = args.defaults[default_idx] if default_idx >= 0 else None

        param = ParameterInfo(
            name=arg.arg,
            type_annotation=_extract_type_annotation(arg.annotation),
            default_value=_extract_default_value(default),
            is_required=default is None,
        )
        params.append(param)

    # *args
    if args.vararg:
        params.append(ParameterInfo(
            name=f"*{args.vararg.arg}",
            type_annotation=_extract_type_annotation(args.vararg.annotation),
            is_required=False,
        ))

    # **kwargs
    if args.kwarg:
        params.append(ParameterInfo(
            name=f"**{args.kwarg.arg}",
            type_annotation=_extract_type_annotation(args.kwarg.annotation),
            is_required=False,
        ))

    return params


def _extract_exceptions(func_node: ast.FunctionDef | ast.AsyncFunctionDef) -> List[str]:
    """Extract exception types raised by a function."""
    exceptions = set()

    # Check docstring for raises/throws documentation
    docstring = _get_docstring(func_node)
    if docstring:
        # Match patterns like "Raises ValueError", "Throws RuntimeError"
        raises_pattern = r"(?:Raises|Throws):\s*(\w+)"
        for match in re.finditer(raises_pattern, docstring):
            exceptions.add(match.group(1))

    # Check for raise statements in the function body
    for node in ast.walk(func_node):
        if isinstance(node, ast.Raise) and node.exc:
            if isinstance(node.exc, ast.Call):
                exc_type = _extract_type_annotation(node.exc.func)
                if exc_type:
                    exceptions.add(exc_type)
            elif isinstance(node.exc, ast.Name):
                exceptions.add(node.exc.id)

    return sorted(exceptions)


def _extract_method_signature(
    func_node: ast.FunctionDef | ast.AsyncFunctionDef
) -> MethodSignature:
    """Extract detailed method signature from a function node."""
    params = _extract_parameters(func_node)
    return_type = _extract_type_annotation(func_node.returns)
    exceptions = _extract_exceptions(func_node)

    # Check for decorators
    is_property = any(
        isinstance(d, ast.Name) and d.id == "property"
        for d in func_node.decorator_list
    )
    is_classmethod = any(
        isinstance(d, ast.Name) and d.id == "classmethod"
        for d in func_node.decorator_list
    )
    is_staticmethod = any(
        isinstance(d, ast.Name) and d.id == "staticmethod"
        for d in func_node.decorator_list
    )

    return MethodSignature(
        name=func_node.name,
        parameters=params,
        return_type=return_type,
        docstring=_get_docstring(func_node),
        exceptions=exceptions,
        is_async=isinstance(func_node, ast.AsyncFunctionDef),
        is_property=is_property,
        is_classmethod=is_classmethod,
        is_staticmethod=is_staticmethod,
        line_number=func_node.lineno,
    )


class ServiceReferenceDiscoverer:
    """
    Enhanced service discoverer that extracts detailed API information
    including method signatures, parameters, return types, and exceptions.
    """

    _SERVICE_SUFFIXES = ("Service", "Engine", "Resolver", "Registry", "Manager")

    def __init__(self, services_root: Path, src_root: Path) -> None:
        self._services_root = services_root
        self._src_root = src_root

    def discover(self) -> List[ServiceInterface]:
        """Discover services with detailed API information."""
        interfaces: dict[str, ServiceInterface] = {}

        for py_file in _python_files(self._services_root):
            if py_file.name.startswith("__"):
                continue

            module = _parse_module(py_file)
            if module is None:
                continue

            module_name = _module_name(py_file, self._src_root)
            is_impl = "_impl" in py_file.stem

            for node in ast.walk(module):
                if not isinstance(node, ast.ClassDef):
                    continue

                bases = _base_names(node)
                if not any("ServiceLifecycle" in b or "DIInitializeMixin" in b for b in bases):
                    continue

                name = node.name
                if not any(name.endswith(sfx) for sfx in self._SERVICE_SUFFIXES):
                    continue

                # Extract all methods
                methods = []
                lifecycle_methods = []
                constructor_params = []

                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if item.name.startswith("_") and item.name not in LIFECYCLE_METHODS:
                            continue

                        sig = _extract_method_signature(item)

                        # Check if it's a lifecycle method
                        if item.name in LIFECYCLE_METHODS:
                            lifecycle_method = LifecycleMethod(
                                name=item.name,
                                phase=LIFECYCLE_METHODS[item.name],
                                signature=sig,
                                dependencies=[],
                            )
                            lifecycle_methods.append(lifecycle_method)

                            # Extract constructor dependencies
                            if item.name == "__init__":
                                constructor_params = sig.parameters
                        else:
                            methods.append(sig)

                # Create or update interface entry
                if is_impl:
                    iface_name = self._guess_interface(name)
                    if iface_name and iface_name in interfaces:
                        interfaces[iface_name].implementation = name
                        interfaces[iface_name].impl_module = module_name
                    else:
                        # Standalone implementation
                        interface = ServiceInterface(
                            name=name,
                            module=module_name,
                            file_path=str(py_file),
                            docstring=_get_docstring(node),
                            base_classes=bases,
                            methods=methods,
                            lifecycle_methods=lifecycle_methods,
                            constructor_params=constructor_params,
                            line_number=node.lineno,
                        )
                        interfaces[name] = interface
                else:
                    if name not in interfaces:
                        interface = ServiceInterface(
                            name=name,
                            module=module_name,
                            file_path=str(py_file),
                            docstring=_get_docstring(node),
                            base_classes=bases,
                            methods=methods,
                            lifecycle_methods=lifecycle_methods,
                            constructor_params=constructor_params,
                            line_number=node.lineno,
                        )
                        interfaces[name] = interface

        return sorted(interfaces.values(), key=lambda i: i.name)

    @staticmethod
    def _guess_interface(impl_name: str) -> Optional[str]:
        """Guess the interface name from an implementation name."""
        if impl_name.endswith("Impl"):
            return impl_name[:-4]
        return None
