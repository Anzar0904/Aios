"""
GitHub Intelligence Module — Sprint 25.

Exposes:
    GitHubConnectionManager   — auth, discovery, connection testing
    GitHubIntelligenceEngine  — repo/PR/issue/branch/commit/release/actions intelligence
    GitHubMemory              — persistent repository metadata cache
    GitHubReportGenerator     — docs/github/ markdown report generation
"""

from aios.github.connection import GitHubConnectionManager
from aios.github.intelligence import GitHubIntelligenceEngine
from aios.github.memory import GitHubMemory
from aios.github.reports import GitHubReportGenerator

__all__ = [
    "GitHubConnectionManager",
    "GitHubIntelligenceEngine",
    "GitHubMemory",
    "GitHubReportGenerator",
]
