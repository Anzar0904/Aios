"""
AIOS Documentation Generator (Sprint 7 Milestone 2).

Discovers services, repositories, skills, providers, runtime components,
database models, and DI registrations from source code, then produces
Markdown catalogs into docs/generated/.

Entry point: DocGeneratorEngine.run()
"""

from aios.docgen.engine import DocGeneratorEngine
from aios.docgen.models import GenerationResult, GenerationStatus

__all__ = ["DocGeneratorEngine", "GenerationResult", "GenerationStatus"]
