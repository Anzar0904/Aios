import signal
import sys
from pathlib import Path

from aios.kernel import Kernel


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
                if user_input.lower() in ("exit", "quit"):
                    break
                elif not user_input:
                    continue
                else:
                    # MVP requirement constraint: No business logic implemented.
                    print("Interactive command execution not implemented in bootstrap.")
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
