"""Live test entry point for Oddsklubben.

This intentionally stops after verifying the Bet365 candidate field until
league IDs and the full value/report pipeline are configured.
"""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import os
from src.bet365 import Bet365Client

TZ = ZoneInfo("Europe/Copenhagen")

def next_week(now=None):
    now = now or datetime.now(TZ)
    monday = (now + timedelta(days=(7-now.weekday()))).replace(hour=0, minute=0, second=0, microsecond=0)
    sunday = monday + timedelta(days=6, hours=23, minutes=59, seconds=59)
    return monday, sunday

def main():
    start, end = next_week()
    print(f"Oddsklubben live test: {start.isoformat()} -> {end.isoformat()}")
    client = Bet365Client()
    fixtures = client.fixtures(start, end)
    print(f"Scheduled fixtures returned by provider: {len(fixtures)}")
    print("API authentication and fixture retrieval succeeded.")
    print("Next step: map competition IDs and run Bet365 1X2/value filtering.")

if __name__ == "__main__":
    main()
