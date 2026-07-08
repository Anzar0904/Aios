from aios.services.engineer.graph import EngineeringGraph
from aios.services.engineer.rules import ArchitectureRuleEngine

def test_circular_dependency_detection():
    # Setup circular imports
    mock_data = {
        "index_data": {
            "core/src/aios/services/a.py": {
                "imports": ["aios.services.b"]
            },
            "core/src/aios/services/b.py": {
                "imports": ["aios.services.a"]
            }
        }
    }
    graph = EngineeringGraph(mock_data)
    graph.build()
    engine = ArchitectureRuleEngine(graph)
    violations = engine.validate()
    assert any("circular" in v["type"] for v in violations)

def test_layering_violation_detection():
    # Service importing Kernel (Layer 3 importing Layer 2)
    # Kernel importing Skills (Layer 2 importing Layer 5)
    mock_data = {
        "index_data": {
            "core/src/aios/services/my_service.py": {
                "imports": ["aios.kernel"]
            },
            "core/src/aios/kernel.py": {
                "imports": ["skills.my_skill"]
            }
        }
    }
    graph = EngineeringGraph(mock_data)
    graph.build()
    engine = ArchitectureRuleEngine(graph)
    violations = engine.validate()
    
    assert any(
        v["type"] == "layering_violation" and "my_service.py" in v["description"] and "aios.kernel" in v["description"]
        for v in violations
    )
    assert any(
        v["type"] == "layering_violation" and "kernel.py" in v["description"] and "skills.my_skill" in v["description"]
        for v in violations
    )

def test_invalid_import_concrete():
    # Brain (Layer 4) importing a concrete implementation from Service Layer (Layer 3)
    mock_data = {
        "index_data": {
            "core/src/aios/brain/orchestrator.py": {
                "imports": ["aios.services.LocalMemoryService"]
            }
        }
    }
    graph = EngineeringGraph(mock_data)
    graph.build()
    engine = ArchitectureRuleEngine(graph)
    violations = engine.validate()
    
    assert any(
        v["type"] == "invalid_import" and "LocalMemoryService" in v["description"]
        for v in violations
    )
