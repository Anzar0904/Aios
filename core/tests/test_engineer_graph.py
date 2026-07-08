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
