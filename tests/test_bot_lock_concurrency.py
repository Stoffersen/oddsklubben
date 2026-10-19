"""Concurrency and lost-ack regression checks for the isolated SQLite ledger."""
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier
from src.bot_ledger_sqlite import SQLiteLedger

ARGS=("request-1","coupon-1","bet-1",20,"fixture-1","2026-10-20T12:00:00Z","2026-10-19T12:00:00Z")

class LockConcurrencyTests(unittest.TestCase):
    def test_two_independent_connections_same_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"ledger.sqlite"
            barrier=Barrier(2)
            def run():
                db=SQLiteLedger(path)
                try:
                    barrier.wait(timeout=10)
                    return db.lock_request(*ARGS)
                finally:
                    db.close()
            with ThreadPoolExecutor(max_workers=2) as pool:
                outcomes=list(pool.map(lambda _:run(),range(2)))
            self.assertEqual(sum(x["created"] for x in outcomes),1)
            self.assertEqual({x["bet_id"] for x in outcomes},{"bet-1"})
            db=SQLiteLedger(path)
            self.assertEqual(db.totals()["stake_ore"],2000)
            self.assertEqual(db.db.execute("SELECT COUNT(*) FROM lock_requests").fetchone()[0],1)
            db.close()

    def test_lost_ack_and_restart_returns_same_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"ledger.sqlite"
            db=SQLiteLedger(path)
            db.lock_request(*ARGS)
            db.close()
            db=SQLiteLedger(path)
            receipt=db.lock_request(*ARGS)
            self.assertEqual(receipt,{"created":False,"coupon_id":"coupon-1","bet_id":"bet-1"})
            self.assertEqual(db.totals()["stake_ore"],2000)
            db.close()

    def test_concurrent_conflicting_payload_same_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"ledger.sqlite"
            db=SQLiteLedger(path)
            db.lock_request(*ARGS)
            db.close()
            db=SQLiteLedger(path)
            with self.assertRaises(ValueError):
                db.lock_request(*ARGS[:3],21,*ARGS[4:])
            self.assertEqual(db.db.execute("SELECT COUNT(*) FROM bets").fetchone()[0],1)
            db.close()
