"""
bootstrap_modules/agents.py

Constructs, registers, and wires AI Agents, Agent Runtime, registries, managers,
and the Mission Engine.
"""

from __future__ import annotations

import logging

# Interface imports
from aios.services.agent import AgentRegistry, AgentRuntimeService, LocalAgentManager

# Concrete agent and runtime imports
from aios.services.agent_impl import CareerAgent, DeveloperAgent, LocalAgentRuntime, MockAgent
from aios.services.mission import MissionEngine
from aios.services.mission_impl import LocalMissionEngine

logger = logging.getLogger(__name__)


def bootstrap_agents(
    registry,  # noqa: ANN001
    event_bus,  # noqa: ANN001
    memory_service,  # noqa: ANN001
    context_service,  # noqa: ANN001
    tool_service,  # noqa: ANN001
    model_service,  # noqa: ANN001
    github_service,  # noqa: ANN001
    career_os,  # noqa: ANN001
    daily_os,  # noqa: ANN001
    orchestrator_service,  # noqa: ANN001
) -> dict:
    """Wires and registers agents, runtime services, and mission engine."""
    agent_registry = AgentRegistry()
    agent_manager = LocalAgentManager(agent_registry, orchestrator_service)
    agent_manager.initialize()

    # Instantiate agents
    career_agent = CareerAgent(
        memory_service,
        context_service,
        tool_service,
        model_service,
        github_service,
        career_os,
        daily_os,
    )
    developer_agent = DeveloperAgent(memory_service, context_service, tool_service, model_service)
    mock_agent = MockAgent(memory_service, context_service, tool_service)

    # Register to AgentRegistry
    agent_registry.register(career_agent)
    agent_registry.register(developer_agent)
    agent_registry.register(mock_agent)

    # Instantiate Agent Runtime
    agent_runtime = LocalAgentRuntime(
        event_bus=event_bus,
        memory_service=memory_service,
        context_service=context_service,
        tool_service=tool_service,
        model_service=model_service,
    )

    mission_engine = LocalMissionEngine(agent_runtime, registry=registry)
    mission_engine.initialize()

    # Register agents to the Agent Runtime
    agent_runtime.register_agent(mock_agent)
    agent_runtime.register_agent(developer_agent)
    agent_runtime.register_agent(career_agent)

    # Register in registry
    registry.register(AgentRuntimeService, agent_runtime)
    registry.register(AgentRegistry, agent_registry)
    registry.register(LocalAgentManager, agent_manager)
    registry.register(MissionEngine, mission_engine)

    return {
        "agent_registry": agent_registry,
        "agent_manager": agent_manager,
        "agent_runtime": agent_runtime,
        "mission_engine": mission_engine,
        "career_agent": career_agent,
        "developer_agent": developer_agent,
        "mock_agent": mock_agent,
    }
