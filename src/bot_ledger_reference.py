"""Pure reference ledger for Bot Bet; not connected to the production feed.

Stable IDs are supplied by the authoritative producer, never fabricated by the UI.
Amounts are integer øre to avoid binary rounding. Ledger operations are immutable
from the perspective of callers; repeated events are ignored after consistency checks.
"""
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

VALID_RESULTS = {"pending", "won", "lost", "void"}

def ore(value):
    try:
        amount = Decimal(str(value))
        if not amount.is_finite():
            raise ValueError("amount must be finite")
        return int((amount * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    except (InvalidOperation, OverflowError) as exc:
        raise ValueError("invalid money amount") from exc

@dataclass(frozen=True)
class Bet:
    coupon_id: str
    bet_id: str
    stake_ore: int

class Ledger:
    def __init__(self):
        self.bets = {}
        self.events = {}
        self.settlements = {}

    def lock(self, coupon_id, bet_id, stake_kr):
        if not coupon_id or not bet_id:
            raise ValueError("stable coupon_id and bet_id required")
        bet = Bet(coupon_id, bet_id, ore(stake_kr))
        if bet.stake_ore <= 0:
            raise ValueError("stake must be positive")
        previous = self.bets.get(bet_id)
        if previous is not None and previous != bet:
            raise ValueError("bet_id collision with different terms")
        self.bets[bet_id] = bet
        return previous is None

    def settle(self, settlement_id, bet_id, result, return_kr, *, revision_of=None):
        if not settlement_id or bet_id not in self.bets:
            raise ValueError("unknown bet or settlement ID")
        if result not in VALID_RESULTS or result == "pending":
            raise ValueError("invalid final settlement status")
        returned = ore(return_kr)
        if returned < 0 or result in ("lost", "void") and returned != (self.bets[bet_id].stake_ore if result == "void" else 0):
            raise ValueError("invalid payout")
        event = (bet_id, result, returned, revision_of)
        if settlement_id in self.events:
            if self.events[settlement_id] != event:
                raise ValueError("settlement_id reused with different terms")
            return False
        prior = self.settlements.get(bet_id)
        if prior is not None and revision_of != prior[0]:
            raise ValueError("re-settlement requires reference to prior event")
        if prior is None and revision_of is not None:
            raise ValueError("revision without prior event")
        self.events[settlement_id] = event
        self.settlements[bet_id] = (settlement_id, result, returned)
        return True

    def totals(self):
        stakes = sum(b.stake_ore for b in self.bets.values())
        returns = sum(s[2] for s in self.settlements.values())
        return {"stake_ore": stakes, "return_ore": returns, "profit_ore": returns-stakes,
                "settled_bets": len(self.settlements)}
