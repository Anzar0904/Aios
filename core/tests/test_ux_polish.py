import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

from aios.ux import (
    BootExperience,
    DashboardRenderer,
    DiagnosticsEngine,
    LiveProgressEngine,
    SessionManager,
    SetupWizard,
    StartupHealthChecks,
)


def test_boot_experience():
    with patch("time.sleep", return_value=None):
        duration = BootExperience.boot()
        assert duration > 0


def test_startup_health_checks():
    results = StartupHealthChecks.run_checks()
    assert "Internet Connection" in results
    assert "Workspace Directory" in results
    assert results["Workspace Directory"] == "Healthy"


def test_live_progress_engine():
    with patch("time.sleep", return_value=None):
        with LiveProgressEngine(description="Testing Engine") as engine:
            engine.update("Still testing")
            assert engine.description == "Testing Engine"


def test_diagnostics_engine():
    metrics = DiagnosticsEngine.get_metrics()
    assert "boot_time" in metrics
    assert "loaded_modules" in metrics
    assert metrics["loaded_modules"] == 47


def test_session_manager():
    temp_dir = Path(tempfile.mkdtemp())
    try:
        session_file = temp_dir / "session.json"
        mgr = SessionManager(path=session_file)
        
        # Load empty session
        data = mgr.load_session()
        assert data["current_project"] == "Aios"
        
        # Save session updates
        mgr.save_session({"current_project": "UpdatedProject"})
        
        # Load again
        updated_data = mgr.load_session()
        assert updated_data["current_project"] == "UpdatedProject"
    finally:
        shutil.rmtree(temp_dir)


def test_dashboard_renderer():
    with patch("rich.console.Console.print") as mock_print:
        DashboardRenderer.render()
        mock_print.assert_called()


@patch(
    "builtins.input",
    side_effect=[
        "openrouter",
        "qwen/qwen3-coder",
        "my-key",
        "my-user",
        "my-token",
        "my-url",
        "my-role",
        "my-vtoken",
    ],
)
@patch("os.chmod")
def test_setup_wizard(mock_chmod, mock_input):
    temp_dir = Path(tempfile.mkdtemp())
    try:
        # Patch keys locations
        with patch("pathlib.Path.cwd", return_value=temp_dir):
            SetupWizard.run()
    finally:
        shutil.rmtree(temp_dir)
