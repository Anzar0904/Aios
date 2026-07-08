import pytest
from aios.services.engineer.graph import EngineeringGraph


def test_graph_builder_loads_entities():
    mock_data = {
        "scan_results": {
            "packages": ["aios.services"],
            "modules": ["aios.services.context"],
            "services": [{"name": "ContextService", "path": "core/src/aios/services/context.py"}],
            "tests": []
        },
        "index_data": {
            "core/src/aios/services/context.py": {
                "classes": [
                    {
                        "name": "ContextService",
                        "docstring": "",
                        "bases": ["ServiceLifecycle"],
                        "decorators": [],
                        "is_dataclass": False,
                        "is_enum": False,
                        "methods": []
                    }
                ],
                "functions": [],
                "imports": []
            }
        }
    }
    graph = EngineeringGraph(mock_data)
    graph.build()
    assert "ContextService" in graph.entities
    assert graph.entities["ContextService"]["type"] == "service"


@pytest.mark.parametrize(
    "class_data, expected_type, should_be_present",
    [
        # Service branch
        (
            {
                "name": "ContextService",
                "docstring": "",
                "bases": ["ServiceLifecycle"],
                "decorators": [],
                "is_dataclass": False,
                "is_enum": False,
                "methods": []
            },
            "service",
            True,
        ),
        # Provider branch
        (
            {
                "name": "LLMProvider",
                "docstring": "",
                "bases": [],
                "decorators": [],
                "is_dataclass": False,
                "is_enum": False,
                "methods": []
            },
            "provider",
            True,
        ),
        # Registry branch
        (
            {
                "name": "ServiceRegistry",
                "docstring": "",
                "bases": [],
                "decorators": [],
                "is_dataclass": False,
                "is_enum": False,
                "methods": []
            },
            "registry",
            True,
        ),
        # Event branch
        (
            {
                "name": "TaskEvent",
                "docstring": "",
                "bases": [],
                "decorators": [],
                "is_dataclass": False,
                "is_enum": False,
                "methods": []
            },
            "event",
            True,
        ),
        # Dataclass branch
        (
            {
                "name": "TaskData",
                "docstring": "",
                "bases": [],
                "decorators": [],
                "is_dataclass": True,
                "is_enum": False,
                "methods": []
            },
            "dataclass",
            True,
        ),
        # Enum branch
        (
            {
                "name": "TaskStatus",
                "docstring": "",
                "bases": [],
                "decorators": [],
                "is_dataclass": False,
                "is_enum": True,
                "methods": []
            },
            "enum",
            True,
        ),
        # Interface branch (ABC base)
        (
            {
                "name": "BaseAgent",
                "docstring": "",
                "bases": ["ABC"],
                "decorators": [],
                "is_dataclass": False,
                "is_enum": False,
                "methods": []
            },
            "interface",
            True,
        ),
        # Interface branch (Interface in base name)
        (
            {
                "name": "AgentRunner",
                "docstring": "",
                "bases": ["IAgentInterface"],
                "decorators": [],
                "is_dataclass": False,
                "is_enum": False,
                "methods": []
            },
            "interface",
            True,
        ),
        # Default Class branch
        (
            {
                "name": "TaskManager",
                "docstring": "",
                "bases": [],
                "decorators": [],
                "is_dataclass": False,
                "is_enum": False,
                "methods": []
            },
            "class",
            True,
        ),
        # Missing/Empty name (Defensive check)
        (
            {
                "docstring": "",
                "bases": [],
                "decorators": [],
                "is_dataclass": False,
                "is_enum": False,
                "methods": []
            },
            None,
            False,
        ),
    ]
)
def test_graph_builder_type_classification(class_data, expected_type, should_be_present):
    mock_data = {
        "index_data": {
            "core/src/aios/services/context.py": {
                "classes": [class_data]
            }
        }
    }
    graph = EngineeringGraph(mock_data)
    graph.build()
    
    if should_be_present:
        class_name = class_data["name"]
        assert class_name in graph.entities
        assert graph.entities[class_name]["type"] == expected_type
    else:
        assert len(graph.entities) == 0
