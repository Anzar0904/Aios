import os
import pytest
from unittest.mock import MagicMock

from aios.services.workspace_intelligence import CodeStructureSummary
from aios.services.model import ModelService, LLMResponse
from aios.services.memory import MemoryService
from aios.services.knowledge_hub import KnowledgeHubService
from aios.services.code_generation import (
    GenerationPolicy,
    GeneratedArtifact,
    GenerationSession,
)
from aios.services.code_generation_impl import (
    LocalCodePlanner,
    LocalContextAssembler,
    LocalPromptBuilder,
    LocalFileGenerator,
    LocalFileEditor,
    LocalSyntaxValidator,
    LocalStyleValidator,
    LocalImportValidator,
    LocalGenerationValidator,
    LocalCodeGenerationService,
)


def test_code_planner():
    planner = LocalCodePlanner()
    steps = planner.plan_generation_steps("create a helper file", GenerationPolicy.BALANCED)
    assert len(steps) == 1
    assert steps[0]["action"] == "create"


def test_context_assembler():
    assembler = LocalContextAssembler()
    summary = CodeStructureSummary(
        summary_id="s1",
        timestamp=0.0,
        symbols={},
        call_graph={},
        dependency_graph={"main.py": ["utils.py"]},
        inheritance_map={},
        public_apis=["start"]
    )
    ctx = assembler.assemble_context("main.py", summary)
    assert "utils.py" in ctx
    assert "start" in ctx


def test_prompt_builder_policies():
    builder = LocalPromptBuilder()
    
    req_c = builder.build_prompt("fix bug", "main.py", "context", GenerationPolicy.CONSERVATIVE)
    assert "CONSERVATIVE POLICY" in req_c.prompt
    
    req_a = builder.build_prompt("fix bug", "main.py", "context", GenerationPolicy.AGGRESSIVE)
    assert "AGGRESSIVE POLICY" in req_a.prompt


def test_file_generator_editor(tmp_path):
    generator = LocalFileGenerator()
    editor = LocalFileEditor()
    
    ws_root = str(tmp_path)
    
    art = generator.create_file(ws_root, "test_gen.py", "print('hello')\n")
    assert os.path.exists(os.path.join(ws_root, "test_gen.py"))
    assert art.checksum is not None
    
    art_edit = editor.edit_file(ws_root, "test_gen.py", "print('edited')\n")
    with open(os.path.join(ws_root, "test_gen.py"), "r") as fh:
        assert fh.read() == "print('edited')\n"


def test_syntax_style_validators():
    syntax = LocalSyntaxValidator()
    style = LocalStyleValidator()
    
    # Valid Python Code
    ok, err = syntax.validate_syntax("def test():\n    pass\n", "file.py")
    assert ok
    
    # Invalid Python Code (Syntax Error)
    bad_ok, bad_err = syntax.validate_syntax("def test(\n", "file.py")
    assert not bad_ok
    assert "Python Syntax Error" in bad_err

    # Line Length Style checks
    style_ok, style_err = style.validate_style("a" * 121, "file.py")
    assert not style_ok
    assert "exceeds maximum line length" in style_err


def test_code_generation_service_flow(tmp_path):
    mock_model = MagicMock(spec=ModelService)
    mock_memory = MagicMock(spec=MemoryService)
    mock_kh = MagicMock(spec=KnowledgeHubService)
    
    # Mock LLM Response
    mock_response = MagicMock(spec=LLMResponse)
    mock_response.content = "```python\ndef dynamic_func():\n    return 42\n```"
    mock_model.execute_request.return_value = mock_response
    
    service = LocalCodeGenerationService(
        memory_service=mock_memory,
        model_service=mock_model,
        knowledge_hub=mock_kh
    )
    service.initialize()
    
    session = service.start_session("ws_1", GenerationPolicy.BALANCED)
    assert session.policy == GenerationPolicy.BALANCED
    
    summary = CodeStructureSummary("s1", 0.0, {}, {}, {}, {}, [])
    
    report = service.generate_code(
        session=session,
        target_file="gen_out.py",
        objective="Write dynamic_func",
        workspace_root=str(tmp_path),
        code_summary=summary
    )
    
    assert report.validation_status == "passed"
    assert len(report.artifacts) == 1
    assert os.path.exists(tmp_path / "gen_out.py")
    
    with open(tmp_path / "gen_out.py", "r") as fh:
        assert "def dynamic_func():" in fh.read()
        
    # Store
    service.store_generation_summary(report)
    mock_memory.add_memory.assert_called_once()
    
    # Publish
    service.publish_generation_report(report)
    mock_kh.sync_document.assert_called_once()


def test_backward_compatibility():
    class CustomSyntaxValidator(LocalSyntaxValidator):
        def validate_syntax(self, content, file_path):
            ok, err = super().validate_syntax(content, file_path)
            if not ok:
                return False, err
            return True, "Custom syntax logic."
            
    val = CustomSyntaxValidator()
    assert val is not None
