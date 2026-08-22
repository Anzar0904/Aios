from core.tests.run_qdrant_production_validation import copy_reports_to_artifacts


def test_qdrant_artifact_copy_is_opt_in_and_only_copies_reports(tmp_path, monkeypatch):
    reports = tmp_path / "reports"
    reports.mkdir()
    (reports / "QDRANT_REPORT.md").write_text("report")
    (reports / "other.md").write_text("other")
    destination = tmp_path / "artifacts"

    copy_reports_to_artifacts(str(reports))
    assert not destination.exists()

    monkeypatch.setenv("AIOS_QDRANT_ARTIFACT_DIR", str(destination))
    copy_reports_to_artifacts(str(reports))
    assert (destination / "QDRANT_REPORT.md").read_text() == "report"
    assert not (destination / "other.md").exists()
