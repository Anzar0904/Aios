import pytest
from aios.services.engineer.graph import EngineeringGraph
from aios.services.engineer.impact import ImpactAnalyzer

def test_impact_analyzer_determines_dependents():
    mock_data = {
        "scan_results": {
            "tests": [
                {"name": "test_memory.py", "path": "core/tests/test_memory.py"},
                {"name": "test_context.py", "path": "core/tests/test_context.py"}
            ]
        },
        "index_data": {
            "core/src/aios/services/context.py": {
                "classes": [{"name": "ContextService"}],
                "imports": []
            },
            "core/src/aios/services/memory.py": {
                "classes": [{"name": "MemoryService"}],
                "imports": ["aios.services.context"]
            }
        }
    }
    graph = EngineeringGraph(mock_data)
    graph.build()
    analyzer = ImpactAnalyzer(graph)
    report = analyzer.analyze("ContextService")
    assert "core/src/aios/services/memory.py" in report["dependents"]
    assert "core/tests/test_context.py" in report["affected_tests"]
    assert report["risk_score"] == 10 + 1 * 15 + 1 * 5  # 30

def test_impact_analyzer_entity_not_found():
    mock_data = {
        "scan_results": {
            "tests": []
        },
        "index_data": {
            "core/src/aios/services/context.py": {
                "classes": [{"name": "ContextService"}],
                "imports": []
            }
        }
    }
    graph = EngineeringGraph(mock_data)
    graph.build()
    analyzer = ImpactAnalyzer(graph)
    report = analyzer.analyze("NonExistentService")
    assert "error" in report
    assert "NonExistentService not found" in report["error"]

def test_impact_analyzer_max_risk_score():
    mock_data = {
        "scan_results": {
            "tests": [
                {"name": "test_context_1.py", "path": "core/tests/test_context_1.py"},
                {"name": "test_context_2.py", "path": "core/tests/test_context_2.py"},
                {"name": "test_context_3.py", "path": "core/tests/test_context_3.py"},
                {"name": "test_context_4.py", "path": "core/tests/test_context_4.py"},
                {"name": "test_context_5.py", "path": "core/tests/test_context_5.py"},
                {"name": "test_context_6.py", "path": "core/tests/test_context_6.py"},
            ]
        },
        "index_data": {
            "core/src/aios/services/context.py": {
                "classes": [{"name": "ContextService"}],
                "imports": []
            },
            "core/src/aios/services/memory.py": {
                "classes": [{"name": "MemoryService"}],
                "imports": ["aios.services.context"]
            },
            "core/src/aios/services/persistence.py": {
                "classes": [{"name": "PersistenceService"}],
                "imports": ["aios.services.context"]
            },
            "core/src/aios/services/orchestrator.py": {
                "classes": [{"name": "OrchestratorService"}],
                "imports": ["aios.services.context"]
            },
            "core/src/aios/services/agent.py": {
                "classes": [{"name": "AgentService"}],
                "imports": ["aios.services.context"]
            },
            "core/src/aios/services/kernel.py": {
                "classes": [{"name": "KernelService"}],
                "imports": ["aios.services.context"]
            },
            "core/src/aios/services/action.py": {
                "classes": [{"name": "ActionService"}],
                "imports": ["aios.services.context"]
            }
        }
    }
    graph = EngineeringGraph(mock_data)
    graph.build()
    analyzer = ImpactAnalyzer(graph)
    report = analyzer.analyze("ContextService")
    
    # 6 dependents: memory, persistence, orchestrator, agent, kernel, action
    # 6 affected tests: test_context_1 to 6
    # Raw score: 10 + 6 * 15 + 6 * 5 = 10 + 90 + 30 = 130 -> Capped at 100
    assert len(report["dependents"]) == 6
    assert len(report["affected_tests"]) == 6
    assert report["risk_score"] == 100
