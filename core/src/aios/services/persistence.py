import abc
from typing import Any, Dict, List, Optional, Type, TypeVar

from aios.services.base import ServiceLifecycle

T = TypeVar("T")


class PersistenceConfigurationService(ServiceLifecycle):
    """Configuration management service for the Persistence Platform."""

    def __init__(self) -> None:
        self.provider_name: str = "postgresql"
        self.host: str = "localhost"
        self.port: int = 5432
        self.database: str = "aios"
        self.user: str = "aios"
        self.password: str = ""
        self.connection_timeout: int = 5
        self.max_retries: int = 3
        self.pool_min_size: int = 2
        self.pool_max_size: int = 10
        self.retry_backoff: float = 1.0


class PersistenceProvider(abc.ABC):
    """Abstract interface for database engine providers."""

    @abc.abstractmethod
    def initialize(self, config: PersistenceConfigurationService) -> None:
        """Initializes the provider with configuration."""
        pass

    @abc.abstractmethod
    def connect(self) -> None:
        """Establishes connections/pools to the database."""
        pass

    @abc.abstractmethod
    def disconnect(self) -> None:
        """Closes all active connections and pools."""
        pass

    @abc.abstractmethod
    def execute(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Executes a SQL query and returns result rows."""
        pass

    @abc.abstractmethod
    def begin_transaction(self) -> None:
        """Begins a database transaction."""
        pass

    @abc.abstractmethod
    def commit_transaction(self) -> None:
        """Commits the active transaction."""
        pass

    @abc.abstractmethod
    def rollback_transaction(self) -> None:
        """Rollbacks the active transaction."""
        pass

    @abc.abstractmethod
    def is_connected(self) -> bool:
        """Returns True if the provider is successfully connected."""
        pass

    @abc.abstractmethod
    def get_metrics(self) -> Dict[str, Any]:
        """Returns connection and performance metrics."""
        pass


class PersistenceRegistry(ServiceLifecycle):
    """Registry managing pluggable persistence provider engines."""

    def __init__(self) -> None:
        self._providers: Dict[str, Type[PersistenceProvider]] = {}

    def register_provider(self, name: str, provider_cls: Type[PersistenceProvider]) -> None:
        """Registers a PersistenceProvider class class."""
        self._providers[name] = provider_cls

    def get_provider_class(self, name: str) -> Type[PersistenceProvider]:
        """Retrieves a registered provider class."""
        provider_cls = self._providers.get(name)
        if provider_cls is None:
            raise KeyError(f"Persistence provider '{name}' is not registered")
        return provider_cls


class RepositoryRegistry(ServiceLifecycle):
    """Registry capable of managing database repositories for future entities."""

    def __init__(self) -> None:
        self._repositories: Dict[str, Any] = {}

    def register_repository(self, name: str, repository_instance: Any) -> None:
        """Registers a concrete repository instance under a given name."""
        self._repositories[name] = repository_instance

    def get_repository(self, name: str) -> Any:
        """Retrieves a registered repository instance."""
        repo = self._repositories.get(name)
        if repo is None:
            raise KeyError(f"Repository '{name}' is not registered")
        return repo


class PersistenceService(ServiceLifecycle):
    """The central unified service that orchestrates all database interactions."""

    @abc.abstractmethod
    def execute(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Executes a database query."""
        pass

    @abc.abstractmethod
    def begin_transaction(self) -> None:
        """Starts a transaction scope."""
        pass

    @abc.abstractmethod
    def commit_transaction(self) -> None:
        """Commits the active transaction scope."""
        pass

    @abc.abstractmethod
    def rollback_transaction(self) -> None:
        """Rolls back the active transaction scope."""
        pass
