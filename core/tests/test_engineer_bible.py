import json
from unittest.mock import MagicMock

from aios.services.engineer.bible import EngineeringBibleService
from aios.services.engineer.graph import EngineeringGraph


def test_bible_service_exact_search():
    mock_data = {
        "index_data": {
            "core/src/aios/services/context.py": {
                "classes": [{"name": "ContextService"}],
                "imports": []
            }
        }
    }
    graph = EngineeringGraph(mock_data)
    graph.build()
    service = EngineeringBibleService(graph=graph)
    service.initialize()
    res = service.search("ContextService")
    assert any(r["name"] == "ContextService" for r in res)

def test_bible_service_search_variations():
    mock_data = {
        "index_data": {
            "core/src/aios/services/context.py": {
                "classes": [{"name": "ContextService"}],
                "imports": []
            },
            "core/src/aios/services/omniroute.py": {
                "classes": [{"name": "OmniRouteRegistry"}],
                "imports": []
            }
        }
    }
    graph = EngineeringGraph(mock_data)
    graph.build()
    service = EngineeringBibleService(graph=graph)
    service.initialize()

    # Search with lower case (fuzzy/case-insensitive match on name)
    res_lower = service.search("contextservice")
    assert len(res_lower) == 1
    assert res_lower[0]["name"] == "ContextService"

    # Search with part of file path
    res_file = service.search("omniroute.py")
    assert len(res_file) == 1
    assert res_file[0]["name"] == "OmniRouteRegistry"

    # Search non-matching query
    res_none = service.search("NonExistentEntity")
    assert len(res_none) == 0

def test_bible_service_lifecycle_with_provided_graph():
    mock_data = {
        "index_data": {}
    }
    graph = EngineeringGraph(mock_data)
    service = EngineeringBibleService(graph=graph)
    assert not service._is_initialized

    # Initialize, start, shutdown
    service.initialize()
    assert service._is_initialized
    assert service.dependency_analyzer is not None
    assert service.rule_engine is not None
    assert service.impact_analyzer is not None

    # Verify start and shutdown don't crash
    service.start()
    service.shutdown()

def test_bible_service_init_load_index_file(tmp_path):
    mock_data = {
        "index_data": {
            "core/src/aios/services/dummy.py": {
                "classes": [{"name": "DummyService"}],
                "imports": []
            }
        }
    }
    index_file = tmp_path / "index.json"
    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(mock_data, f)

    service = EngineeringBibleService(index_path=str(index_file))
    assert service.graph is None

    service.initialize()
    assert service.graph is not None
    assert "DummyService" in service.graph.entities

def test_bible_service_init_fallback_empty_graph(tmp_path):
    # index_path does not exist
    index_file = tmp_path / "non_existent_index.json"
    service = EngineeringBibleService(index_path=str(index_file))
    assert service.graph is None

    service.initialize()
    assert service.graph is not None
    assert len(service.graph.entities) == 0

def test_bible_service_get_decision_memory():
    mock_data = {"index_data": {}}
    graph = EngineeringGraph(mock_data)
    service = EngineeringBibleService(graph=graph)
    service.initialize()

    decisions = service.get_decision_memory()
    assert "decisions" in decisions
    assert len(decisions["decisions"]) >= 2
    assert any("Freeze AI Core API architectures" in d["decision"] for d in decisions["decisions"])

def test_bible_service_generate_context_no_model():
    mock_data = {"index_data": {}}
    graph = EngineeringGraph(mock_data)
    service = EngineeringBibleService(graph=graph)
    service.initialize()

    context = service.generate_engineering_context("Implement Task 5")
    assert "Architecture Constraint Guidelines:" in context
    assert "- Do not modify frozen core APIs." in context

def test_bible_service_generate_context_with_model():
    mock_data = {"index_data": {}}
    graph = EngineeringGraph(mock_data)
    
    mock_model = MagicMock()
    mock_model.execute_prompt.return_value = "Custom Guidelines: Always write tests."

    service = EngineeringBibleService(model_service=mock_model, graph=graph)
    service.initialize()

    context = service.generate_engineering_context("Implement Task 5")
    assert context == "Custom Guidelines: Always write tests."
    mock_model.execute_prompt.assert_called_once()

def test_bible_service_generate_context_model_exception():
    mock_data = {"index_data": {}}
    graph = EngineeringGraph(mock_data)
    
    mock_model = MagicMock()
    mock_model.execute_prompt.side_effect = Exception("LLM connection timed out")

    service = EngineeringBibleService(model_service=mock_model, graph=graph)
    service.initialize()

    context = service.generate_engineering_context("Implement Task 5")
    assert "Failed to call LLM model" in context
    assert "LLM connection timed out" in context
