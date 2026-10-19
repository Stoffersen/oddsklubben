import tempfile
import unittest
from pathlib import Path
from src.bot_ledger_sqlite import SQLiteLedger
from src.bot_shadow_compare import compare_snapshots

class DualShadowTests(unittest.TestCase):
    def test_independently_created_synthetic_ledger_matches(self):
        with tempfile.TemporaryDirectory() as d:
            ledger = SQLiteLedger(Path(d)/"shadow.db")
            ledger.lock("c1", "b1", 40)
            ledger.lock("c1", "b2", 40)
            ledger.settle("s1","b1","won",46.8)
            ledger.settle("s2","b2","won",48.8)
            legacy = {"stake_kr":80, "return_kr":95.6, "profit_kr":15.6}
            report = compare_snapshots(legacy,ledger.totals())
            self.assertTrue(report["ok"],report)
            ledger.close()

    def test_missing_bet_detected_without_reconciliation_write(self):
        with tempfile.TemporaryDirectory() as d:
            ledger = SQLiteLedger(Path(d)/"shadow.db")
            ledger.lock("c1", "b1", 40)
            legacy = {"stake_kr":80, "return_kr":95.6, "profit_kr":15.6}
            before = ledger.totals().copy()
            report = compare_snapshots(legacy, before)
            self.assertFalse(report["ok"])
            self.assertIn("stake_kr mismatch",report["anomalies"])
            self.assertEqual(ledger.totals(),before)
            ledger.close()

    def test_difference_in_ore_is_not_rounded_away(self):
        result = compare_snapshots(
            {"stake_kr":80, "return_kr":95.6,"profit_kr":15.6},
            {"stake_ore":8000,"return_ore":9561,"profit_ore":1561})
        self.assertFalse(result["ok"])
        self.assertEqual(result["comparison"]["return_kr"]["difference_ore"],1)

    def test_bad_candidate_type_fails_closed(self):
        with self.assertRaises(ValueError):
            compare_snapshots({"stake_kr":1,"return_kr":1,"profit_kr":0},
                              {"stake_ore":True,"return_ore":100,"profit_ore":0})

if __name__=="__main__":
    unittest.main()
