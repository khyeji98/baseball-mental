"""One historical game per manual invocation; not a production polling service."""

import argparse
import asyncio
import hashlib
import json
import re
from datetime import UTC, datetime

from app.config import Settings
from app.database import connect
from app.models import GameSnapshot
from app.repository import GameRepository
from workers.probe_kbo import RelayParser, fetch


def collect_snapshot(game_id: str, series_id: str) -> GameSnapshot:
    if not re.fullmatch(r"\d{8}[A-Z]{4}\d", game_id):
        raise ValueError("Invalid game ID")
    collected_at = datetime.now(UTC)
    html = fetch(
        "https://www.koreabaseball.com",
        "/Game/LiveTextView2.aspx",
        {
            "leagueId": "1",
            "seriesId": series_id,
            "gameId": game_id,
            "gyear": game_id[:4],
        },
    )
    relay = RelayParser()
    relay.feed(html)
    score = json.loads(
        fetch(
            "https://m.koreabaseball.com",
            "/ws/Kbo.asmx/GetLiveTextScore",
            {
                "le_id": "1",
                "sr_id": series_id,
                "g_id": game_id,
                "sc_id": "0",
            },
        )
    )
    rows = json.loads(score["resultTable"])["rows"]
    if len(rows) != 2 or not relay.lines:
        raise ValueError("Missing score or relay; refusing to persist")
    runs = [int(row["row"][0]["Text"]) for row in rows]
    canonical = json.dumps({"relay": relay.lines, "runs": runs}, ensure_ascii=False)
    return GameSnapshot(
        game_id=game_id,
        game_date=datetime.strptime(game_id[:8], "%Y%m%d").date(),
        series_id=series_id,
        away_team_id=game_id[8:10],
        home_team_id=game_id[10:12],
        away_runs=runs[0],
        home_runs=runs[1],
        collected_at=collected_at,
        relay_line_count=len(relay.lines),
        content_hash=hashlib.sha256(canonical.encode()).hexdigest(),
    )


async def run(game_id: str, series_id: str):
    settings = Settings()
    if not settings.enable_kbo_probe:
        raise ValueError("Set ENABLE_KBO_PROBE=true only for authorized source verification")
    client = await connect(settings)
    try:
        snapshot = await asyncio.to_thread(collect_snapshot, game_id, series_id)
        await GameRepository().save(snapshot)
        print(json.dumps({"game_id": game_id, "status": "stored-historical-probe"}))
    finally:
        await client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_id")
    parser.add_argument("--series-id", default="0")
    args = parser.parse_args()
    asyncio.run(run(args.game_id, args.series_id))
