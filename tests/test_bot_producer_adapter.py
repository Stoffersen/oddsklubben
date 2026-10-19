import tempfile
import unittest
from pathlib import Path
from src.bot_ledger_sqlite import SQLiteLedger
from src.bot_producer_adapter import apply

LOCK={"schema_version":1,"event_type":"lock","coupon_id":"c1","bet_id":"b1",
"stake_kr":20,"fixture_id":"provider:123","locked_at_utc":"2026-10-19T12:00:00Z",
"kickoff_utc":"2026-10-20T12:00:00Z"}
SETTLE={"schema_version":1,"event_type":"settle","settlement_id":"s1","bet_id":"b1",
"result":"won","return_kr":30,"source":"verified",
"observed_at_utc":"2026-10-20T16:00:00Z"}

class AdapterTests(unittest.TestCase):
    def test_persistent_replay(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"ledger.sqlite"
            db=SQLiteLedger(p)
            self.assertTrue(apply(db, LOCK))
            self.assertTrue(apply(db, SETTLE))
            db.close()
            db=SQLiteLedger(p)
            self.assertFalse(apply(db, LOCK))
            self.assertFalse(apply(db, SETTLE))
            self.assertEqual(db.totals()["profit_ore"],1000)
            db.close()

    def test_deny_untrusted_recommendation(self):
        with tempfile.TemporaryDirectory() as tmp:
            db=SQLiteLedger(Path(tmp)/"x.db")
            with self.assertRaises(ValueError):
                apply(db,{"schema_version":1,"event_type":"recommendation"})
            db.close()

    def test_pre_kickoff_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            db=SQLiteLedger(Path(tmp)/"x.db")
            bad=dict(LOCK,locked_at_utc="2026-10-21T12:00:00Z")
            with self.assertRaises(ValueError):
                apply(db,bad)
            bad=dict(LOCK,locked_at_utc="2026-10-19T12:00:00")
            with self.assertRaises(ValueError):
                apply(db,bad)
            self.assertEqual(db.totals()["stake_ore"],0)
            db.close()

    def test_correction_requires_reason(self):
        with tempfile.TemporaryDirectory() as tmp:
            db=SQLiteLedger(Path(tmp)/"x.db")
            apply(db,LOCK)
            with self.assertRaises(ValueError):
                apply(db,dict(SETTLE,revision_of="s0"))
            db.close()
