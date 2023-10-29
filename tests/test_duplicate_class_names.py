from dataclasses import dataclass

import pytest

from dataclass_mapper.implementations.pydantic_v1 import pydantic_version
from dataclass_mapper.mapper import map_to, mapper_from


def test_duplicate_class_name_in_different_scopes():
    @dataclass
    class SongData:
        title: str
        artist: str
        genre: str
        length: int
        encoding: str

    class Display:
        @mapper_from(SongData)
        @dataclass
        class Song:
            title: str
            artist: str
            genre: str

    class Technical:
        @mapper_from(SongData)
        @dataclass
        class Song:
            title: str
            length: int
            encoding: str

    base = SongData(
        title="Ode to Joy",
        artist="Friedrich Schiller",
        genre="classic",
        length=123,
        encoding="mp3",
    )

    display = map_to(base, Display.Song)
    technical = map_to(base, Technical.Song)

    assert display == Display.Song(
        title="Ode to Joy",
        artist="Friedrich Schiller",
        genre="classic",
    )

    assert technical == Technical.Song(
        title="Ode to Joy",
        length=123,
        encoding="mp3",
    )


@pytest.mark.skipif(pydantic_version()[0] == 0, reason="Requires Pydantic")
def test_duplicate_class_name_in_different_modules():
    from tests.models import base, display, technical

    base_song = base.SongData(
        title="Ode to Joy",
        artist="Friedrich Schiller",
        genre="classic",
        length=123,
        encoding="mp3",
    )
    display_song = map_to(base_song, display.Song)
    technical_song = map_to(base_song, technical.Song)

    assert display_song == display.Song(
        title="Ode to Joy",
        artist="Friedrich Schiller",
        genre="classic",
    )

    assert technical_song == technical.Song(
        title="Ode to Joy",
        length=123,
        encoding="mp3",
    )
