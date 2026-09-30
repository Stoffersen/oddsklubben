"""Bet365 1X2 adapter using 5DollarFootballAPI.

Set FIVE_DOLLAR_FOOTBALL_API_KEY in the runtime environment.
"""
from __future__ import annotations
import os
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
    def __init__(self, api_key: str | None = None, timeout: int = 20):
        self.api_key = api_key or os.getenv("FIVE_DOLLAR_FOOTBALL_API_KEY")
        if not self.api_key:
            raise RuntimeError("FIVE_DOLLAR_FOOTBALL_API_KEY is not set")
        self.timeout = timeout

    def _get(self, path: str, **params):
        r = requests.get(
            f"{BASE_URL}{path}",
            params=params,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=self.timeout,
        )
        r.raise_for_status()
        payload = r.json()
        if isinstance(payload, dict) and payload.get("success") == 0:
            raise RuntimeError(f"API request failed: {payload}")
        return payload.get("data", payload) if isinstance(payload, dict) else payload

    def fixtures(self, start: datetime, end: datetime) -> list[dict]:
        """Fetch scheduled fixtures in <=24-hour windows."""
        out = []
        cursor = start
        while cursor <= end:
            window_end = min(end, cursor + timedelta(hours=23, minutes=59, seconds=59))
            page = 1
            while True:
                data = self._get(
                    "/fixtures",
                    start_time=int(cursor.timestamp()),
                    end_time=int(window_end.timestamp()),
                    status="scheduled",
                    esports="false",
                    page=page,
                    per_page=100,
                )
                if isinstance(data, dict):
                    items = data.get("fixtures") or data.get("items") or data.get("data") or []
                else:
                    items = data or []
                out.extend(items)
                if len(items) < 100:
                    break
                page += 1
            cursor = window_end + timedelta(seconds=1)
        return out

    def quote_1x2(self, fixture: dict) -> Bet365Quote | None:
        fixture_id = int(fixture.get("id") or fixture.get("fixture_id"))
        data = self._get(
            f"/fixtures/{fixture_id}/odds",
            bookmakers=BOOKMAKER,
            market="1x2",
        )
        books = (data or {}).get("bookmakers", []) if isinstance(data, dict) else []
        book = next((b for b in books if str(b.get("slug", "")).lower() == BOOKMAKER), None)
        if not book:
            return None
        market = (book.get("odds") or {}).get("1x2") or {}
        price = market.get("closing") or market.get("opening")
        if not price or not all(price.get(k) is not None for k in ("home", "draw", "away")):
            return None

        league = fixture.get("league") or {}
        home = fixture.get("home") or fixture.get("home_team") or {}
        away = fixture.get("away") or fixture.get("away_team") or {}
        raw = fixture.get("start_time") or fixture.get("date") or fixture.get("kickoff")
        kickoff = (
            datetime.fromtimestamp(raw, tz=timezone.utc)
            if isinstance(raw, (int, float))
            else datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        )
        at = price.get("at")
        quoted_at = datetime.fromtimestamp(at, tz=timezone.utc) if isinstance(at, (int, float)) else None
        return Bet365Quote(
            fixture_id=fixture_id,
            home=home.get("name", "") if isinstance(home, dict) else str(home),
            away=away.get("name", "") if isinstance(away, dict) else str(away),
            kickoff=kickoff,
            league_id=league.get("id") if isinstance(league, dict) else None,
            league=league.get("name", "") if isinstance(league, dict) else str(league),
            home_odds=float(price["home"]),
            draw_odds=float(price["draw"]),
            away_odds=float(price["away"]),
            quoted_at=quoted_at,
        )

    def verified_quotes(self, start: datetime, end: datetime,
                        allowed_league_ids: Iterable[int]) -> list[Bet365Quote]:
        """Only fixtures in scope with a complete, verifiable Bet365 1X2 quote."""
        allowed = set(allowed_league_ids)
        out = []
        for fixture in self.fixtures(start, end):
            league = fixture.get("league") or {}
            league_id = league.get("id") if isinstance(league, dict) else None
            if league_id not in allowed:
                continue
            quote = self.quote_1x2(fixture)
            if quote is not None:
                out.append(quote)
        return sorted(out, key=lambda q: q.kickoff)
