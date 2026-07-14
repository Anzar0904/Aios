"""Phase 11: Personal Intelligence — Knowledge Graph Bridge.

Bridges Personal Goals, Habits, Tasks, Meetings, and Reminders into the Universal
Knowledge Graph using SUPPORTS, DEPENDS_ON, and TRACKS links.
"""

from __future__ import annotations

import logging

from aios.services.graph import EntityType
from aios.services.graph_query import GraphQueryEngine
from aios.services.personal import CalendarEvent, Habit, PersonalGoal, PersonalTask

logger = logging.getLogger(__name__)


class PersonalGraphBridge:
    """Synchronizes personal goals, tasks, habits, and events to the Knowledge Graph."""

    def __init__(self, graph_engine: GraphQueryEngine) -> None:
        self._engine = graph_engine

    def sync_goal(self, goal: PersonalGoal) -> str:
        """Create or update a GOAL node in the graph."""
        try:
            props = {
                "timeframe": goal.timeframe,
                "category": goal.category,
                "status": goal.status,
            }
            entity = self._engine.ensure_entity(EntityType.GOAL, goal.title, props)
            return entity.entity_id
        except Exception as exc:
            logger.warning("Failed to sync goal to graph: %s", exc)
            return ""

    def sync_task(self, task: PersonalTask) -> str:
        """Create or update a TASK node in the graph."""
        try:
            props = {
                "category": task.category,
                "status": task.status,
            }
            entity = self._engine.ensure_entity(EntityType.TASK, task.title, props)
            return entity.entity_id
        except Exception as exc:
            logger.warning("Failed to sync task to graph: %s", exc)
            return ""

    def sync_habit(self, habit: Habit) -> str:
        """Create or update a HABIT node in the graph."""
        try:
            props = {
                "frequency": habit.frequency,
                "streak": habit.streak,
            }
            entity = self._engine.ensure_entity(EntityType.HABIT, habit.name, props)
            return entity.entity_id
        except Exception as exc:
            logger.warning("Failed to sync habit to graph: %s", exc)
            return ""

    def sync_event(self, event: CalendarEvent) -> str:
        """Create or update a MEETING node in the graph."""
        try:
            props = {
                "category": event.category,
            }
            entity = self._engine.ensure_entity(EntityType.MEETING, event.title, props)
            return entity.entity_id
        except Exception as exc:
            logger.warning("Failed to sync calendar event to graph: %s", exc)
            return ""
