import unittest
from src.bot_ledger_reference import Ledger

class LedgerTests(unittest.TestCase):
    def test_repeated_sync_is_idempotent(self):
        ledger=Ledger()
        self.assertTrue(ledger.lock("coupon-a","bet-1",40))
        self.assertFalse(ledger.lock("coupon-a","bet-1",40))
        self.assertTrue(ledger.settle("settle-1","bet-1","won",46.8))
        self.assertFalse(ledger.settle("settle-1","bet-1","won",46.8))
        self.assertEqual(ledger.totals(),{"stake_ore":4000,"return_ore":4680,"profit_ore":680,"settled_bets":1})

    def test_conflicting_replays_rejected(self):
        l=Ledger();l.lock("a","b",20)
        with self.assertRaises(ValueError):l.lock("x","b",20)
        l.settle("s1","b","lost",0)
        with self.assertRaises(ValueError):l.settle("s1","b","won",30)
        with self.assertRaises(ValueError):l.settle("s2","b","won",30)

    def test_explicit_revision_replaces_prior_effect(self):
        l=Ledger();l.lock("a","b",20);l.settle("s1","b","lost",0)
        l.settle("s2","b","won",31.2,revision_of="s1")
        self.assertEqual(l.totals()["profit_ore"],1120)
        self.assertEqual(len(l.events),2)

    def test_void_returns_stake(self):
        l=Ledger();l.lock("a","b",20);l.settle("v","b","void",20)
        self.assertEqual(l.totals()["profit_ore"],0)

    def test_distinct_identical_bets_need_distinct_ids(self):
        l=Ledger();l.lock("a","x",40);l.lock("b","y",40)
        self.assertEqual(l.totals()["stake_ore"],8000)

    def test_invalid_money_never_mutates_ledger(self):
        ledger = Ledger()
        for value in ("NaN", "Infinity", "-1", "0", "garbage"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                ledger.lock("c", "b", value)
        self.assertEqual(ledger.totals()["stake_ore"], 0)
        ledger.lock("c", "b", 20)
        for value in ("NaN", "Infinity", "-5"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                ledger.settle("event", "b", "won", value)
        self.assertEqual(ledger.totals()["return_ore"], 0)

    def test_revision_cannot_rewrite_an_unrelated_bet(self):
        ledger = Ledger()
        ledger.lock("c", "a", 20)
        ledger.lock("c", "b", 20)
        ledger.settle("e1", "a", "lost", 0)
        with self.assertRaises(ValueError):
            ledger.settle("e2", "b", "won", 30, revision_of="e1")
        self.assertEqual(ledger.totals()["settled_bets"], 1)

if __name__=="__main__":
    unittest.main()
