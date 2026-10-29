import asyncio
import os
from datetime import timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.database import connect
from app.main import create_app
from app.models import SourceSnapshot
from app.repository import GameRepository
from tests.test_api import sample_snapshot


@pytest.mark.integration
def test_mongo_retry_correction_late_write_and_restart():
    uri = os.environ.get("TEST_MONGODB_URI")
    if not uri:
        pytest.skip("TEST_MONGODB_URI is required for Mongo integration")
    settings = Settings(
        _env_file=None, mongodb_uri=uri, mongodb_database="test_baseball_" + uuid4().hex
    )
    first = sample_snapshot()
    corrected = first.model_copy(
        update={
            "away_runs": 4,
            "content_hash": "b" * 64,
            "collected_at": first.collected_at + timedelta(seconds=60),
        }
    )

    async def populate():
        client = await connect(settings)
        try:
            repo = GameRepository()
            await asyncio.gather(repo.save(first), repo.save(first))
            await repo.save(corrected)
            await repo.save(first)  # Delayed worker cannot overwrite a newer snapshot.
            assert await SourceSnapshot.count() == 2
            assert (await repo.get_game(first.game_id)).away_runs == 4
        finally:
            await client.close()

    async def cleanup():
        client = await connect(settings)
        try:
            await client.drop_database(settings.mongodb_database)
        finally:
            await client.close()

    try:
        asyncio.run(populate())
        # New application connection proves persistence rather than in-memory fixtures.
        with TestClient(create_app(settings)) as client:
            assert client.get("/health/ready").status_code == 200
            result = client.get("/v1/games?game_date=2026-09-01")
            assert result.status_code == 200
            assert len(result.json()) == 1
            assert result.json()[0]["away_runs"] == 4
    finally:
        asyncio.run(cleanup())
