#!/usr/bin/env python3

from typing import List

from requests_html import HTMLSession

from ..Track import Track


class FXAlternative(object):

    url: str = None

    def __init__(self, url: str = "https://mytuner-radio.com/radio/fx-alternative-radio-456034/") -> None:
        self.session = HTMLSession()
        self.url = url

    def get_song_history(self) -> List[Track]:
        r = self.session.get(self.url)
        r.html.render()

        song_history = r.html.find('div.previous-songs div.history-song')

        tracks: List[Track] = []

        for song in song_history:
            track = Track(
                artist=str(song.find('span.artist-name', first=True).text),
                title=str(song.find('span.song-name > p', first=True).text).replace(' (Radio Edit)', '')
            )
            tracks.append(track)

        return tracks
