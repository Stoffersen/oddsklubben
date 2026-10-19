import copy
import json
import unittest
from pathlib import Path
from src.bot_shadow_reconcile import reconcile

class ShadowReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.feed=json.loads((Path(__file__).resolve().parents[1]/"data/bot-bets.json").read_text(encoding="utf-8"))

    def test_current_legacy_snapshot_reconciles(self):
        result=reconcile(self.feed)
        self.assertTrue(result["ok"],result["anomalies"])
        self.assertEqual(result["computed_ore"],result["published_ore"])

    def test_unaccounted_extra_coupon_is_detected(self):
        altered=copy.deepcopy(self.feed)
        for w in altered["weeks"]:
            w.pop("excluded_from_totals",None)
        self.assertFalse(reconcile(altered)["ok"])

    def test_tampered_balance_is_detected(self):
        altered=copy.deepcopy(self.feed)
        altered["totals"]["profit_kr"]+=1
        self.assertFalse(reconcile(altered)["ok"])

    def test_missing_duplicate_provenance_is_detected(self):
        altered=copy.deepcopy(self.feed)
        excluded=next(w for w in altered["weeks"] if w.get("excluded_from_totals"))
        excluded["duplicate_of"]="not-real"
        self.assertFalse(reconcile(altered)["ok"])

if __name__=="__main__":
    unittest.main()
