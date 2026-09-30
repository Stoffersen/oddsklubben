"""Bet365-only 1X2 adapter via Odds-API.io v3.

Set ODDS_API_KEY in the runtime environment. No key is stored in Git.
"""
from __future__ import annotations
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable
import requests

BASE_URL = "https://api.odds-api.io/v3"
BOOKMAKER = "Bet365"

@dataclass(frozen=True)
class Bet365Quote:
    event_id: int
    home: str
    away: str
    kickoff: datetime
    league: str
    home_odds: float
    draw_odds: float
    away_odds: float
    updated_at: datetime | None

class Bet365Client:
    def __init__(self, api_key: str | None = None, timeout: int = 20):
        self.api_key = api_key or os.getenv("ODDS_API_KEY")
        if not self.api_key:
            raise RuntimeError("ODDS_API_KEY is not set")
        self.timeout = timeout

    def _get(self, path: str, **params):
        params["apiKey"] = self.api_key
        r = requests.get(f"{BASE_URL}{path}", params=params, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def events(self, league: str) -> list[dict]:
        data = self._get("/events", sport="football", league=league,
                         status="pending", bookmaker=BOOKMAKER)
        return data if isinstance(data, list) else data.get("events", data.get("items", []))

    def quote_1x2(self, event: dict) -> Bet365Quote | None:
        data = self._get("/odds", eventId=event["id"],
                         bookmakers=BOOKMAKER, markets="ML")
        markets = data.get("bookmakers", {}).get(BOOKMAKER, [])
        ml = next((m for m in markets if m.get("name") == "ML"), None)
        if not ml or not ml.get("odds"):
            return None
        row = ml["odds"][0]
        if not all(row.get(k) for k in ("home", "draw", "away")):
            return None
        kickoff = datetime.fromisoformat(event["date"].replace("Z", "+00:00"))
        updated = ml.get("updatedAt")
        return Bet365Quote(
            event_id=int(event["id"]), home=event["home"], away=event["away"],
            kickoff=kickoff, league=event.get("league", {}).get("slug", ""),
            home_odds=float(row["home"]), draw_odds=float(row["draw"]),
            away_odds=float(row["away"]),
            updated_at=datetime.fromisoformat(updated.replace("Z", "+00:00")) if updated else None,
        )

    def verified_quotes(self, leagues: Iterable[str], start: datetime, end: datetime) -> list[Bet365Quote]:
        """Only return matches with a current, complete Bet365 ML/1X2 board."""
        out: list[Bet365Quote] = []
        for league in leagues:
            for event in self.events(league):
                kickoff = datetime.fromisoformat(event["date"].replace("Z", "+00:00"))
                if start <= kickoff <= end:
                    quote = self.quote_1x2(event)
                    if quote is not None:
                        out.append(quote)
        return sorted(out, key=lambda q: q.kickoff)
