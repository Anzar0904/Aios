from pathlib import Path
from unittest.mock import MagicMock, patch

from aios.services.context import (
    ContextChangedEvent,
    ContextLoadedEvent,
    WorkspaceContext,
)
from aios.services.context_impl import LocalContextService
from aios.services.event_bus_impl import LocalEventBus


def test_context_detection_git():
    event_bus = LocalEventBus()
    event_bus.register_event_type(ContextLoadedEvent)
    event_bus.register_event_type(ContextChangedEvent)

    # Subscribe to verify event publication
    events = []
    event_bus.subscribe(ContextLoadedEvent, lambda e: events.append(e))

    service = LocalContextService(event_bus)

    # Mock subprocess.run for git commands
    mock_toplevel = MagicMock()
    mock_toplevel.stdout = "/Users/anzarakhtar/aios\n"
    mock_toplevel.returncode = 0

    mock_branch = MagicMock()
    mock_branch.stdout = "main\n"
    mock_branch.returncode = 0

    def side_effect(args, **kwargs):
        if "--show-toplevel" in args:
            return mock_toplevel
        elif "--abbrev-ref" in args:
            return mock_branch
        raise FileNotFoundError()

    with patch("subprocess.run", side_effect=side_effect):
        context = service.detect_context()

    assert isinstance(context, WorkspaceContext)
    assert context.working_directory == str(Path.cwd().resolve())
    assert context.git_repo_path == "/Users/anzarakhtar/aios"
    assert context.git_branch == "main"
    assert context.project_root == "/Users/anzarakhtar/aios"
    assert context.project_name == "aios"

    # Loaded event must have been published
    assert len(events) == 1
    assert events[0].context == context

    assert service.get_current_context() == context


def test_context_detection_fallback():
    event_bus = LocalEventBus()
    event_bus.register_event_type(ContextLoadedEvent)
    event_bus.register_event_type(ContextChangedEvent)

    service = LocalContextService(event_bus)

    # Mock subprocess.run to raise FileNotFoundError to simulate missing git binary
    with patch("subprocess.run", side_effect=FileNotFoundError("git not found")):
        context = service.detect_context()

    assert context.git_repo_path is None
    assert context.git_branch is None
    assert context.project_root == str(Path.cwd().resolve())
    assert context.project_name == Path.cwd().name


def test_context_change_event():
    event_bus = LocalEventBus()
    event_bus.register_event_type(ContextLoadedEvent)
    event_bus.register_event_type(ContextChangedEvent)

    loaded_events = []
    changed_events = []

    event_bus.subscribe(ContextLoadedEvent, lambda e: loaded_events.append(e))
    event_bus.subscribe(ContextChangedEvent, lambda e: changed_events.append(e))

    service = LocalContextService(event_bus)

    # First detection publishes LoadedEvent
    c1 = service.detect_context()
    assert len(loaded_events) == 1
    assert len(changed_events) == 0

    # Mock context change (by modifying cwd in patch)
    with patch("pathlib.Path.cwd", return_value=Path("/tmp/fake_project")):
        with patch("subprocess.run", side_effect=FileNotFoundError()):
            c2 = service.detect_context()

    assert c1 != c2
    assert len(loaded_events) == 1
    assert len(changed_events) == 1
    assert changed_events[0].old_context == c1
    assert changed_events[0].new_context == c2
