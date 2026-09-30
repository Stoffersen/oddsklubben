"""Feature engineering from finished fixtures; no fabricated xG."""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

@dataclass
class Strength:
    long_term: float
    recent_form: float
    goal_diff: float
    venue_form: float
    sample_games: int

def _points(gf,ga): return 3 if gf>ga else (1 if gf==ga else 0)
def _norm(x,scale): return max(-1.5,min(1.5,x/scale))

def strength_from_fixtures(fixtures, team_id, venue):
    rows=[]
    for f in fixtures:
        if f.get("status")!="finished": continue
        teams=f.get("teams") or {}; h=(teams.get("home") or {}).get("id"); a=(teams.get("away") or {}).get("id")
        goals=f.get("goals") or {}; hg=goals.get("home"); ag=goals.get("away")
        if hg is None or ag is None or team_id not in (h,a): continue
        is_home=team_id==h; gf=hg if is_home else ag; ga=ag if is_home else hg
        rows.append((gf,ga,"home" if is_home else "away"))
    rows=rows[:20]
    if not rows: return None
    recent=rows[:6]
    ppg=sum(_points(gf,ga) for gf,ga,_ in recent)/(3*len(recent))
    gd=sum(gf-ga for gf,ga,_ in recent)/len(recent)
    long_ppg=sum(_points(gf,ga) for gf,ga,_ in rows)/(3*len(rows))
    venue_rows=[r for r in rows if r[2]==venue][:8]
    venue_ppg=(sum(_points(gf,ga) for gf,ga,_ in venue_rows)/(3*len(venue_rows))) if venue_rows else .5
    return Strength(_norm(long_ppg-.5,.35),_norm(ppg-.5,.35),_norm(gd,1.5),_norm(venue_ppg-.5,.35),len(rows))

def team_history(client, team_id, now=None, days=90):
    now=now or datetime.now(timezone.utc)
    data=client._get(f"/teams/{team_id}/fixtures",status="finished",
        start_time=int((now-timedelta(days=days)).timestamp()),end_time=int(now.timestamp()),
        order="desc",page=1,per_page=30)
    if isinstance(data,dict): return data.get("fixtures") or data.get("items") or data.get("data") or []
    return data or []
