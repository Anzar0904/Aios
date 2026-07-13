from aios.services.engineer.dependency import DependencyAnalyzer
from aios.services.engineer.graph import EngineeringGraph


def test_dependency_analyzer_exports_all_dot_graphs():
    mock_data = {
        "index_data": {
            "core/src/aios/services/context.py": {
                "classes": [
                    {
                        "name": "ContextService",
                        "bases": ["ServiceLifecycle"],
                        "methods": [
                            {
                                "name": "__init__",
                                "arguments": [
                                    {"name": "self", "type": None},
                                    {"name": "memory_service", "type": "MemoryService"},
                                    {"name": "llm_provider", "type": "Optional[LLMProvider]"},
                                ],
                            },
                            {
                                "name": "handle_task",
                                "arguments": [
                                    {"name": "self", "type": None},
                                    {"name": "event", "type": "TaskEvent"},
                                ],
                            },
                        ],
                    }
                ],
                "imports": ["aios.services.memory", "aios.providers.llm"],
            },
            "core/src/aios/services/memory.py": {
                "classes": [
                    {
                        "name": "MemoryService",
                        "bases": ["ServiceLifecycle"],
                        "methods": [
                            {"name": "__init__", "arguments": [{"name": "self", "type": None}]}
                        ],
                    }
                ],
                "imports": [],
            },
            "core/src/aios/providers/llm.py": {
                "classes": [
                    {
                        "name": "LLMProvider",
                        "bases": ["BaseProvider"],
                        "methods": [
                            {"name": "__init__", "arguments": [{"name": "self", "type": None}]}
                        ],
                    }
                ],
                "imports": [],
            },
            "core/src/aios/events/task.py": {
                "classes": [
                    {"name": "TaskEvent", "bases": ["BaseEvent"], "methods": []},
                    {"name": "BaseEvent", "bases": [], "methods": []},
                ],
                "imports": [],
            },
        }
    }
    graph = EngineeringGraph(mock_data)
    graph.build()
    analyzer = DependencyAnalyzer(graph)

    # 1. Import Graph
    import_dot = analyzer.generate_import_graph()
    assert "digraph ImportGraph {" in import_dot
    assert '"context" -> "memory";' in import_dot
    assert '"context" -> "llm";' in import_dot

    # 2. Service Graph
    service_dot = analyzer.generate_service_graph()
    assert "digraph ServiceGraph {" in service_dot
    assert '"ContextService" -> "MemoryService";' in service_dot

    # 3. Event Graph
    event_dot = analyzer.generate_event_graph()
    assert "digraph EventGraph {" in event_dot
    assert '"BaseEvent" -> "TaskEvent";' in event_dot
    assert '"ContextService" -> "TaskEvent";' in event_dot

    # 4. Provider Graph
    provider_dot = analyzer.generate_provider_graph()
    assert "digraph ProviderGraph {" in provider_dot
    assert '"ContextService" -> "LLMProvider";' in provider_dot
