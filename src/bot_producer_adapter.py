"""Opt-in event adapter, not wired to active publication."""
from datetime import datetime
from src.bot_ledger_sqlite import SQLiteLedger

def parse_time(value):
    if not isinstance(value, str):
        raise ValueError("timestamp required")
    d = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if d.utcoffset() is None:
        raise ValueError("timezone required")
    return d

def apply(ledger, event):
    if event.get("schema_version") != 1:
        raise ValueError("unsupported schema")
    kind = event.get("event_type")
    if kind == "lock":
        keys = ("coupon_id","bet_id","stake_kr","fixture_id","locked_at_utc","kickoff_utc")
        if any(not event.get(k) for k in keys):
            raise ValueError("missing lock field")
        if parse_time(event["locked_at_utc"]) >= parse_time(event["kickoff_utc"]):
            raise ValueError("cannot lock after kickoff")
        return ledger.lock(event["coupon_id"],event["bet_id"],event["stake_kr"])
    if kind == "settle":
        keys = ("settlement_id","bet_id","result","return_kr","source","observed_at_utc")
        if any(k not in event for k in keys):
            raise ValueError("missing settlement field")
        if not event["source"]:
            raise ValueError("source required")
        parse_time(event["observed_at_utc"])
        if event.get("revision_of") and not event.get("reason"):
            raise ValueError("reason required for correction")
        return ledger.settle(event["settlement_id"],event["bet_id"],event["result"],
                             event["return_kr"],event.get("revision_of"))
    raise ValueError("unsupported event kind")
