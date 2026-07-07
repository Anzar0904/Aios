import json
import os
from unittest.mock import MagicMock

import pytest
from aios.services.docintel.agent import DocumentationAgent
from aios.services.model import ModelService


@pytest.fixture
def mock_index_path(tmpdir):
    index_file = os.path.join(tmpdir, "index.json")
    mock_data = {
        "scan_results": {
            "packages": ["aios.services", "aios.providers"],
            "modules": ["aios.services.context", "aios.services.memory"],
            "services": [
                {"name": "ContextService", "path": "core/src/aios/services/context.py"},
                {"name": "MemoryService", "path": "core/src/aios/services/memory.py"},
            ],
            "tests": [{"name": "test_context.py", "path": "core/tests/test_context.py"}],
        },
        "index_data": {
            "core/src/aios/services/context.py": {
                "classes": [
                    {
                        "name": "ContextService",
                        "docstring": "Manages conversation and session context.",
                        "bases": ["ServiceLifecycle"],
                        "decorators": [],
                        "is_dataclass": False,
                        "is_enum": False,
                        "methods": [
                            {"name": "get_context", "arguments": [], "return_type": "Context"}
                        ],
                    }
                ],
                "functions": [],
                "imports": ["aios.services.base"],
            },
            "core/src/aios/services/memory.py": {
                "classes": [
                    {
                        "name": "MemoryService",
                        "docstring": "",  # Undocumented
                        "bases": ["ServiceLifecycle"],
                        "decorators": [],
                        "is_dataclass": False,
                        "is_enum": False,
                        "methods": [],
                    }
                ],
                "functions": [{"name": "load_memories", "arguments": [], "return_type": None}],
                "imports": ["aios.services.context"],
            },
        },
        "intel_report": {
            "score": 85,
            "undocumented_classes": [
                {"class": "MemoryService", "file": "core/src/aios/services/memory.py"}
            ],
            "undocumented_functions": [],
            "todos_fixmes": [],
        },
        "dep_mermaid": "graph TD\n  ContextService --> Base\n  MemoryService --> ContextService",
    }

    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(mock_data, f)
    return index_file


def test_agent_initialization(mock_index_path):
    agent = DocumentationAgent(index_path=mock_index_path)
    agent.initialize()
    assert agent._is_initialized
    assert "scan_results" in agent.index


def test_agent_fuzzy_symbol_search(mock_index_path):
    agent = DocumentationAgent(index_path=mock_index_path)
    agent.initialize()

    # Search for ContextService
    cls_res = agent.search_class("context")
    assert len(cls_res) > 0
    assert cls_res[0]["name"] == "ContextService"

    # Search for MemoryService
    symbol_res = agent.search_symbol("memory")
    assert len(symbol_res) > 0
    assert any(s["name"] == "MemoryService" for s in symbol_res)


def test_agent_ask_specific_class(mock_index_path):
    agent = DocumentationAgent(index_path=mock_index_path)
    agent.initialize()

    res = agent.ask("Explain class ContextService")
    assert "ContextService" in res
    assert "core/src/aios/services/context.py" in res
    assert "Manages conversation and session context." in res


def test_agent_ask_dependencies_and_dependents(mock_index_path):
    agent = DocumentationAgent(index_path=mock_index_path)
    agent.initialize()

    # ContextService has dependent: MemoryService
    res = agent.ask("Explain ContextService")
    assert "memory.py" in res


def test_agent_ask_special_queries(mock_index_path):
    agent = DocumentationAgent(index_path=mock_index_path)
    agent.initialize()

    # Undocumented modules
    res = agent.ask("Which modules have no documentation?")
    assert "MemoryService" in res

    # Untested functions
    res = agent.ask("Which functions lack tests?")
    assert "memory.py" in res  # memory.py has no tests in mock conftest

    # Dependency graph
    res = agent.ask("Explain the dependency graph")
    assert "Dependency Graph Overview" in res
    assert "graph TD" in res


def test_agent_ask_with_model_service(mock_index_path):
    mock_model = MagicMock(spec=ModelService)
    mock_model.execute_prompt.return_value = "Synthesized explanation from LLM."

    agent = DocumentationAgent(model_service=mock_model, index_path=mock_index_path)
    agent.initialize()

    res = agent.ask("Explain ContextService")
    assert "Synthesized explanation from LLM." in res
    mock_model.execute_prompt.assert_called_once()
