from pydantic import BaseModel
from dataclass_mapper.mapper import mapper_from
from .base import SongData as BaseSong

@mapper_from(BaseSong)
class Song(BaseModel):
    title: str
    artist: str
    genre: str
