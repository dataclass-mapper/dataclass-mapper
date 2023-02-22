from pydantic import BaseModel

from dataclass_mapper.mapper import map_to, mapper_from


def test_duplicate_class_name_in_different_scopes():
    song_class = {}

    def initialiser():
        
        def base_initializer():
            class Song(BaseModel):
                title: str
                artist: str
                genre: str
                length: int
                encoding: str
            song_class['base'] = Song

        base_initializer()

        def display_initializer():
            @mapper_from(song_class['base'])
            class Song(BaseModel):
                title: str
                artist: str
                genre: str
            song_class['display'] = Song
            
        display_initializer()

        def technical_initializer():
            @mapper_from(song_class['base'])
            class Song(BaseModel):
                title: str
                length: int
                encoding: str
            song_class['technical'] = Song

        technical_initializer()
    initialiser()

    base = song_class['base'].construct(
        title="Ode to Joy",
        artist="Friedrich Schiller",
        genre="classic",
        length=123,
        encoding="mp3",
        )
    
    display = map_to(base, song_class['display'])
    technical = map_to(base, song_class['technical'])

    assert display == song_class['display'].construct(
        title="Ode to Joy",
        artist="Friedrich Schiller",
        genre="classic",
    )

    assert technical == song_class['technical'].construct(
        title="Ode to Joy",
        length=123,
        encoding="mp3",
    )

def test_duplicate_class_name_in_different_modules():
    from .models import base, display, technical
    base_song = base.Song.construct(
        title="Ode to Joy",
        artist="Friedrich Schiller",
        genre="classic",
        length=123,
        encoding="mp3",
    )
    display_song = map_to(base_song, display.Song)
    technical_song = map_to(base_song, technical.Song)

    assert display_song == display.Song.construct(
        title="Ode to Joy",
        artist="Friedrich Schiller",
        genre="classic",
    )

    assert technical_song == technical.Song.construct(
        title="Ode to Joy",
        length=123,
        encoding="mp3",
    )
