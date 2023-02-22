from pydantic import BaseModel


class Song(BaseModel):
            title: str
            artist: str
            genre: str
            length: int
            encoding: str
