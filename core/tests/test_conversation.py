from unittest.mock import MagicMock

from aios.services.conversation.manager import ConversationManager
from aios.services.conversation.store import ConversationStore
from aios.services.model import LLMResponse


def test_conversation_persistence_and_loading(tmp_path):
    store = ConversationStore(tmp_path)
    manager = ConversationManager(store)

    # 1. Create conversation
    conv = manager.create_conversation(title="Test Conv", agent_name="developer_agent")
    assert conv.title == "Test Conv"
    assert conv.active_agent == "developer_agent"

    # 2. Add messages
    manager.add_message(conv.id, "user", "Hello agent")
    manager.add_message(conv.id, "assistant", "Hello user")

    # 3. Reload from store
    store2 = ConversationStore(tmp_path)
    manager2 = ConversationManager(store2)
    conv_loaded = manager2.resume_conversation(conv.id)

    assert conv_loaded is not None
    assert conv_loaded.title == "Test Conv"
    assert len(conv_loaded.messages) == 2
    assert conv_loaded.messages[0].role == "user"
    assert conv_loaded.messages[0].content == "Hello agent"
    assert conv_loaded.messages[1].role == "assistant"
    assert conv_loaded.messages[1].content == "Hello user"


def test_conversation_manager_lifecycle(tmp_path):
    store = ConversationStore(tmp_path)
    manager = ConversationManager(store)

    # Create conversations
    c1 = manager.create_conversation("C1")
    c2 = manager.create_conversation("C2")

    # List
    convs = manager.list_conversations()
    assert len(convs) == 2
    assert any(c["title"] == "C1" for c in convs)

    # Rename
    manager.rename_conversation(c1.id, "New C1")
    assert manager.store.load(c1.id)["title"] == "New C1"

    # Switch/Resume
    manager.resume_conversation(c2.id)
    assert manager.get_current_conversation().id == c2.id

    # Delete
    manager.delete_conversation(c2.id)
    assert manager.get_current_conversation() is None
    assert len(manager.list_conversations()) == 1


def test_conversation_summarization(tmp_path):
    store = ConversationStore(tmp_path)
    manager = ConversationManager(store)

    conv = manager.create_conversation("Summarize test")
    # Add 11 messages (limit is 10)
    for i in range(11):
        role = "user" if i % 2 == 0 else "assistant"
        manager.add_message(conv.id, role, f"Message {i}")

    conv = manager.get_current_conversation()
    assert len(conv.messages) == 11

    # Mock model service
    model_service = MagicMock()
    model_service.execute_request.return_value = LLMResponse(
        content=(
            "Summary: Explored repository structure.\n"
            "Decisions:\n"
            "- Selected Python for coding.\n"
            "Action Items:\n"
            "- Write code.\n"
            "Unresolved Questions:\n"
            "- Which framework?"
        ),
        model_name="claude-3-5-sonnet",
        provider_name="claude",
    )

    # Trigger summarization
    manager.summarize_if_needed(conv, model_service, max_messages=10)

    # Verify summary is stored and message history is truncated
    conv_updated = manager.get_current_conversation()
    assert len(conv_updated.messages) == 4
    assert conv_updated.summary is not None
    assert conv_updated.summary.summary == "Explored repository structure."
    assert "Selected Python for coding." in conv_updated.summary.decisions
    assert "Write code." in conv_updated.summary.action_items
    assert "Which framework?" in conv_updated.summary.unresolved_questions
