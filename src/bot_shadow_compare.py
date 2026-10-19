"""Pure comparison of two independent monetary snapshots (no side effects).

This module does NOT import historical coupons into the new ledger or fabricate IDs.
Its synthetic SQLite fixtures exercise the comparison until a real producer exists.
"""
from src.bot_shadow_reconcile import cents

FIELDS = ("stake_kr", "return_kr", "profit_kr")

def compare_snapshots(legacy_totals, ledger_totals):
    """Compare legacy kroner with authoritative candidate's integer øre values."""
    comparison = {}
    anomalies = []
    for key in FIELDS:
        expected = cents(legacy_totals[key])
        actual = ledger_totals[{"stake_kr":"stake_ore",
                                "return_kr":"return_ore",
                                "profit_kr":"profit_ore"}[key]]
        if not isinstance(actual, int) or isinstance(actual, bool):
            raise ValueError("ledger total must be integer øre: " + key)
        comparison[key] = {"legacy_ore": expected, "candidate_ore": actual,
                           "difference_ore": actual - expected}
        if actual != expected:
            anomalies.append(key + " mismatch")
    return {"ok": not anomalies, "comparison": comparison, "anomalies": anomalies,
            "mode": "read-only dual snapshot; only valid when both cover same bets"}
