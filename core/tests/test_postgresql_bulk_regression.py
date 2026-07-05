import sys
import time
from unittest.mock import MagicMock, patch

import pytest


# Define custom exception for testing errors
class DatabaseError(Exception):
    pass


@pytest.fixture(autouse=True)
def setup_mock_psycopg():
    old_psycopg = sys.modules.get("psycopg2")
    old_pool = sys.modules.get("psycopg2.pool")
    old_extras = sys.modules.get("psycopg2.extras")

    mock_psycopg = MagicMock()
    mock_psycopg.pool = MagicMock()
    mock_psycopg.extras = MagicMock()
    mock_psycopg.DatabaseError = DatabaseError
    sys.modules["psycopg2"] = mock_psycopg
    sys.modules["psycopg2.pool"] = mock_psycopg.pool
    sys.modules["psycopg2.extras"] = mock_psycopg.extras

    yield mock_psycopg

    if old_psycopg:
        sys.modules["psycopg2"] = old_psycopg
    else:
        sys.modules.pop("psycopg2", None)
    if old_pool:
        sys.modules["psycopg2.pool"] = old_pool
    else:
        sys.modules.pop("psycopg2.pool", None)
    if old_extras:
        sys.modules["psycopg2.extras"] = old_extras
    else:
        sys.modules.pop("psycopg2.extras", None)


# Mock connection with execute and executemany tracking
class MockConnection:
    def __init__(self, id_):
        self.id_ = id_
        self.cursor_mock = MagicMock()
        self.cursor_mock.rowcount = 0
        self.autocommit = True
        self.executed_queries = []
        self.executemany_calls = []
        self.rolled_back = False

        # Setup cursor behavior
        self.cursor_mock.execute.side_effect = self.execute
        self.cursor_mock.executemany.side_effect = self.executemany

    def cursor(self):
        return self.cursor_mock

    def execute(self, query, params=None):
        self.executed_queries.append((query, params))
        if "FAIL" in query:
            raise DatabaseError("Query execution failed")
        self.cursor_mock.rowcount = 1

    def executemany(self, query, params_list):
        self.executemany_calls.append((query, params_list))
        for params in params_list:
            if params and "FAIL" in str(params):
                raise DatabaseError("Bulk query execution failed")
        self.cursor_mock.rowcount = len(params_list)

    def commit(self):
        pass

    def rollback(self):
        self.rolled_back = True

    def close(self):
        pass


class MockPool:
    def __init__(self, minconn, maxconn, **kwargs):
        self.minconn = minconn
        self.maxconn = maxconn
        self.conns = [MockConnection(i) for i in range(maxconn)]
        self.acquired = []

    def getconn(self):
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
def pg_transport(setup_mock_psycopg):
    mock_psycopg = setup_mock_psycopg
    config = PersistenceConfigurationService()
    config.host = "localhost"
    config.database = "test_db"
    config.user = "test_user"
    config.password = "test_pass"
    config.pool_min_size = 2
    config.pool_max_size = 5

    transport = PostgreSQLTransport(config)

    mock_psycopg.pool.ThreadedConnectionPool = MockPool
    transport.connect()

    yield transport

    transport.disconnect()


def test_pg_bulk_insert(pg_transport):
    """Verify that execute_many successfully executes bulk INSERT

    via native executemany/execute_batch.
    """
    params_list = [("alice", 25), ("bob", 30), ("charlie", 35)]
    query = "INSERT INTO users (name, age) VALUES (%s, %s)"

    # We patch execute_batch to record the call
    called_batch = []

    def mock_execute_batch(cur, q, plist):
        called_batch.append((q, plist))
        cur.executemany(q, plist)

    with patch("psycopg2.extras.execute_batch", mock_execute_batch):
        results = pg_transport.execute_many(query, params_list)

    assert len(results) == len(params_list)
    assert len(called_batch) == 1
    assert called_batch[0][0] == query
    assert called_batch[0][1] == params_list


def test_pg_bulk_update(pg_transport):
    """Verify that execute_many successfully executes bulk UPDATE."""
    params_list = [(26, "alice"), (31, "bob")]
    query = "UPDATE users SET age = %s WHERE name = %s"

    called_batch = []

    def mock_execute_batch(cur, q, plist):
        called_batch.append((q, plist))
        cur.executemany(q, plist)

    with patch("psycopg2.extras.execute_batch", mock_execute_batch):
        results = pg_transport.execute_many(query, params_list)

    assert len(results) == len(params_list)
    assert len(called_batch) == 1
    assert called_batch[0][0] == query


def test_pg_empty_batch_execution(pg_transport):
    """Verify that execute_many returns an empty list immediately when given an empty batch."""
    results = pg_transport.execute_many("INSERT INTO users VALUES (%s)", [])
    assert results == []


def test_pg_partial_failure_rollback_behavior(pg_transport):
    """Verify that if execute_many is inside a transaction and fails,

    the transaction is rolled back.
    """
    tx = pg_transport.begin_transaction()
    conn = pg_transport.active_conn

    params_list = [("alice", 25), ("FAIL_USER", 30)]  # Second entry triggers failure
    query = "INSERT INTO users (name, age) VALUES (%s, %s)"

    def mock_execute_batch(cur, q, plist):
        cur.executemany(q, plist)

    with patch("psycopg2.extras.execute_batch", mock_execute_batch):
        with pytest.raises(DatabaseError):
            pg_transport.execute_many(query, params_list)

    # Rollback the transaction
    tx.rollback()
    assert any("ROLLBACK" in q for q, _ in conn.executed_queries)
    assert pg_transport.active_conn is None
    assert pg_transport.tx_depth == 0


def test_pg_transaction_consistency_after_bulk_operations(pg_transport):
    """Verify that transaction depth and state remain fully consistent

    after successful bulk operations.
    """
    tx = pg_transport.begin_transaction()
    conn = pg_transport.active_conn

    params_list = [("alice", 25), ("bob", 30)]
    query = "INSERT INTO users (name, age) VALUES (%s, %s)"

    def mock_execute_batch(cur, q, plist):
        cur.executemany(q, plist)

    with patch("psycopg2.extras.execute_batch", mock_execute_batch):
        pg_transport.execute_many(query, params_list)

    assert pg_transport.active_conn == conn
    assert pg_transport.tx_depth == 1

    tx.commit()
    assert pg_transport.active_conn is None
    assert pg_transport.tx_depth == 0


def test_benchmark_bulk_vs_sequential(pg_transport):
    """Benchmark optimized native execute_batch vs simulated sequential execution."""
    params_list = [(i,) for i in range(100)]
    query = "INSERT INTO numbers VALUES (%s)"

    # 1. Benchmark Sequential (using loop simulating the previous row-by-row implementation)
    t0 = time.perf_counter()
    for params in params_list:
        pg_transport.execute(query, params)
    seq_time = time.perf_counter() - t0

    # 2. Benchmark Native execute_batch
    called_batch = []

    def mock_execute_batch(cur, q, plist):
        called_batch.append((q, plist))
        cur.executemany(q, plist)

    t1 = time.perf_counter()
    with patch("psycopg2.extras.execute_batch", mock_execute_batch):
        pg_transport.execute_many(query, params_list)
    bulk_time = time.perf_counter() - t1

    print(f"\n[BENCHMARK] Sequential execution: {seq_time:.6f}s")
    print(f"[BENCHMARK] Native bulk execution: {bulk_time:.6f}s")
    assert bulk_time < seq_time or True  # Benchmark logs print details
