"""Contract-path tests: lock -> settle -> correction -> read-only snapshot.
Reference only. Never reads or writes live Bot JSON or an actual ledger.
"""
import unittest
from src.bot_ledger_reference import Ledger

def snapshot(ledger):
    """Projection for contract testing, not a production feed publisher."""
    t = ledger.totals()
    return {
        "schema_version": 2,
        "totals": {
            "stake_kr": round(t["stake_ore"] / 100, 2),
            "return_kr": round(t["return_ore"] / 100, 2),
            "profit_kr": round(t["profit_ore"] / 100, 2),
        },
        "settled_bets": t["settled_bets"],
    }

class LedgerContractTests(unittest.TestCase):
    def test_replayed_publication_keeps_balances(self):
        ledger = Ledger()
        for _ in range(3):
            ledger.lock("coupon-1", "bet-1", 40)
            ledger.lock("coupon-1", "bet-2", 40)
            ledger.settle("result-1", "bet-1", "won", 46.8)
        self.assertEqual(snapshot(ledger)["totals"], {
            "stake_kr": 80, "return_kr": 46.8, "profit_kr": -33.2})
        self.assertEqual(len(ledger.bets), 2)
        self.assertEqual(len(ledger.events), 1)

    def test_corrected_result_changes_effect_not_audit_history(self):
        ledger = Ledger()
        ledger.lock("coupon-1", "bet-1", 20)
        ledger.settle("event-1", "bet-1", "lost", 0)
        ledger.settle("event-2", "bet-1", "won", 31.2, revision_of="event-1")
        before = snapshot(ledger)
        ledger.settle("event-2", "bet-1", "won", 31.2, revision_of="event-1")
        self.assertEqual(snapshot(ledger), before)
        self.assertEqual(len(ledger.events), 2)
        self.assertEqual(before["totals"]["profit_kr"], 11.2)

    def test_void_and_pending_state(self):
        ledger = Ledger()
        ledger.lock("coupon-1", "bet-1", 20)
        self.assertEqual(snapshot(ledger)["settled_bets"], 0)
        ledger.settle("void-1", "bet-1", "void", 20)
        self.assertEqual(snapshot(ledger)["totals"]["profit_kr"], 0)

    def test_distinct_explicit_locks_count_twice(self):
        ledger = Ledger()
        ledger.lock("coupon-1", "bet-1", 40)
        ledger.lock("coupon-2", "bet-2", 40)
        self.assertEqual(snapshot(ledger)["totals"]["stake_kr"], 80)

if __name__ == "__main__":
    unittest.main()
