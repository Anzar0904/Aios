class ServiceLifecycle:
    """
    Defines the contract for core service lifecycles.
    Each service transitions through these stages:
    initialize -> start -> ready -> shutdown.
    """

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        # Wrap initialize
        orig_init = getattr(cls, "initialize", None)
        if orig_init:

            def wrapped_init(self, *args, **kwargs):
                if not getattr(self, "_lifecycle_initialized", False):
                    self._lifecycle_initialized = True
                    orig_init(self, *args, **kwargs)

            cls.initialize = wrapped_init

        # Wrap start
        orig_start = getattr(cls, "start", None)
        if orig_start:

            def wrapped_start(self, *args, **kwargs):
                if not getattr(self, "_lifecycle_start", False):
                    self._lifecycle_start = True
                    orig_start(self, *args, **kwargs)

            cls.start = wrapped_start

        # Wrap shutdown
        orig_shutdown = getattr(cls, "shutdown", None)
        if orig_shutdown:

            def wrapped_shutdown(self, *args, **kwargs):
                if not getattr(self, "_lifecycle_shutdown", False):
                    self._lifecycle_shutdown = True
                    orig_shutdown(self, *args, **kwargs)

            cls.shutdown = wrapped_shutdown

    def initialize(self) -> None:
        if not getattr(self, "_lifecycle_initialized", False):
            self._lifecycle_initialized = True

    def start(self) -> None:
        if not getattr(self, "_lifecycle_start", False):
            self._lifecycle_start = True

    def ready(self) -> bool:
        return True

    def shutdown(self) -> None:
        if not getattr(self, "_lifecycle_shutdown", False):
            self._lifecycle_shutdown = True
