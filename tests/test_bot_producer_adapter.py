import tempfile
import unittest
from pathlib import Path
from src.bot_ledger_sqlite import SQLiteLedger
from src.bot_producer_adapter import apply

LOCK={"schema_version":1,"event_type":"lock","lock_request_id":"request-1","coupon_id":"c1","bet_id":"b1",
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
            self.assertTrue(apply(db, LOCK)["created"])
            self.assertTrue(apply(db, SETTLE))
            db.close()
            db=SQLiteLedger(p)
            self.assertFalse(apply(db, LOCK)["created"])
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

    def test_identity_fields_must_be_nonblank_strings(self):
        with tempfile.TemporaryDirectory() as tmp:
            db=SQLiteLedger(Path(tmp)/"x.db")
            for field in ("coupon_id","bet_id","fixture_id"):
                for value in ("   ",123,False):
                    with self.subTest(field=field,value=value), self.assertRaises(ValueError):
                        apply(db,dict(LOCK,**{field:value}))
            for field in ("settlement_id","bet_id","source"):
                with self.subTest(field=field), self.assertRaises(ValueError):
                    apply(db,dict(SETTLE,**{field:"   "}))
            self.assertEqual(db.totals()["stake_ore"],0)
            db.close()

    def test_result_provenance_survives_reopen(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"check.db"
            db=SQLiteLedger(path)
            apply(db,LOCK)
            apply(db,dict(SETTLE,source_ref="source-record"))
            db.close()
            db=SQLiteLedger(path)
            row=db.db.execute("SELECT source,source_ref FROM settlement_provenance").fetchone()
            self.assertEqual(row,("verified","source-record"))
            db.close()

    def test_request_key_conflict_and_replay_after_reopen(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"ledger.db"
            db=SQLiteLedger(path)
            first=apply(db,LOCK)
            db.close()
            db=SQLiteLedger(path)
            second=apply(db,LOCK)
            self.assertEqual(first["bet_id"],second["bet_id"])
            self.assertFalse(second["created"])
            with self.assertRaises(ValueError):
                apply(db,dict(LOCK,stake_kr=21))
            with self.assertRaises(ValueError):
                apply(db,dict(LOCK,lock_request_id="request-2"))
            self.assertEqual(db.totals()["stake_ore"],2000)
            db.close()
