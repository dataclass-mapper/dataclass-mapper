from pydantic import BaseModel

from dataclass_mapper.mapper import mapper_from
from tests.models.base import SongData as BaseSong


@mapper_from(BaseSong)
class Song(BaseModel):
    title: str
    length: int
    encoding: str
