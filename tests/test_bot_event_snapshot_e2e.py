import tempfile
import unittest
from pathlib import Path
from src.bot_ledger_sqlite import SQLiteLedger
from src.bot_producer_adapter import apply
from src.bot_snapshot_projection import read_snapshot, compare_to_legacy

LOCK={"schema_version":1,"event_type":"lock","lock_request_id":"req-1",
"coupon_id":"coupon-1","bet_id":"bet-1","stake_kr":80,
"fixture_id":"provider:fixture-1","locked_at_utc":"2026-10-19T10:00:00Z",
"kickoff_utc":"2026-10-20T10:00:00Z"}
RESULT={"schema_version":1,"event_type":"settle","settlement_id":"result-1",
"bet_id":"bet-1","result":"won","return_kr":95.6,"source":"verified-fixture",
"source_ref":"fixture-source-1","observed_at_utc":"2026-10-20T17:00:00Z"}
LEGACY={"stake_kr":80,"return_kr":95.6,"profit_kr":15.6}

class PipelineAcceptanceTests(unittest.TestCase):
    def test_events_to_persistent_snapshot_to_comparison(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"ledger.sqlite"
            db=SQLiteLedger(path)
            self.assertTrue(apply(db,LOCK)["created"])
            self.assertTrue(apply(db,RESULT))
            self.assertTrue(compare_to_legacy(LEGACY,db)["ok"])
            first=read_snapshot(db)
            db.close()
            db=SQLiteLedger(path)
            self.assertFalse(apply(db,LOCK)["created"])
            self.assertFalse(apply(db,RESULT))
            self.assertEqual(read_snapshot(db),first)
            self.assertEqual(db.db.execute("SELECT source FROM settlement_provenance").fetchone()[0],"verified-fixture")
            db.close()

    def test_correction_changes_projection_without_rewriting_event(self):
        with tempfile.TemporaryDirectory() as folder:
            db=SQLiteLedger(Path(folder)/"ledger.sqlite")
            apply(db,LOCK)
            apply(db,dict(RESULT,result="lost",return_kr=0))
            self.assertFalse(compare_to_legacy(LEGACY,db)["ok"])
            correction=dict(RESULT,settlement_id="result-2",revision_of="result-1",reason="corrected final")
            self.assertTrue(apply(db,correction))
            self.assertTrue(compare_to_legacy(LEGACY,db)["ok"])
            self.assertEqual(db.db.execute("SELECT COUNT(*) FROM settlement_events").fetchone()[0],2)
            db.close()

    def test_unsettled_lock_remains_visible_as_exposure_not_return(self):
        with tempfile.TemporaryDirectory() as folder:
            db=SQLiteLedger(Path(folder)/"ledger.sqlite")
            apply(db,LOCK)
            snap=read_snapshot(db)
            self.assertEqual(snap["settled_bets"],0)
            self.assertEqual(snap["totals_ore"]["stake_ore"],8000)
            self.assertEqual(snap["totals_ore"]["return_ore"],0)
            db.close()
