"""Oddsklubben live candidate-field runner.

This stage discovers the provider's competition IDs/names and verifies Bet365
1X2 availability. It does NOT invent team-strength inputs: value bets are only
computed once real model features are connected.
"""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from src.bet365 import Bet365Client

TZ = ZoneInfo("Europe/Copenhagen")
TARGET_NAMES = (
    "premier league", "championship", "serie a", "bundesliga",
    "superliga", "laliga", "la liga",
)
INTERNATIONAL_HINTS = (
    "world cup", "uefa nations", "euro", "qualification", "qualifier",
    "international", "friendly",
)

def next_week(now=None):
    now = now or datetime.now(TZ)
    monday = (now + timedelta(days=(7-now.weekday()))).replace(
        hour=0, minute=0, second=0, microsecond=0)
    return monday, monday + timedelta(days=6, hours=23, minutes=59, seconds=59)

def league_info(f):
    league=f.get("league") or {}
    if isinstance(league, dict):
        return league.get("id"), str(league.get("name") or league.get("slug") or "")
    return None, str(league)

def in_scope(name):
    n=name.casefold()
    return any(x in n for x in TARGET_NAMES) or any(x in n for x in INTERNATIONAL_HINTS)

def main():
    start,end=next_week()
    checked=datetime.now(TZ)
    print(f"Window: {start.isoformat()} -> {end.isoformat()}")
    print(f"Odds check: {checked.isoformat()}")
    client=Bet365Client()
    fixtures=client.fixtures(start,end)
    print(f"Provider scheduled fixtures: {len(fixtures)}")

    leagues={}
    scoped=[]
    for f in fixtures:
        lid,name=league_info(f)
        leagues[(lid,name)]=leagues.get((lid,name),0)+1
        if in_scope(name):
            scoped.append(f)

    print("Competitions returned:")
    for (lid,name),count in sorted(leagues.items(), key=lambda x:(x[0][1],str(x[0][0]))):
        print(f"  id={lid!r} | {name} | fixtures={count}")

    print(f"In-scope fixtures before Bet365 check: {len(scoped)}")
    quotes=[]
    for f in scoped:
        try:
            q=client.quote_1x2(f)
        except Exception as exc:
            print(f"Odds lookup failed for fixture {f.get('id')}: {type(exc).__name__}: {exc}")
            continue
        if q:
            quotes.append(q)
            print(f"BET365 | {q.league} | {q.home} v {q.away} | "
                  f"1={q.home_odds:.2f} X={q.draw_odds:.2f} 2={q.away_odds:.2f}")

    print(f"Verified Bet365 1X2 candidate field: {len(quotes)}")
    print("No Top 10 emitted yet: real team-strength/xG/form/availability features "
          "are not connected, so model probabilities and EV would otherwise be fabricated.")

if __name__=="__main__":
    main()
