from datetime import UTC, date, datetime

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app, repository
from app.models import GameSnapshot


def sample_snapshot(**overrides):
    values = {
        "game_id": "20260901LGOB0",
        "game_date": date(2026, 9, 1),
        "series_id": "0",
        "away_team_id": "LG",
        "home_team_id": "OB",
        "away_runs": 3,
        "home_runs": 1,
        "collected_at": datetime(2026, 10, 29, tzinfo=UTC),
        "relay_line_count": 475,
        "content_hash": "a" * 64,
    }
    return GameSnapshot(**(values | overrides))


def test_unconfigured_storage_is_not_reported_as_empty_or_ready():
    with TestClient(create_app(Settings(_env_file=None, mongodb_uri=None))) as client:
        assert client.get("/health/live").status_code == 200
        assert client.get("/health/ready").status_code == 503
        assert client.get("/v1/games?game_date=2026-09-01").status_code == 503


def test_api_dates_not_found_and_source_provenance():
    snapshot = sample_snapshot()

    class FakeRepository:
        async def list_games(self, game_date):
            return [snapshot] if game_date == snapshot.game_date else []

        async def get_game(self, game_id):
            return snapshot if game_id == snapshot.game_id else None

    app = create_app(Settings(_env_file=None, mongodb_uri=None))
    app.dependency_overrides[repository] = FakeRepository
    with TestClient(app) as client:
        assert client.get("/v1/games?game_date=invalid").status_code == 422
        assert client.get("/v1/games?game_date=2026-09-02").json() == []
        assert client.get("/v1/games/missing").status_code == 404
        response = client.get("/v1/games?game_date=2026-09-01")
        assert response.status_code == 200
        assert response.json()[0]["verification"] == "historical-response-only"
        assert response.json()[0]["away_runs"] == 3
        assert client.get("/v1/games/20260901LGOB0").json() == response.json()[0]
