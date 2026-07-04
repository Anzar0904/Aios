import logging
from typing import Any, Callable, Dict, List, Optional

from aios.services.base import ServiceLifecycle
from aios.services.command.metadata import CommandCategory, CommandMetadata

logger = logging.getLogger(__name__)

class CommandRegistry(ServiceLifecycle):
    def __init__(self) -> None:
        self._commands: Dict[str, CommandMetadata] = {}
        self._handlers: Dict[str, Callable[[Any], Any]] = {}

    def initialize(self) -> None:
        pass

    def register_command(self, metadata: CommandMetadata, handler: Callable[[Any], Any]) -> None:
        self._commands[metadata.name.lower()] = metadata
        self._handlers[metadata.name.lower()] = handler
        logger.info(f"Registered command: {metadata.name}")

    def unregister_command(self, name: str) -> None:
        name_lower = name.lower()
        if name_lower in self._commands:
            del self._commands[name_lower]
        if name_lower in self._handlers:
            del self._handlers[name_lower]
        logger.info(f"Unregistered command: {name}")

    def get_command(self, name: str) -> Optional[CommandMetadata]:
        return self._commands.get(name.lower())

    def get_handler(self, name: str) -> Optional[Callable[[Any], Any]]:
        return self._handlers.get(name.lower())

    def list_commands(self, category: Optional[CommandCategory] = None) -> List[CommandMetadata]:
        cmds = list(self._commands.values())
        if category:
            cmds = [c for c in cmds if c.category == category]
        return sorted(cmds, key=lambda x: x.name)

    def search_commands(self, keyword: str) -> List[CommandMetadata]:
        keyword = keyword.lower()
        results = []
        for cmd in self._commands.values():
            if (keyword in cmd.name.lower() or 
                keyword in cmd.description.lower() or 
                keyword in cmd.category.value.lower()):
                results.append(cmd)
        return sorted(results, key=lambda x: x.name)
