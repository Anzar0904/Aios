class ServiceLifecycle:
    """
    Defines the contract for core service lifecycles.
    Each service transitions through these stages:
    initialize -> on_ready -> on_active -> teardown.
    """

    def initialize(self) -> None:
        """Called during service registration to initialize resources."""
        pass

    def on_ready(self) -> None:
        """Called when all services are registered and the system is ready to start."""
        pass

    def on_active(self) -> None:
        """Called when the service is transitioning to active session state."""
        pass

    def teardown(self) -> None:
        """Called during graceful shutdown to clean up resources."""
        pass
