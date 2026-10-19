"""SQLite-backed reference event ledger. Prototype only; not wired to publishing.

DB operations use BEGIN IMMEDIATE, unique event IDs and an append-only audit log.
Do not use this module as a production service without deployment/storage review.
"""
import sqlite3
from src.bot_ledger_reference import ore

class SQLiteLedger:
    def __init__(self, db_path):
        self.db = sqlite3.connect(str(db_path), isolation_level=None, timeout=10)
        self.db.execute("PRAGMA foreign_keys = ON")
        self.db.execute("PRAGMA busy_timeout = 10000")
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS bets (
            bet_id TEXT PRIMARY KEY, coupon_id TEXT NOT NULL,
            stake_ore INTEGER NOT NULL CHECK(stake_ore > 0)
        );
        CREATE TABLE IF NOT EXISTS settlement_events (
            settlement_id TEXT PRIMARY KEY, bet_id TEXT NOT NULL REFERENCES bets(bet_id),
            result TEXT NOT NULL CHECK(result IN ('won','lost','void')),
            return_ore INTEGER NOT NULL CHECK(return_ore >= 0),
            revision_of TEXT REFERENCES settlement_events(settlement_id)
        );
        CREATE INDEX IF NOT EXISTS settlement_bet_idx ON settlement_events(bet_id);
        """)

    def close(self):
        self.db.close()

    def lock(self, coupon_id, bet_id, stake_kr):
        stake = ore(stake_kr)
        if not coupon_id or not bet_id or stake <= 0:
            raise ValueError("invalid lock")
        self.db.execute("BEGIN IMMEDIATE")
        try:
            prior = self.db.execute("SELECT coupon_id,stake_ore FROM bets WHERE bet_id=?", (bet_id,)).fetchone()
            if prior:
                if prior != (coupon_id,stake):
                    raise ValueError("conflicting bet_id replay")
                result = False
            else:
                self.db.execute("INSERT INTO bets VALUES (?,?,?)", (bet_id,coupon_id,stake))
                result = True
            self.db.execute("COMMIT")
            return result
        except BaseException:
            self.db.execute("ROLLBACK")
            raise

    def settle(self, settlement_id, bet_id, result, return_kr, revision_of=None):
        amount = ore(return_kr)
        if not settlement_id or not bet_id or result not in ("won","lost","void") or amount < 0:
            raise ValueError("invalid settlement")
        self.db.execute("BEGIN IMMEDIATE")
        try:
            bet = self.db.execute("SELECT stake_ore FROM bets WHERE bet_id=?", (bet_id,)).fetchone()
            if bet is None:
                raise ValueError("unknown bet")
            if result == "lost" and amount != 0 or result == "void" and amount != bet[0]:
                raise ValueError("invalid payout")
            existing = self.db.execute("SELECT bet_id,result,return_ore,revision_of FROM settlement_events WHERE settlement_id=?", (settlement_id,)).fetchone()
            event=(bet_id,result,amount,revision_of)
            if existing:
                if existing != event:
                    raise ValueError("conflicting settlement_id replay")
                self.db.execute("COMMIT")
                return False
            last = self.db.execute("SELECT settlement_id FROM settlement_events WHERE bet_id=? ORDER BY rowid DESC LIMIT 1", (bet_id,)).fetchone()
            if (last[0] if last else None) != revision_of:
                raise ValueError("revision reference mismatch")
            self.db.execute("INSERT INTO settlement_events VALUES (?,?,?,?,?)", (settlement_id,bet_id,result,amount,revision_of))
            self.db.execute("COMMIT")
            return True
        except BaseException:
            self.db.execute("ROLLBACK")
            raise

    def totals(self):
        stakes = self.db.execute("SELECT COALESCE(SUM(stake_ore),0) FROM bets").fetchone()[0]
        returns = self.db.execute("""SELECT COALESCE(SUM(e.return_ore),0)
          FROM settlement_events e
          WHERE NOT EXISTS (SELECT 1 FROM settlement_events next
            WHERE next.revision_of=e.settlement_id)""").fetchone()[0]
        count = self.db.execute("""SELECT COUNT(*) FROM settlement_events e
          WHERE NOT EXISTS (SELECT 1 FROM settlement_events next
            WHERE next.revision_of=e.settlement_id)""").fetchone()[0]
        return {"stake_ore":stakes,"return_ore":returns,"profit_ore":returns-stakes,"settled_bets":count}
