"""Pure read-only projection from test ledger state; no publication or migration."""
from src.bot_shadow_compare import compare_snapshots

def read_snapshot(ledger):
    values=ledger.totals()
    return {"schema_version":1, "read_only":True,
            "totals_ore":dict(values), "settled_bets":values["settled_bets"]}

def compare_to_legacy(legacy_totals, ledger):
    return compare_snapshots(legacy_totals,read_snapshot(ledger)["totals_ore"])
