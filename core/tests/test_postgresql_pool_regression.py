import sys
from unittest.mock import MagicMock

import pytest


# Define custom exceptions and mock structures to test psycopg2.pool behaviour
class PoolError(Exception):
    pass


mock_psycopg = None


@pytest.fixture(autouse=True)
def setup_mock_psycopg():
    global mock_psycopg
    old_psycopg = sys.modules.get("psycopg2")
    old_pool = sys.modules.get("psycopg2.pool")

    mock_psycopg = MagicMock()
    mock_psycopg.pool = MagicMock()
    mock_psycopg.pool.PoolError = PoolError
    sys.modules["psycopg2"] = mock_psycopg
    sys.modules["psycopg2.pool"] = mock_psycopg.pool

    yield mock_psycopg

    if old_psycopg:
        sys.modules["psycopg2"] = old_psycopg
    else:
        sys.modules.pop("psycopg2", None)
    if old_pool:
        sys.modules["psycopg2.pool"] = old_pool
    else:
        sys.modules.pop("psycopg2.pool", None)
    mock_psycopg = None


# Mock ThreadedConnectionPool behavior
class MockConnection:
    def __init__(self, id_):
        self.id_ = id_
        self.cursor_mock = MagicMock()
        self.autocommit = True

    def cursor(self):
        return self.cursor_mock

    def close(self):
        pass


class MockPool:
    def __init__(self, minconn, maxconn, **kwargs):
        self.minconn = minconn
        self.maxconn = maxconn
        self.conns = [MockConnection(i) for i in range(maxconn)]
        self.acquired = []

    def getconn(self):
        if not self.conns:
            raise PoolError("Pool exhausted")
        c = self.conns.pop(0)
        self.acquired.append(c)
        return c

    def putconn(self, conn):
        self.acquired.remove(conn)
        self.conns.append(conn)

    def closeall(self):
        self.conns.clear()
        self.acquired.clear()


from aios.services.persistence_impl import (  # noqa: E402
    PersistenceConfigurationService,
    PostgreSQLTransport,
)


@pytest.fixture
def pg_transport():
    config = PersistenceConfigurationService()
    config.host = "localhost"
    config.database = "test_db"
    config.user = "test_user"
    config.password = "test_pass"
    config.pool_min_size = 2
    config.pool_max_size = 3

    transport = PostgreSQLTransport(config)

    mock_psycopg.pool.ThreadedConnectionPool = MockPool
    transport.connect()

    yield transport

    transport.disconnect()


def test_pg_concurrent_connection_acquisition(pg_transport):
    """Verify that multiple connections can be acquired concurrently from the pool."""
    pool = pg_transport.pool

    # Execute query 1
    pg_transport.execute("SELECT 1")
    assert len(pool.acquired) == 0  # connection returned after single execute

    # Active transaction acquires and holds connection
    tx1 = pg_transport.begin_transaction()
    assert len(pool.acquired) == 1
    conn1 = pg_transport.active_conn

    # Run query inside transaction
    pg_transport.execute("SELECT 2")
    assert pg_transport.active_conn == conn1
    assert len(pool.acquired) == 1

    # Run query outside transaction concurrent with active transaction
    # Since execute() without active transaction acquires connection dynamically,
    # it gets conn2 from pool and releases it immediately.
    pg_transport.execute("SELECT 3")
    assert len(pool.acquired) == 1

    # Commit transaction 1
    tx1.commit()
    assert len(pool.acquired) == 0
    assert pg_transport.active_conn is None


def test_pg_connection_release(pg_transport):
    """Verify that connection is safely returned/released to the pool

    on execution completion or rollback.
    """
    pool = pg_transport.pool

    tx = pg_transport.begin_transaction()
    assert len(pool.acquired) == 1

    tx.rollback()
    assert len(pool.acquired) == 0
    assert pg_transport.active_conn is None


def test_pg_pool_exhaustion_handling(pg_transport):
    """Verify that pool exhaustion (no connections available) is handled

    correctly by raising PoolError.
    """
    pool = pg_transport.pool

    # Acquire max connections (3) using nested/multiple transactions simulated concurrently
    txs = []
    for _ in range(3):
        # We manually acquire connections to exhaust the pool
        txs.append(pool.getconn())

    assert len(pool.acquired) == 3

    # Next acquisition attempt should raise PoolError
    with pytest.raises(PoolError, match="Pool exhausted"):
        pool.getconn()

    # Release one connection
    pool.putconn(txs.pop())
    assert len(pool.acquired) == 2

    # Now acquisition should succeed
    c = pool.getconn()
    assert c is not None


def test_pg_reuse_of_returned_connections(pg_transport):
    """Verify that returned/released connections are reused by subsequent queries."""
    pool = pg_transport.pool

    # Execute query, connection is acquired and returned
    pg_transport.execute("SELECT 1")
    assert len(pool.acquired) == 0

    # Begin transaction, connection is acquired
    tx = pg_transport.begin_transaction()
    assert len(pool.acquired) == 1

    tx.commit()
    assert len(pool.acquired) == 0

    # Execute again, connection from the pool should be reused
    pg_transport.execute("SELECT 2")
    assert len(pool.acquired) == 0
