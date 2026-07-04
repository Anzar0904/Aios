from aios.services.intelligence import (
    ContextRanker,
    IntentExpander,
    MemoryRanker,
    ReasoningContext,
    RepositoryAnalyzer,
    ToolSelector,
)
from aios.services.intent import Intent, IntentType


def test_repository_analyzer():
    scanner_res = {"project_name": "test-project", "git_branch": "main"}
    index_res = {"languages": ["Python"]}

    analyzer = RepositoryAnalyzer(scanner_res, index_res)
    analysis = analyzer.analyze()

    assert analysis.project_name == "test-project"
    assert analysis.git_branch == "main"
    assert analysis.languages == ["Python"]


def test_memory_ranker():
    class MockMemoryMetadata:
        def __init__(self, workspace_id, importance, tags):
            self.workspace_id = workspace_id
            self.importance = importance
            self.tags = tags

    class MockMemory:
        def __init__(self, content, created_at, metadata):
            self.content = content
            self.created_at = created_at
            self.metadata = metadata

    m1 = MockMemory(
        "database connections and parameters",
        0.0,
        MockMemoryMetadata("ws-1", 3, ["db"]),
    )
    m2 = MockMemory("unrelated test case", 0.0, MockMemoryMetadata("ws-2", 1, ["test"]))

    ranker = MemoryRanker([m1, m2])
    ranked = ranker.rank("database config query", "ws-1")

    assert len(ranked) == 2
    assert ranked[0].content == "database connections and parameters"


def test_context_ranker():
    tree_lines = [f"line{i}" for i in range(1, 23)]
    full_analysis = {
        "project_name": "my-os",
        "directory_tree": "\n".join(tree_lines),
        "git_status": "Changes staged",
        "git_diff": "diff --git",
        "open_todos": "TODO: fix bugs",
    }

    ranker = ContextRanker()
    # 1. Non-git, non-todo action
    ctx = ranker.select_context("ExplainFile", "tell me about architecture", full_analysis)
    assert ctx["git_status"] == "Omitted for context focus."
    assert "truncated" in ctx["directory_tree"]
    assert ctx["open_todos"] == "Omitted for context focus."

    # 2. Git action
    ctx_git = ranker.select_context("GitReview", "git changes", full_analysis)
    assert ctx_git["git_status"] == "Changes staged"
    assert ctx_git["git_diff"] == "diff --git"


def test_tool_selector():
    selector = ToolSelector()

    intent_git = Intent(IntentType.DEVELOPER, "AgentRuntimeService", "GitReview", {}, 1.0)
    tools_git = selector.select_tools(intent_git)
    assert "git" in tools_git

    intent_fs = Intent(IntentType.DEVELOPER, "AgentRuntimeService", "ExplainFile", {}, 1.0)
    tools_fs = selector.select_tools(intent_fs)
    assert "filesystem" in tools_fs


def test_intent_expander():
    expander = IntentExpander()

    intent = Intent(IntentType.DEVELOPER, "AgentRuntimeService", "ReviewRepository", {}, 1.0)
    expanded = expander.expand(intent)
    assert "senior software engineering review" in expanded


def test_reasoning_context_assembly():
    intent = Intent(IntentType.DEVELOPER, "AgentRuntimeService", "GitReview", {}, 1.0)
    r_ctx = ReasoningContext(
        intent=intent,
        repository_analysis={"project_name": "test"},
        conversation_summary="Summary text",
        conversation_history="History text",
        memories=[],
        workspace={"project_name": "test"},
        selected_tools=["git"],
        expanded_query="Expanded text",
    )

    assert r_ctx.intent == intent
    assert r_ctx.selected_tools == ["git"]
    assert r_ctx.expanded_query == "Expanded text"
