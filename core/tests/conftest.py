import os

import pytest


@pytest.fixture(autouse=True)
def setup_test_env():
    # Enforce test/development environment with fallback enabled during pytest runs
    # unless explicitly overridden by specific test parameters.
    old_env = os.environ.get("AIOS_ENV")
    old_fallback = os.environ.get("REDIS_FALLBACK_ENABLED")

    os.environ["AIOS_ENV"] = "test"
    os.environ["REDIS_FALLBACK_ENABLED"] = "true"

    yield

    if old_env is not None:
        os.environ["AIOS_ENV"] = old_env
    else:
        os.environ.pop("AIOS_ENV", None)

    if old_fallback is not None:
        os.environ["REDIS_FALLBACK_ENABLED"] = old_fallback
    else:
        os.environ.pop("REDIS_FALLBACK_ENABLED", None)
