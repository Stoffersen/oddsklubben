from dataclasses import dataclass
from math import exp

@dataclass
class TeamProfile:
    long_term: float
    recent_form: float
    xg_diff: float
    venue_form: float
    availability: float = 0.0

def _sigmoid(x):
    return 1.0 / (1.0 + exp(-x))

def estimate_1x2(home: TeamProfile, away: TeamProfile, home_advantage=0.16):
    """
    Explicit venue-aware model.
    venue_form = home team's HOME form / away team's AWAY form.
    Inputs should be normalized approximately around 0.
    """
    h = (0.34*home.long_term + 0.20*home.recent_form + 0.24*home.xg_diff
         + 0.14*home.venue_form + 0.08*home.availability + home_advantage)
    a = (0.34*away.long_term + 0.20*away.recent_form + 0.24*away.xg_diff
         + 0.14*away.venue_form + 0.08*away.availability)
    edge = h - a

    # Three-way approximation with draw probability higher for balanced games.
    draw = max(0.18, min(0.31, 0.29 - 0.07*abs(edge)))
    home_share = _sigmoid(1.35*edge)
    remaining = 1.0 - draw
    p1 = remaining * home_share
    p2 = remaining * (1.0-home_share)
    return {"1": p1, "X": draw, "2": p2}

def confidence(sample_games, data_completeness, lineup_confidence):
    sample = min(1.0, max(0.0, sample_games / 10.0))
    return 0.45*sample + 0.35*data_completeness + 0.20*lineup_confidence
