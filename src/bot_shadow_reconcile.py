"""Read-only legacy Bot Bet shadow reconciliation. No IDs or ledger events synthesized.

Usage: python -m src.bot_shadow_reconcile --feed data/bot-bets.json
Nonzero exit on mismatch; prints JSON report. Does not write files.
"""
import argparse
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

def cents(value):
    try:
        v = Decimal(str(value))
        if not v.is_finite() or v.as_tuple().exponent < -2:
            raise ValueError("invalid monetary precision")
        return int(v * 100)
    except (InvalidOperation, TypeError) as exc:
        raise ValueError("invalid monetary amount") from exc

def reconcile(feed):
    weeks=feed["weeks"]
    included=[w for w in weeks if w.get("status")=="settled" and not w.get("excluded_from_totals")]
    anomalies=[]
    for w in weeks:
        if w.get("excluded_from_totals"):
            originals=[x for x in weeks if x.get("coupon_date")==w.get("duplicate_of")]
            if len(originals)!=1:
                anomalies.append("excluded coupon has no unique original: "+str(w.get("coupon_date")))
    fields=("stake_kr","return_kr","profit_kr")
    computed={key:sum(cents(w[key]) for w in included) for key in fields}
    published={key:cents(feed["totals"][key]) for key in fields}
    if computed["profit_kr"]!=computed["return_kr"]-computed["stake_kr"]:
        anomalies.append("included coupon profit does not equal returns minus stake")
    if published["profit_kr"]!=published["return_kr"]-published["stake_kr"]:
        anomalies.append("published profit does not equal returns minus stake")
    if len(included)!=feed["totals"]["settled_weeks"]:
        anomalies.append("settled_weeks differs")
    for key in fields:
        if computed[key]!=published[key]:
            anomalies.append(key+" differs")
    return {"ok":not anomalies, "included_coupon_dates":[w["coupon_date"] for w in included],
            "excluded_coupon_dates":[w["coupon_date"] for w in weeks if w.get("excluded_from_totals")],
            "computed_ore":computed,"published_ore":published,"anomalies":anomalies,
            "mode":"legacy-read-only; no authoritative ledger comparison"}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--feed",type=Path,default=Path("data/bot-bets.json"))
    args=parser.parse_args()
    report=reconcile(json.loads(args.feed.read_text(encoding="utf-8")))
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 0 if report["ok"] else 1

if __name__=="__main__":
    raise SystemExit(main())
