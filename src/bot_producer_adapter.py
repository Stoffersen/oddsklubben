"""Opt-in event adapter, not wired to active publication."""
from datetime import datetime, timezone
from src.bot_ledger_sqlite import SQLiteLedger

def parse_time(value):
    if not isinstance(value, str):
        raise ValueError("timestamp required")
    d = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if d.utcoffset() is None:
        raise ValueError("timezone required")
    return d.astimezone(timezone.utc)

def apply(ledger, event):
    if event.get("schema_version") != 1:
        raise ValueError("unsupported schema")
    kind = event.get("event_type")
    if kind == "lock":
        keys = ("lock_request_id","coupon_id","bet_id","stake_kr","fixture_id","locked_at_utc","kickoff_utc")
        if any(k not in event or event[k] is None or event[k] == "" for k in keys):
            raise ValueError("missing lock field")
        for identity in ("lock_request_id", "coupon_id", "bet_id", "fixture_id"):
            if not isinstance(event[identity], str) or not event[identity].strip():
                raise ValueError("invalid identity")
        if parse_time(event["locked_at_utc"]) >= parse_time(event["kickoff_utc"]):
            raise ValueError("cannot lock after kickoff")
        return ledger.lock_request(event["lock_request_id"], event["coupon_id"], event["bet_id"], event["stake_kr"], event["fixture_id"], event["kickoff_utc"], event["locked_at_utc"])
    if kind == "settle":
        keys = ("settlement_id","bet_id","result","return_kr","source","observed_at_utc")
        if any(k not in event for k in keys):
            raise ValueError("missing settlement field")
        for identity in ("settlement_id", "bet_id", "source"):
            if not isinstance(event[identity], str) or not event[identity].strip():
                raise ValueError("invalid settlement identity")
        if not event["source"]:
            raise ValueError("source required")
        parse_time(event["observed_at_utc"])
        if event.get("revision_of") is not None and (not isinstance(event["revision_of"], str) or not event["revision_of"].strip() or not isinstance(event.get("reason"), str) or not event["reason"].strip()):
            raise ValueError("reason required for correction")
        return ledger.settle(event["settlement_id"],event["bet_id"],event["result"],
                             event["return_kr"],event.get("revision_of"), provenance={"source":event["source"], "observed_at_utc":parse_time(event["observed_at_utc"]).isoformat(), "reason":event.get("reason"), "source_ref":event.get("source_ref")})
    raise ValueError("unsupported event kind")
