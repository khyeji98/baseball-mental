from contextlib import asynccontextmanager
from datetime import date
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from pymongo.errors import PyMongoError

from app.config import Settings
from app.database import connect
from app.models import GameSnapshot
from app.repository import GameRepository


def repository(request: Request) -> GameRepository:
    if request.app.state.client is None:
        raise HTTPException(503, "Game storage is not configured")
    return GameRepository()


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.client = await connect(settings) if settings.mongodb_uri else None
        try:
            yield
        finally:
            if app.state.client is not None:
                await app.state.client.close()

    app = FastAPI(title="왜저럴까 API", version="0.1.0", lifespan=lifespan)

    @app.get("/health/live", tags=["health"])
    async def live() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/health/ready", tags=["health"])
    async def ready(request: Request) -> dict[str, str]:
        client = request.app.state.client
        if client is None:
            raise HTTPException(503, "Game storage is not configured")
        try:
            await client.admin.command("ping")
        except PyMongoError:
            raise HTTPException(503, "Game storage is unavailable") from None
        return {"status": "ok"}

    @app.get("/v1/games", response_model=list[GameSnapshot], tags=["games"])
    async def list_games(
        game_date: Annotated[date, Query()],
        repo: Annotated[GameRepository, Depends(repository)],
    ):
        try:
            return await repo.list_games(game_date)
        except PyMongoError:
            raise HTTPException(503, "Game storage is unavailable") from None

    @app.get("/v1/games/{game_id}", response_model=GameSnapshot, tags=["games"])
    async def get_game(game_id: str, repo: Annotated[GameRepository, Depends(repository)]):
        try:
            game = await repo.get_game(game_id)
        except PyMongoError:
            raise HTTPException(503, "Game storage is unavailable") from None
        if game is None:
            raise HTTPException(404, "Game not found")
        return game

    return app


app = create_app()
