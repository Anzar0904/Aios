"""
refgen_models.py — Enhanced data models for API reference generation.

Extends the base docgen models with detailed method signatures, parameters,
return types, exceptions, and lifecycle information.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ParameterInfo:
    """Represents a method parameter with type information."""

    name: str
    type_annotation: Optional[str] = None
    default_value: Optional[str] = None
    is_required: bool = True


@dataclass
class MethodSignature:
    """Detailed method signature with parameters, return type, and exceptions."""

    name: str
    parameters: List[ParameterInfo] = field(default_factory=list)
    return_type: Optional[str] = None
    docstring: Optional[str] = None
    exceptions: List[str] = field(default_factory=list)
    is_async: bool = False
    is_property: bool = False
    is_classmethod: bool = False
    is_staticmethod: bool = False
    line_number: int = 0


@dataclass
class LifecycleMethod:
    """Lifecycle method (init_service, cleanup, etc.) with documentation."""

    name: str
    phase: str  # "initialization", "cleanup", "runtime"
    signature: MethodSignature
    dependencies: List[str] = field(default_factory=list)


@dataclass
class ServiceInterface:
    """Enhanced service interface with full API documentation."""

    name: str
    module: str
    file_path: str
    docstring: Optional[str]
    base_classes: List[str] = field(default_factory=list)
    methods: List[MethodSignature] = field(default_factory=list)
    lifecycle_methods: List[LifecycleMethod] = field(default_factory=list)
    constructor_params: List[ParameterInfo] = field(default_factory=list)
    implementation: Optional[str] = None
    impl_module: Optional[str] = None
    line_number: int = 0


@dataclass
class InterfaceImplementationPair:
    """Pairs an interface with its concrete implementation."""

    interface_name: str
    interface_module: str
    implementation_name: str
    implementation_module: str
    di_binding_location: Optional[str] = None
