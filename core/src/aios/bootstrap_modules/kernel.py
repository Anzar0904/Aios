"""
bootstrap_modules/kernel.py

Instantiates the global Kernel with the ServiceRegistry.
"""

from __future__ import annotations

from pathlib import Path

from aios.kernel import Kernel


def bootstrap_kernel_instance(config_path: Path, registry, runtime_service) -> Kernel:  # noqa: ANN001
    """Constructs the Kernel and links the runtime service."""
    kernel = Kernel(config_path=config_path, registry=registry)
    runtime_service._kernel = kernel
    return kernel
