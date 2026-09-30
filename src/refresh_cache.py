"""Refresh historical team data without consuming Sunday's odds budget."""
import json, os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from src.bet365 import Bet365Client

CACHE=Path("data/team_history.json")
LEAGUE_IDS=[4160026622,3614399544,686337048,3405541143,4212821298]

def main():
    c=Bet365Client()
    now=datetime.now(timezone.utc)
    # Discover active teams from recent + upcoming top-five fixtures in a small number of calls.
    start=now-timedelta(days=21); end=now+timedelta(days=14)
    teams={}
    cursor=start
    while cursor<end:
        stop=min(end,cursor+timedelta(hours=23,minutes=59))
        for f in c.fixtures(cursor,stop):
            league=f.get("league") or {}
            if league.get("id") not in LEAGUE_IDS: continue
            for side in ("home","away"):
                t=((f.get("teams") or {}).get(side) or {})
                if t.get("id"): teams[str(t["id"])]=t.get("name","")
        cursor=stop+timedelta(seconds=1)
    old={}
    if CACHE.exists():
        old=json.loads(CACHE.read_text())
    # Refresh a deterministic slice each run; repeated scheduled runs rotate by UTC day.
    ids=sorted(teams)
    if not ids:
        print("No teams discovered"); return
    offset=(now.toordinal()*12)%len(ids)
    batch=(ids+ids)[offset:offset+12]
    for sid in batch:
        tid=int(sid)
        data=c._get(f"/teams/{tid}/fixtures",status="finished",
            start_time=int((now-timedelta(days=90)).timestamp()),end_time=int(now.timestamp()),
            order="desc",page=1,per_page=30)
        rows=(data.get("fixtures") or data.get("items") or data.get("data") or []) if isinstance(data,dict) else (data or [])
        old[sid]={"name":teams.get(sid,""),"updated_at":now.isoformat(),"fixtures":rows}
        print(f"cached {teams.get(sid,sid)}: {len(rows)} fixtures")
    CACHE.parent.mkdir(parents=True,exist_ok=True)
    CACHE.write_text(json.dumps(old,ensure_ascii=False,separators=(",",":")))
    print(f"cache teams={len(old)}")

if __name__=="__main__": main()
