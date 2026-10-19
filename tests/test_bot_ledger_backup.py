import tempfile
import unittest
from pathlib import Path
from src.bot_ledger_sqlite import SQLiteLedger
from src.bot_ledger_backup import backup_ledger

class SQLiteBackupTests(unittest.TestCase):
    def test_backup_is_consistent_and_replay_safe_after_restore(self):
        with tempfile.TemporaryDirectory() as tmp:
            primary=Path(tmp)/"primary.sqlite3"
            archive=Path(tmp)/"archive.sqlite3"
            ledger=SQLiteLedger(primary)
            ledger.lock("coupon-x","bet-x",80)
            ledger.settle("event-x","bet-x","won",95.6)
            backup_ledger(primary,archive)
            with self.assertRaises(FileExistsError):
                backup_ledger(primary,archive)
            ledger.close()
            recovered=SQLiteLedger(archive)
            self.assertEqual(recovered.totals(),{"stake_ore":8000,"return_ore":9560,
                                                "profit_ore":1560,"settled_bets":1})
            self.assertFalse(recovered.lock("coupon-x","bet-x",80))
            self.assertFalse(recovered.settle("event-x","bet-x","won",95.6))
            recovered.close()

    def test_missing_source_and_same_destination_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"missing.sqlite3"
            with self.assertRaises(FileNotFoundError):
                backup_ledger(path,Path(tmp)/"other.sqlite3")
            with self.assertRaises(ValueError):
                backup_ledger(path,path)
            self.assertFalse(path.exists())

if __name__=="__main__":
    unittest.main()
