"""Feature engineering from finished fixtures; no fabricated xG."""
from dataclasses import dataclass
@dataclass
class Strength:
    long_term:float; recent_form:float; goal_diff:float; venue_form:float; sample_games:int
def _points(gf,ga): return 3 if gf>ga else (1 if gf==ga else 0)
def _norm(x,scale): return max(-1.5,min(1.5,x/scale))
def strength_from_fixtures(fixtures,team_id,venue):
    rows=[]
    for f in fixtures:
        if f.get("status")!="finished": continue
        teams=f.get("teams") or {}; h=(teams.get("home") or {}).get("id"); a=(teams.get("away") or {}).get("id")
        goals=f.get("goals") or {}; hg=goals.get("home"); ag=goals.get("away")
        if hg is None or ag is None or team_id not in (h,a): continue
        ih=team_id==h; rows.append((hg if ih else ag,ag if ih else hg,"home" if ih else "away"))
    rows=rows[:20]
    if not rows:return None
    recent=rows[:6]; venue_rows=[r for r in rows if r[2]==venue][:8]
    ppg=sum(_points(x,y) for x,y,_ in recent)/(3*len(recent))
    gd=sum(x-y for x,y,_ in recent)/len(recent)
    lppg=sum(_points(x,y) for x,y,_ in rows)/(3*len(rows))
    vppg=sum(_points(x,y) for x,y,_ in venue_rows)/(3*len(venue_rows)) if venue_rows else .5
    return Strength(_norm(lppg-.5,.35),_norm(ppg-.5,.35),_norm(gd,1.5),_norm(vppg-.5,.35),len(rows))
