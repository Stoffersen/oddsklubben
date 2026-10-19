"""Read-only regression checks for the published Bot Bet ledger.
Run: python -m unittest discover -s tests -p 'test_*.py'
"""
import json
import unittest
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data" / "bot-bets.json"

def signature(week):
    """Canonical economic coupon signature, independent of publish date."""
    return tuple(sorted([(
        b.get("type"),
        float(b.get("stake_kr", 0)),
        tuple(sorted((l.get("date"), l.get("match"), l.get("selection"))
                     for l in b.get("legs", [])))
    ) for b in week.get("bets", [])], key=repr))

class BotLedgerIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.feed = json.loads(DATA.read_text(encoding="utf-8"))

    def test_duplicate_records_never_count_as_independent_bets(self):
        weeks = self.feed["weeks"]
        eligible = [w for w in weeks if not w.get("excluded_from_totals")]
        for excluded in (w for w in weeks if w.get("excluded_from_totals")):
            self.assertTrue(excluded.get("duplicate_of"), "Exclusion needs provenance")
            matches = [w for w in weeks if w.get("coupon_date") == excluded["duplicate_of"]]
            self.assertEqual(len(matches), 1, "Duplicate points to exactly one coupon")
            self.assertEqual(signature(excluded), signature(matches[0]))
        fingerprints = [signature(w) for w in eligible]
        self.assertEqual(len(fingerprints), len(set(fingerprints)),
                         "Two included coupons have identical economic selections")

    def test_published_totals_match_eligible_settlements(self):
        eligible = [w for w in self.feed["weeks"]
                    if w.get("status") == "settled" and not w.get("excluded_from_totals")]
        totals = self.feed["totals"]
        self.assertEqual(totals["settled_weeks"], len(eligible))
        for key in ("stake_kr", "return_kr", "profit_kr"):
            self.assertAlmostEqual(totals[key], sum(float(w.get(key) or 0) for w in eligible),
                                   places=2, msg=key)

    def test_settled_coupon_economics(self):
        for week in self.feed["weeks"]:
            if week.get("status") != "settled":
                continue
            self.assertAlmostEqual(week["profit_kr"],
                                   week["return_kr"] - week["stake_kr"], places=2)
            self.assertAlmostEqual(week["stake_kr"],
                                   sum(float(b["stake_kr"]) for b in week["bets"]), places=2)

if __name__ == "__main__":
    unittest.main()
