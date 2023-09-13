from dataclasses import dataclass


@dataclass
class Track(object):
    title: str = None
    artist: str = None
    id: str = None

    def __str__(self) -> str:
        return "{id}: {artist} - {title}".format(id=self.id, artist=self.artist, title=self.title)
