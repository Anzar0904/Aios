class ServiceLifecycle:
    """
    Defines the contract for core service lifecycles.
    Each service transitions through these stages:
    initialize -> on_ready -> on_active -> teardown.
    """

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        # Wrap initialize
        orig_init = getattr(cls, "initialize", None)
        if orig_init:
            def wrapped_init(self, *args, **kwargs):
                if not getattr(self, "_lifecycle_initialized", False):
                    setattr(self, "_lifecycle_initialized", True)
                    orig_init(self, *args, **kwargs)
            cls.initialize = wrapped_init

        # Wrap on_ready
        orig_ready = getattr(cls, "on_ready", None)
        if orig_ready:
            def wrapped_ready(self, *args, **kwargs):
                if not getattr(self, "_lifecycle_ready", False):
                    setattr(self, "_lifecycle_ready", True)
                    orig_ready(self, *args, **kwargs)
            cls.on_ready = wrapped_ready

        # Wrap teardown
        orig_teardown = getattr(cls, "teardown", None)
        if orig_teardown:
            def wrapped_teardown(self, *args, **kwargs):
                if not getattr(self, "_lifecycle_teardown", False):
                    setattr(self, "_lifecycle_teardown", True)
                    orig_teardown(self, *args, **kwargs)
            cls.teardown = wrapped_teardown

    def initialize(self) -> None:
        """Called during service registration to initialize resources."""
        if not getattr(self, "_lifecycle_initialized", False):
            setattr(self, "_lifecycle_initialized", True)

    def on_ready(self) -> None:
        """Called when all services are registered and the system is ready to start."""
        if not getattr(self, "_lifecycle_ready", False):
            setattr(self, "_lifecycle_ready", True)

    def on_active(self) -> None:
        """Called when the service is transitioning to active session state."""
        pass

    def teardown(self) -> None:
        """Called during graceful shutdown to clean up resources."""
        if not getattr(self, "_lifecycle_teardown", False):
            setattr(self, "_lifecycle_teardown", True)
