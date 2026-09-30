"""Oddsklubben weekly value runner."""
from datetime import datetime,timedelta,timezone
from zoneinfo import ZoneInfo
from src.bet365 import Bet365Client
from src.model import TeamProfile,estimate_1x2,confidence
from src.stats import team_history,strength_from_fixtures
from src.value import picks_for_quote

TZ=ZoneInfo("Europe/Copenhagen")
TARGET=("premier league","championship","serie a","bundesliga","superliga","laliga","la liga")
INTL=("world cup","uefa nations","euro","qualification","qualifier","international","friendly")

def next_week(now=None):
    now=now or datetime.now(TZ); d=7-now.weekday()
    start=(now+timedelta(days=d)).replace(hour=0,minute=0,second=0,microsecond=0)
    return start,start+timedelta(days=6,hours=23,minutes=59,seconds=59)
def info(f):
    x=f.get("league") or {}; return (x.get("id"),str(x.get("name") or "")) if isinstance(x,dict) else (None,str(x))
def scoped(name):
    n=name.casefold(); return any(x in n for x in TARGET+INTL)
def tid(f,side):
    return (((f.get("teams") or {}).get(side) or {}).get("id"))
def profile(s):
    return TeamProfile(s.long_term,s.recent_form,s.goal_diff,s.venue_form,0.0)

def main():
    start,end=next_week(); checked=datetime.now(TZ); c=Bet365Client()
    fixtures=c.fixtures(start,end); fs=[f for f in fixtures if scoped(info(f)[1])]
    print(f"Window: {start.isoformat()} -> {end.isoformat()}")
    print(f"Odds check: {checked.isoformat()}")
    print(f"In-scope fixtures: {len(fs)}")
    # Protect the free-tier hourly quota: reserve requests for odds first.
    quotes=[]
    for f in fs:
        try:
            q=c.quote_1x2(f)
            if q: quotes.append((f,q))
        except RuntimeError as e:
            if "rate limit" in str(e).lower():
                print(f"RATE LIMIT: {e}"); break
            print(f"Odds error {f.get('id')}: {e}")
    print(f"Verified Bet365 1X2 candidate field: {len(quotes)}")
    # Historical team calls cost 2 requests/match, so process only while quota permits.
    picks=[]
    for f,q in quotes:
        h,a=tid(f,"home"),tid(f,"away")
        if not h or not a: continue
        try:
            hh=team_history(c,h,checked.astimezone(timezone.utc))
            ah=team_history(c,a,checked.astimezone(timezone.utc))
        except RuntimeError as e:
            if "rate limit" in str(e).lower():
                print(f"MODEL DATA RATE LIMIT: {e}"); break
            continue
        hs=strength_from_fixtures(hh,h,"home"); ass=strength_from_fixtures(ah,a,"away")
        if not hs or not ass: continue
        probs=estimate_1x2(profile(hs),profile(ass))
        conf=confidence(min(hs.sample_games,ass.sample_games),1.0,0.5)
        picks.extend(picks_for_quote(q,probs,conf))
    picks.sort(key=lambda p:p.ev*p.confidence,reverse=True)
    qualified=[p for p in picks if p.confidence>=0.55 and p.ev>0][:10]
    print("TOP VALUE (model estimates; not guarantees)")
    for i,p in enumerate(qualified,1):
        print(f"{i}. {p.league} | {p.match} | {p.selection} @ {p.odds:.2f} | "
              f"P={p.probability:.1%} fair={p.fair_odds:.2f} EV={p.ev:+.1%} conf={p.confidence:.2f}")
    if not qualified:
        print("No qualified value picks with currently available verified data.")
    distinct=[]
    for p in qualified:
        if p.fixture_id not in {x.fixture_id for x in distinct}: distinct.append(p)
    if distinct:
        print(f"SINGLE: {distinct[0].match} {distinct[0].selection} @ {distinct[0].odds:.2f}")
    if len(distinct)>=2:
        print(f"DOUBLE: combined odds {distinct[0].odds*distinct[1].odds:.2f}")
    if len(distinct)>=3:
        print(f"TRIBLE: combined odds {distinct[0].odds*distinct[1].odds*distinct[2].odds:.2f}")
    print("LIMITATION: model currently uses results/form/goal difference/home-away form; xG and injury/lineup feeds are not connected.")

if __name__=="__main__": main()
