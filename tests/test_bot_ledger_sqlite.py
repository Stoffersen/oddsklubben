import tempfile
import unittest
from pathlib import Path
from src.bot_ledger_sqlite import SQLiteLedger

class SQLiteLedgerTests(unittest.TestCase):
    def test_persistence_replay_and_revision(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"ledger.sqlite3"
            a=SQLiteLedger(path)
            self.assertTrue(a.lock("coupon-1","bet-1",40))
            self.assertTrue(a.settle("event-1","bet-1","lost",0))
            a.close()
            b=SQLiteLedger(path)
            self.assertFalse(b.lock("coupon-1","bet-1",40))
            self.assertFalse(b.settle("event-1","bet-1","lost",0))
            b.settle("event-2","bet-1","won",46.8,revision_of="event-1")
            self.assertEqual(b.totals(),{"stake_ore":4000,"return_ore":4680,"profit_ore":680,"settled_bets":1})
            self.assertEqual(b.db.execute("SELECT COUNT(*) FROM settlement_events").fetchone()[0],2)
            b.close()

    def test_conflicting_replay_does_not_mutate(self):
        with tempfile.TemporaryDirectory() as d:
            db=SQLiteLedger(Path(d)/"x.db")
            db.lock("c","b",20)
            with self.assertRaises(ValueError):
                db.lock("different","b",20)
            db.settle("e1","b","lost",0)
            with self.assertRaises(ValueError):
                db.settle("e1","b","won",30)
            with self.assertRaises(ValueError):
                db.settle("e2","b","won",30)
            self.assertEqual(db.totals()["profit_ore"],-2000)
            db.close()

    def test_database_blocks_forked_revision_chains(self):
        import sqlite3
        with tempfile.TemporaryDirectory() as d:
            db=SQLiteLedger(Path(d)/"x.db")
            db.lock("coupon","bet",20)
            db.settle("first","bet","lost",0)
            db.settle("second","bet","won",30,revision_of="first")
            with self.assertRaises(sqlite3.IntegrityError):
                db.db.execute("INSERT INTO settlement_events VALUES (?,?,?,?,?)",
                              ("fork","bet","won",50,"first"))
            with self.assertRaises(sqlite3.IntegrityError):
                db.db.execute("INSERT INTO settlement_events VALUES (?,?,?,?,?)",
                              ("second-root","bet","lost",0,None))
            self.assertEqual(db.totals()["return_ore"],3000)
            db.close()

if __name__=="__main__":
    unittest.main()
