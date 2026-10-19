"""Read-only transitional Bot feed builder. No guessed historical event IDs.

This view preserves legacy history verbatim and permits separately identified
new ledger entries only. It never writes files or modifies the source object.
"""
from copy import deepcopy
from decimal import Decimal
from src.bot_shadow_reconcile import cents, reconcile

def money(ore):
    return float(Decimal(ore) / 100)

def build_compatible_feed(legacy_feed, new_weeks):
    if not reconcile(legacy_feed)["ok"]:
        raise ValueError("legacy feed must reconcile before projection")
    if not isinstance(new_weeks, list):
        raise ValueError("new weeks must be a list")
    out=deepcopy(legacy_feed)
    known_dates={w["coupon_date"] for w in out["weeks"]}
    existing_ids=set()
    extra_stake=extra_return=settled_extra=0
    for week in new_weeks:
        if not isinstance(week,dict):
            raise ValueError("invalid new week")
        required=("coupon_id","coupon_date","status","stake_kr","return_kr","profit_kr","bets")
        if any(k not in week for k in required):
            raise ValueError("missing new week field")
        if not isinstance(week["coupon_id"],str) or not week["coupon_id"].strip():
            raise ValueError("missing authoritative coupon ID")
        if week["coupon_id"] in existing_ids or week["coupon_date"] in known_dates:
            raise ValueError("duplicate coupon identity/date")
        if week["status"]!="settled" or week.get("excluded_from_totals"):
            raise ValueError("only verified settled new coupons supported")
        if not isinstance(week["bets"],list) or not week["bets"]:
            raise ValueError("new coupon requires bets")
        ids=[bet.get("bet_id") for bet in week["bets"]]
        if any(not isinstance(i,str) or not i.strip() for i in ids):
            raise ValueError("each new bet requires authoritative bet ID")
        if len(set(ids))!=len(ids) or set(ids)&existing_ids:
            raise ValueError("duplicate bet ID")
        stake=cents(week["stake_kr"])
        paid=cents(week["return_kr"])
        if stake<=0 or paid<0 or cents(week["profit_kr"])!=paid-stake:
            raise ValueError("invalid new coupon totals")
        if sum(cents(b["stake_kr"]) for b in week["bets"])!=stake:
            raise ValueError("bet stakes do not match coupon")
        if sum(cents(b["return_kr"]) for b in week["bets"])!=paid:
            raise ValueError("bet returns do not match coupon")
        known_dates.add(week["coupon_date"])
        existing_ids.add(week["coupon_id"])
        existing_ids.update(ids)
        extra_stake+=stake
        extra_return+=paid
        settled_extra+=1
        out["weeks"].append(deepcopy(week))
    if not new_weeks:
        return out
    base=legacy_feed["totals"]
    stake=cents(base["stake_kr"])+extra_stake
    paid=cents(base["return_kr"])+extra_return
    out["totals"].update(settled_weeks=base["settled_weeks"]+settled_extra,
       stake_kr=money(stake),return_kr=money(paid),profit_kr=money(paid-stake),
       return_pct=round(paid/stake*100,2) if stake else 0)
    return out
