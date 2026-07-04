import abc
import os
from typing import Any, Dict, List, Optional, Type, TypeVar

from aios.services.base import ServiceLifecycle

T = TypeVar("T")


class PersistenceConfigurationService(ServiceLifecycle):
    """Configuration management service for the Persistence Platform."""

    def __init__(self) -> None:
        self.provider_name: str = "postgresql"
        # Discovery of standard environment variables
        self.host: str = os.getenv("POSTGRES_HOST", "")
        self.port: int = int(os.getenv("POSTGRES_PORT", "5432")) if os.getenv("POSTGRES_PORT") else 5432
        self.database: str = os.getenv("POSTGRES_DATABASE", "")
        self.user: str = os.getenv("POSTGRES_USER", "")
        self.password: str = os.getenv("POSTGRES_PASSWORD", "")
        self.sslmode: str = os.getenv("POSTGRES_SSLMODE", "prefer")
        self.connection_timeout: int = int(os.getenv("POSTGRES_CONNECT_TIMEOUT", "5")) if os.getenv("POSTGRES_CONNECT_TIMEOUT") else 5
        self.max_retries: int = 3
        self.pool_min_size: int = 2
        self.pool_max_size: int = 10
        self.retry_backoff: float = 1.0


class TransportResult:
    """Wrapper encapsulating query execution results, affected rows, and inserted keys."""

    def __init__(
        self,
        rows: List[Dict[str, Any]],
        last_inserted_id: Optional[Any] = None,
        rows_affected: int = 0
    ) -> None:
        self.rows = rows
        self.last_inserted_id = last_inserted_id
        self.rows_affected = rows_affected


class TransportCapabilities:
    """Features and capabilities supported by the active database transport."""

    def __init__(self, support_savepoints: bool = True, support_json: bool = True) -> None:
        self.support_savepoints = support_savepoints
        self.support_json = support_json


class TransportHealth:
    """Runtime health status representing connection state, latency, and diagnostics."""

    def __init__(
        self,
        is_alive: bool,
        latency_ms: float,
        error_message: Optional[str] = None
    ) -> None:
        self.is_alive = is_alive
        self.latency_ms = latency_ms
        self.error_message = error_message


class TransportConnection(abc.ABC):
    """Abstract database connection instance managed by a DatabaseTransport."""

    @abc.abstractmethod
    def close(self) -> None:
        """Closes the connection instance."""
        pass

    @abc.abstractmethod
    def execute(self, query: str, params: Optional[tuple] = None) -> TransportResult:
        """Executes a query on the connection."""
        pass


class TransportTransaction(abc.ABC):
    """Abstract active database transaction scope."""

    @abc.abstractmethod
    def commit(self) -> None:
        """Commits the transaction."""
        pass

    @abc.abstractmethod
    def rollback(self) -> None:
        """Rollbacks the transaction."""
        pass


class DatabaseTransport(abc.ABC):
    """Abstract interface exposing the low-level database transport engine."""

    def __init__(self, config: PersistenceConfigurationService) -> None:
        self.config = config

    @abc.abstractmethod
    def connect(self) -> None:
        """Establishes connections or pool resources."""
        pass

    @abc.abstractmethod
    def disconnect(self) -> None:
        """Tears down all connections or pools."""
        pass

    @abc.abstractmethod
    def execute(self, query: str, params: Optional[tuple] = None) -> TransportResult:
        """Executes a SQL query and returns result rows."""
        pass

    @abc.abstractmethod
    def execute_many(self, query: str, params_list: List[tuple]) -> List[TransportResult]:
        """Executes a bulk batch of SQL queries."""
        pass

    @abc.abstractmethod
    def begin_transaction(self) -> TransportTransaction:
        """Begins a database transaction scope."""
        pass

    @abc.abstractmethod
    def health(self) -> TransportHealth:
        """Returns health indicators."""
        pass

    @abc.abstractmethod
    def capabilities(self) -> TransportCapabilities:
        """Returns provider features capabilities."""
        pass

    @abc.abstractmethod
    def validate_configuration(self) -> List[str]:
        """Validates configuration parameters and returns error descriptions."""
        pass


class TransportFactory:
    """Factory to discover, validate, and instantiate database transports."""

    def __init__(self) -> None:
        self._transports: Dict[str, Type[DatabaseTransport]] = {}

    def register_transport(self, name: str, transport_cls: Type[DatabaseTransport]) -> None:
        """Registers a DatabaseTransport class under a given name."""
        self._transports[name] = transport_cls

    def create_transport(self, name: str, config: PersistenceConfigurationService) -> DatabaseTransport:
        """Creates an instance of the target DatabaseTransport class."""
        transport_cls = self._transports.get(name)
        if transport_cls is None:
            raise KeyError(f"Database transport '{name}' is not registered.")
        return transport_cls(config)


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
        """Registers a PersistenceProvider class."""
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
