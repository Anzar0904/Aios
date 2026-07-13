from typing import Dict, List, Type, TypeVar

from aios.services.base import ServiceLifecycle

T = TypeVar("T", bound=ServiceLifecycle)


class ServiceRegistry:
    """Manages core service registration and lookup."""

    _global_registry = None

    def __init__(self) -> None:
        self._services: Dict[Type[ServiceLifecycle], ServiceLifecycle] = {}
        ServiceRegistry._global_registry = self

    def register(self, service_type: Type[T], instance: T) -> None:
        """Registers a service instance under its interface class."""
        if not issubclass(service_type, ServiceLifecycle):
            raise TypeError(
                f"Registered type {service_type.__name__} must inherit from ServiceLifecycle"
            )
        if not isinstance(instance, service_type):
            raise TypeError(f"Instance must be an implementation of {service_type.__name__}")
        if service_type in self._services:
            raise ValueError(f"Service {service_type.__name__} is already registered")
        self._services[service_type] = instance

    def get(self, service_type: Type[T]) -> T:
        """Retrieves a registered service instance."""
        service = self._services.get(service_type)
        if service is None:
            raise KeyError(f"Service {service_type.__name__} is not registered")
        return service  # type: ignore

    def get_all(self) -> List[ServiceLifecycle]:
        """Returns all registered service instances."""
        return list(self._services.values())
