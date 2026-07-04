import sys
from unittest.mock import MagicMock, patch
import pytest

from aios.cli import (
    handle_conversation_command,
    print_help_table,
    print_skills_table,
    print_providers_table,
    handle_model_switch,
)
from aios.skills.base import BaseSkill
from aios.skills.metadata import SkillMetadata
from aios.skills.registry import SkillRegistry


def test_handle_conversation_command_list_empty():
    conv_manager = MagicMock()
    conv_manager.list_conversations.return_value = []
    
    # Capture standard output or just verify it returns True
    res = handle_conversation_command("list conversations", conv_manager)
    assert res is True
    conv_manager.list_conversations.assert_called_once()


def test_handle_conversation_command_current_empty():
    conv_manager = MagicMock()
    conv_manager.get_current_conversation.return_value = None
    
    res = handle_conversation_command("current conversation", conv_manager)
    assert res is True
    conv_manager.get_current_conversation.assert_called_once()


def test_print_help_table():
    registry = MagicMock()
    # Test that print_help_table runs without exceptions
    print_help_table(registry)


def test_print_skills_table():
    registry = SkillRegistry()
    meta = SkillMetadata(
        id="test_skill",
        name="Test",
        version="1.0.0",
        author="Tester",
        description="A skill for testing CLI layouts",
        category="TestCategory",
        commands=["run cli test"],
        capabilities=["cli-testing"]
    )
    registry.register(BaseSkill(meta, "/tmp/test"))
    
    # Test that print_skills_table runs with registered skill
    print_skills_table(registry)


def test_print_providers_table():
    model_service = MagicMock()
    model_service.registry.list_supported_models.return_value = ["mock-model"]
    model_service.registry.get_provider_for_model.return_value = "mock"
    
    print_providers_table(model_service)
    model_service.registry.list_supported_models.assert_called_once()


def test_handle_model_switch():
    model_service = MagicMock()
    model_service.registry.get_provider_for_model.return_value = "claude"
    
    handle_model_switch(model_service, "claude-3-5-sonnet")
    assert model_service._default_model == "claude-3-5-sonnet"
    model_service.registry.get_provider_for_model.assert_called_once_with("claude-3-5-sonnet")
