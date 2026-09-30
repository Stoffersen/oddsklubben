"""Bet365 1X2 adapter using 5DollarFootballAPI."""
from __future__ import annotations
import os, time
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Iterable
import requests

BASE_URL = "https://api.5dollarfootballapi.com/v1"
BOOKMAKER = "bet365"

@dataclass(frozen=True)
class Bet365Quote:
    fixture_id: int
    home: str
    away: str
    kickoff: datetime
    league_id: int | None
    league: str
    home_odds: float
    draw_odds: float
    away_odds: float
    quoted_at: datetime | None

class Bet365Client:
    def __init__(self, api_key: str | None = None, timeout: int = 20,
                 min_request_interval: float = 1.05):
        self.api_key = api_key or os.getenv("FIVE_DOLLAR_FOOTBALL_API_KEY")
        if not self.api_key:
            raise RuntimeError("FIVE_DOLLAR_FOOTBALL_API_KEY is not set")
        self.timeout = timeout
        self.min_request_interval = min_request_interval
        self._last_request = 0.0

    def _get(self, path: str, **params):
        # Free tier is 60 requests/hour. Pace calls and honor Retry-After.
        wait = self.min_request_interval - (time.monotonic() - self._last_request)
        if wait > 0:
            time.sleep(wait)
        for attempt in range(4):
            r = requests.get(
                f"{BASE_URL}{path}", params=params,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=self.timeout,
            )
            self._last_request = time.monotonic()
            if r.status_code != 429:
                r.raise_for_status()
                payload = r.json()
                if isinstance(payload, dict) and payload.get("success") == 0:
                    raise RuntimeError(f"API request failed: {payload}")
                return payload.get("data", payload) if isinstance(payload, dict) else payload
            retry = r.headers.get("Retry-After")
            # Avoid sleeping for an hour in CI. Short retry windows are retried;
            # exhausted hourly quota fails clearly and the next run can resume later.
            delay = float(retry) if retry and retry.replace(".", "", 1).isdigit() else 5.0 * (attempt + 1)
            if delay > 60:
                raise RuntimeError(f"API rate limit exhausted; Retry-After={retry}s")
            time.sleep(delay)
        raise RuntimeError("API rate limit persisted after retries")

    def fixtures(self, start: datetime, end: datetime) -> list[dict]:
        out=[]; cursor=start
        while cursor <= end:
            window_end=min(end, cursor + timedelta(hours=23, minutes=59, seconds=59))
            page=1
            while True:
                data=self._get("/fixtures", start_time=int(cursor.timestamp()),
                    end_time=int((window_end + timedelta(seconds=1)).timestamp()),
                    status="scheduled", esports="false", page=page, per_page=100)
                items=(data.get("fixtures") or data.get("items") or data.get("data") or []) if isinstance(data,dict) else (data or [])
                out.extend(items)
                if len(items)<100: break
                page+=1
            cursor=window_end + timedelta(seconds=1)
        return out

    @staticmethod
    def _kickoff(fixture: dict) -> datetime:
        ts=fixture.get("kickoff_ts")
        if isinstance(ts,(int,float)):
            return datetime.fromtimestamp(ts,tz=timezone.utc)
        raw=fixture.get("kickoff_utc") or fixture.get("start_time") or fixture.get("date") or fixture.get("kickoff")
        if not raw:
            raise ValueError(f"Fixture {fixture.get('id')} has no kickoff timestamp")
        return datetime.fromisoformat(str(raw).replace("Z","+00:00"))

    def quote_1x2(self, fixture: dict) -> Bet365Quote | None:
        fixture_id=int(fixture.get("id") or fixture.get("fixture_id"))
        data=self._get(f"/fixtures/{fixture_id}/odds", bookmakers=BOOKMAKER, market="1x2")
        books=(data or {}).get("bookmakers",[]) if isinstance(data,dict) else []
        book=next((b for b in books if str(b.get("slug","")).lower()==BOOKMAKER),None)
        if not book: return None
        market=(book.get("odds") or {}).get("1x2") or {}
        # Provider defines closing as latest pre-match quote before kickoff.
        price=market.get("closing") or market.get("opening")
        if not price or not all(price.get(k) is not None for k in ("home","draw","away")):
            return None
        league=fixture.get("league") or {}
        teams=fixture.get("teams") or {}
        home=teams.get("home") or fixture.get("home") or fixture.get("home_team") or {}
        away=teams.get("away") or fixture.get("away") or fixture.get("away_team") or {}
        at=price.get("at")
        quoted_at=datetime.fromtimestamp(at,tz=timezone.utc) if isinstance(at,(int,float)) else None
        return Bet365Quote(
            fixture_id=fixture_id,
            home=home.get("name","") if isinstance(home,dict) else str(home),
            away=away.get("name","") if isinstance(away,dict) else str(away),
            kickoff=self._kickoff(fixture),
            league_id=league.get("id") if isinstance(league,dict) else None,
            league=league.get("name","") if isinstance(league,dict) else str(league),
            home_odds=float(price["home"]), draw_odds=float(price["draw"]),
            away_odds=float(price["away"]), quoted_at=quoted_at)

    def verified_quotes(self,start:datetime,end:datetime,allowed_league_ids:Iterable[int])->list[Bet365Quote]:
        allowed=set(allowed_league_ids); out=[]
        for fixture in self.fixtures(start,end):
            league=fixture.get("league") or {}
            league_id=league.get("id") if isinstance(league,dict) else None
            if league_id not in allowed: continue
            q=self.quote_1x2(fixture)
            if q is not None: out.append(q)
        return sorted(out,key=lambda q:q.kickoff)
