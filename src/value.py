from dataclasses import dataclass
@dataclass(frozen=True)
class Pick:
    fixture_id:int; league:str; match:str; selection:str; odds:float
    probability:float; fair_odds:float; ev:float; confidence:float
def picks_for_quote(q, probs, conf):
    odds={"1":q.home_odds,"X":q.draw_odds,"2":q.away_odds}; out=[]
    for s,p in probs.items():
        o=odds[s]; ev=p*o-1
        if ev>0:
            out.append(Pick(q.fixture_id,q.league,f"{q.home} v {q.away}",s,o,p,1/p,ev,conf))
    return out
