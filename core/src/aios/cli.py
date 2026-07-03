import signal
import sys
from pathlib import Path

from aios.kernel import Kernel
from aios.services.intent import IntentResolverService


def main() -> None:
    """CLI entry point for aios / atlas."""
    print("Initializing AI OS...")

    # Path to config file relative to standard repository structure
    config_path = Path("config/config.toml")
    kernel = Kernel(config_path)

    # Set up signal handler for graceful shutdown on SIGINT/SIGTERM
    def handle_shutdown(signum, frame):
        print("\nShutting down gracefully...")
        kernel.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    try:
        kernel.boot()
        print("Runtime Ready.")

        # Simple interactive loop
        while True:
            try:
                # Print prompt and read line
                user_input = input("> ").strip()
                if not user_input:
                    continue

                # Resolve natural language input to structured intent
                intent_resolver = kernel.registry.get(IntentResolverService)
                intent = intent_resolver.resolve(user_input)
                print(
                    f"Resolved Intent: {intent.intent_type.name}.{intent.action} "
                    f"(Confidence: {intent.confidence:.2f})"
                )

                # Dispatch structured intent to Kernel for execution
                result = kernel.execute_intent(intent)
                print(result.message)

                # Break CLI loop if session end is requested
                if intent.intent_type.name == "SESSION" and intent.action == "End":
                    break
            except EOFError:
                # Handle Ctrl+D
                break
            except KeyboardInterrupt:
                # Handle Ctrl+C inside input
                print()
                break

    finally:
        print("Shutting down gracefully...")
        kernel.shutdown()


if __name__ == "__main__":
    main()
