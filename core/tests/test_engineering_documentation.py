from unittest.mock import MagicMock

from aios.services.engineering_documentation import (
    DecisionRecord,
    EngineeringDocumentArtifact,
    EngineeringDocumentationReport,
    ImplementationSummary,
    RiskSummary,
    ValidationSummary,
)
from aios.services.engineering_documentation_impl import (
    LocalADRGenerator,
    LocalEngineeringDocumentationService,
    LocalEngineeringDocumentPlanner,
    LocalEngineeringDocumentValidator,
    LocalEngineeringReportGenerator,
)
from aios.services.knowledge_hub import KnowledgeHubService
from aios.services.memory import MemoryService
from aios.services.model import LLMResponse, ModelService


def test_adr_generation():
    generator = LocalADRGenerator()
    record = DecisionRecord(
        adr_id="ADR-001",
        title="SQLite usage",
        status="accepted",
        context="Context details",
        decision="Decision statement",
        alternatives=["Postgres"],
        consequences="Consequences statement",
    )

    output = generator.generate_adr(record)
    assert "# ADR ADR-001: SQLite usage" in output
    assert "Context details" in output
    assert "- Postgres" in output


def test_engineering_reports():
    generator = LocalEngineeringReportGenerator()
    summary = ImplementationSummary("s1", ["Feature A"], ["Step 1"], ["file.py"])
    validation = ValidationSummary("v1", 10, 9, 90.0)
    risk = RiskSummary("r1", "low", ["Domain"])

    output = generator.generate_engineering_report(summary, validation, risk)
    assert "# Executive Implementation Report" in output
    assert "- `file.py`" in output
    assert "90.0%" in output
    assert "LOW" in output


def test_decision_records_planning():
    planner = LocalEngineeringDocumentPlanner()
    records = planner.plan_engineering_documents("ws_1")

    assert len(records) > 0
    assert records[0].adr_id == "ADR-001"


def test_document_validator():
    validator = LocalEngineeringDocumentValidator()

    # 1. Valid
    r = DecisionRecord("1", "title", "status", "context", "decision")
    artifact = EngineeringDocumentArtifact("a1", "ws_1", "", 0.0, [r])
    errors = validator.validate_engineering_document(artifact)
    assert len(errors) == 0

    # 2. Duplicate ADR
    artifact.adr_records.append(r)
    errors_dup = validator.validate_engineering_document(artifact)
    assert len(errors_dup) == 1
    assert "Duplicate ADR ID: '1'" in errors_dup[0]


def test_service_evaluation_flow():
    mock_memory = MagicMock(spec=MemoryService)
    mock_kh = MagicMock(spec=KnowledgeHubService)
    mock_model = MagicMock(spec=ModelService)

    # Mock LLM Response
    mock_response = MagicMock(spec=LLMResponse)
    mock_response.content = "# ADR ADR-001\nLLM Refined ADR content."
    mock_model.execute_request.return_value = mock_response

    service = LocalEngineeringDocumentationService(
        memory_service=mock_memory, knowledge_hub=mock_kh, model_service=mock_model
    )
    service.initialize()

    record = DecisionRecord("ADR-001", "SQLite", "accepted", "context", "decision")
    artifact = service.create_adr_document("ws_1", record)
    assert "LLM Refined ADR content." in artifact.content

    # Store
    service.store_engineering_summary(artifact)
    mock_memory.add_memory.assert_called_once()

    # Publish
    report = EngineeringDocumentationReport(
        "r1", "ws_1", "Executive summary content", "Low risk assessment", 0.0, ["rec1"]
    )
    service.publish_engineering_report(report)
    mock_kh.sync_document.assert_called_once()


def test_backward_compatibility():
    class CustomValidator(LocalEngineeringDocumentValidator):
        def validate_engineering_document(self, artifact):
            errors = super().validate_engineering_document(artifact)
            errors.append("custom_error")
            return errors

    validator = CustomValidator()
    errors = validator.validate_engineering_document(
        EngineeringDocumentArtifact("a1", "ws_1", "", 0.0, [])
    )
    assert "custom_error" in errors
