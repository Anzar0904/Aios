from aios.services.engineer.graph import EngineeringGraph
from aios.services.engineer.rules import ArchitectureRuleEngine


def test_circular_dependency_detection():
    # Setup circular imports
    mock_data = {
        "index_data": {
            "core/src/aios/services/a.py": {"imports": ["aios.services.b"]},
            "core/src/aios/services/b.py": {"imports": ["aios.services.a"]},
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
            "core/src/aios/services/my_service.py": {"imports": ["aios.kernel"]},
            "core/src/aios/kernel.py": {"imports": ["skills.my_skill"]},
        }
    }
    graph = EngineeringGraph(mock_data)
    graph.build()
    engine = ArchitectureRuleEngine(graph)
    violations = engine.validate()

    assert any(
        v["type"] == "layering_violation"
        and "my_service.py" in v["description"]
        and "aios.kernel" in v["description"]
        for v in violations
    )
    assert any(
        v["type"] == "layering_violation"
        and "kernel.py" in v["description"]
        and "skills.my_skill" in v["description"]
        for v in violations
    )


def test_invalid_import_concrete():
    # Brain (Layer 4) importing a concrete implementation from Service Layer (Layer 3)
    mock_data = {
        "index_data": {
            "core/src/aios/brain/orchestrator.py": {"imports": ["aios.services.LocalMemoryService"]}
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


def test_class_level_circular_dependency():
    # Setup class-level circular imports
    mock_data = {
        "index_data": {
            "core/src/aios/services/a.py": {"imports": ["aios.services.b.MyClass"]},
            "core/src/aios/services/b.py": {"imports": ["aios.services.a.OtherClass"]},
        }
    }
    graph = EngineeringGraph(mock_data)
    graph.build()
    engine = ArchitectureRuleEngine(graph)
    violations = engine.validate()
    circular = [v for v in violations if v["type"] == "circular_dependency"]
    assert len(circular) > 0
    assert any("aios.services.a" in v["description"] for v in circular)
    assert any("aios.services.b" in v["description"] for v in circular)


def test_kernel_isolation_violations():
    # Setup Kernel (Layer 2) importing Layer 4 and 5 directly
    mock_data = {
        "index_data": {
            "core/src/aios/kernel.py": {
                "imports": [
                    "aios.brain.orchestrator",
                    "skills.my_skill",
                ]
            }
        }
    }
    graph = EngineeringGraph(mock_data)
    graph.build()
    engine = ArchitectureRuleEngine(graph)
    violations = engine.validate()
    layering = [v for v in violations if v["type"] == "layering_violation"]
    assert any("kernel.py" in v["description"] and "brain" in v["description"] for v in layering)
    assert any("kernel.py" in v["description"] and "skill" in v["description"] for v in layering)


def test_module_level_vs_contract_imports():
    # Brain (Layer 4) imports a concrete module (violation) vs. contract (allowed)
    mock_data = {
        "index_data": {
            "core/src/aios/brain/orchestrator.py": {
                "imports": [
                    "aios.services.memory",  # Module-level (concrete namespace) -> Violation
                    "aios.services.MemoryService",  # Contract -> Allowed
                ]
            }
        }
    }
    graph = EngineeringGraph(mock_data)
    graph.build()
    engine = ArchitectureRuleEngine(graph)
    violations = engine.validate()
    layering = [v for v in violations if v["type"] == "layering_violation"]
    assert any(
        "orchestrator.py" in v["description"] and "memory" in v["description"] for v in layering
    )
    assert not any("MemoryService" in v["description"] for v in layering)


def test_core_to_skill_scope_constraints():
    # Layer 3 (Service) and Layer 4 (Brain) cannot import Layer 5 (Skills)
    mock_data = {
        "index_data": {
            "core/src/aios/brain/orchestrator.py": {"imports": ["skills.my_skill"]},
            "core/src/aios/services/my_service.py": {"imports": ["skills.another_skill"]},
        }
    }
    graph = EngineeringGraph(mock_data)
    graph.build()
    engine = ArchitectureRuleEngine(graph)
    violations = engine.validate()
    layering = [v for v in violations if v["type"] == "layering_violation"]
    assert any(
        "my_service.py" in v["description"] and "another_skill" in v["description"]
        for v in layering
    )
    assert any(
        "orchestrator.py" in v["description"] and "my_skill" in v["description"] for v in layering
    )


def test_service_to_engine_layering_violation():
    # Service (Layer 3) cannot import Execution Engine (Layer 4)
    mock_data = {
        "index_data": {
            "core/src/aios/services/my_service.py": {"imports": ["aios.brain.orchestrator"]},
        }
    }
    graph = EngineeringGraph(mock_data)
    graph.build()
    engine = ArchitectureRuleEngine(graph)
    violations = engine.validate()
    layering = [v for v in violations if v["type"] == "layering_violation"]
    assert any(
        "my_service.py" in v["description"] and "brain" in v["description"] for v in layering
    )


def test_skip_test_files_validation():
    # Test files (containing "tests/" or starting with "test_") are skipped
    mock_data = {
        "index_data": {
            "core/tests/test_something.py": {"imports": ["skills.my_skill"]},
            "test_another.py": {"imports": ["skills.another_skill"]},
        }
    }
    graph = EngineeringGraph(mock_data)
    graph.build()
    engine = ArchitectureRuleEngine(graph)
    violations = engine.validate()
    assert len(violations) == 0


def test_deduplicate_cross_layer_violations():
    # Setup duplicate cross-layer imports
    mock_data = {
        "index_data": {
            "core/src/aios/services/my_service.py": {
                "imports": [
                    "aios.kernel",
                    "aios.kernel",
                ]
            }
        }
    }
    graph = EngineeringGraph(mock_data)
    graph.build()
    engine = ArchitectureRuleEngine(graph)
    violations = engine.validate()
    layering = [v for v in violations if v["type"] == "layering_violation"]
    assert len(layering) == 1
