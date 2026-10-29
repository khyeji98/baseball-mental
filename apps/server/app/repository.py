from datetime import date

from pymongo.errors import DuplicateKeyError

from app.models import GameRecord, GameSnapshot, SourceSnapshot


class GameRepository:
    async def list_games(self, game_date: date) -> list[GameSnapshot]:
        records = (
            await GameRecord.find({"snapshot.game_date": game_date.isoformat()})
            .sort("snapshot.game_id")
            .limit(100)
            .to_list()
        )
        return [item.snapshot for item in records]

    async def get_game(self, game_id: str) -> GameSnapshot | None:
        record = await GameRecord.find_one({"snapshot.game_id": game_id})
        return record.snapshot if record else None

    async def save(self, snapshot: GameSnapshot) -> None:
        # Retain distinct source versions, and do not double-count identical retries.
        data = snapshot.model_dump(mode="json")
        # Mongo stores this as a date, allowing chronological comparison for delayed workers.
        data["collected_at"] = snapshot.collected_at
        history = SourceSnapshot.get_pymongo_collection()
        try:
            await history.update_one(
                {
                    "snapshot.game_id": snapshot.game_id,
                    "snapshot.content_hash": snapshot.content_hash,
                },
                {"$setOnInsert": {"snapshot": data}},
                upsert=True,
            )
        except DuplicateKeyError:
            pass  # Concurrent identical snapshot already recorded.
        games = GameRecord.get_pymongo_collection()
        try:
            await games.update_one(
                {"snapshot.game_id": snapshot.game_id},
                {"$setOnInsert": {"snapshot": data}},
                upsert=True,
            )
        except DuplicateKeyError:
            pass
        await games.update_one(
            {
                "snapshot.game_id": snapshot.game_id,
                "snapshot.collected_at": {"$lte": snapshot.collected_at},
            },
            {"$set": {"snapshot": data}},
        )
