from pydantic import BaseModel


class SongData(BaseModel):
    title: str
    artist: str
    genre: str
    length: int
    encoding: str
