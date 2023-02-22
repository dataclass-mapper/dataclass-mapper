from pydantic import BaseModel
from dataclass_mapper.mapper import mapper_from
from .base import Song as BaseSong

@mapper_from(BaseSong)
class Song(BaseModel):
    title: str
    length: int
    encoding: str