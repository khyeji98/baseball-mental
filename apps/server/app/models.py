from datetime import date
from typing import ClassVar, Literal

from beanie import Document
from pydantic import AwareDatetime, BaseModel, Field
from pymongo import ASCENDING, IndexModel


class GameSnapshot(BaseModel):
    game_id: str = Field(pattern=r"^\d{8}[A-Z]{4}\d$")
    game_date: date
    series_id: str
    away_team_id: str
    home_team_id: str
    away_runs: int = Field(ge=0)
    home_runs: int = Field(ge=0)
    collected_at: AwareDatetime
    source: Literal["kbo-public-probe"] = "kbo-public-probe"
    verification: Literal["historical-response-only"] = "historical-response-only"
    # HTML line count is not a plate-appearance count or normalized event stream.
    relay_line_count: int = Field(gt=0)
    content_hash: str = Field(pattern=r"^[a-f0-9]{64}$")


class GameRecord(Document):
    snapshot: GameSnapshot

    class Settings:
        name = "games"
        indexes: ClassVar[list[IndexModel]] = [
            IndexModel([("snapshot.game_id", ASCENDING)], unique=True)
        ]


class SourceSnapshot(Document):
    snapshot: GameSnapshot

    class Settings:
        name = "source_snapshots"
        indexes: ClassVar[list[IndexModel]] = [
            IndexModel(
                [("snapshot.game_id", ASCENDING), ("snapshot.content_hash", ASCENDING)], unique=True
            )
        ]
