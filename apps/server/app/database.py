from beanie import init_beanie
from pymongo import AsyncMongoClient

from app.config import Settings
from app.models import GameRecord, SourceSnapshot


async def connect(settings: Settings):
    if settings.mongodb_uri is None:
        raise ValueError("MONGODB_URI is required")
    client = AsyncMongoClient(
        settings.mongodb_uri.get_secret_value(), serverSelectionTimeoutMS=3000, tz_aware=True
    )
    try:
        await client.admin.command("ping")
        await init_beanie(
            database=client[settings.mongodb_database],
            document_models=[GameRecord, SourceSnapshot],
        )
    except Exception:
        await client.close()
        raise
    return client
