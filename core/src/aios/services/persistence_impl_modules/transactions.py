"""
persistence_impl_modules/transactions.py

Manages transaction stacks and savepoints.
"""

from __future__ import annotations

import logging
from typing import List

from aios.services.persistence import DatabaseTransport, TransportTransaction

logger = logging.getLogger(__name__)


class TransactionStackManager:
    """Manages transactional savepoints stacks on top of raw transport transactions."""

    def __init__(self, transport: DatabaseTransport) -> None:
        self.transport = transport
        self.tx_stack: List[TransportTransaction] = []

    def begin(self) -> None:
        if len(self.tx_stack) == 0:
            tx = self.transport.begin_transaction()
            self.tx_stack.append(tx)
        else:
            savepoint_name = f"sp_{len(self.tx_stack)}"
            self.transport.execute(f"SAVEPOINT {savepoint_name}")

            class SavepointTransaction(TransportTransaction):
                def __init__(self, transport: DatabaseTransport, name: str) -> None:
                    self.transport = transport
                    self.name = name

                def commit(self) -> None:
                    self.transport.execute(f"RELEASE SAVEPOINT {self.name}")

                def rollback(self) -> None:
                    self.transport.execute(f"ROLLBACK TO SAVEPOINT {self.name}")

            self.tx_stack.append(SavepointTransaction(self.transport, savepoint_name))

    def commit(self) -> None:
        if not self.tx_stack:
            raise RuntimeError("No active transaction to commit")
        tx = self.tx_stack.pop()
        tx.commit()

    def rollback(self) -> None:
        if not self.tx_stack:
            raise RuntimeError("No active transaction to rollback")
        tx = self.tx_stack.pop()
        try:
            tx.rollback()
        except Exception:
            pass
