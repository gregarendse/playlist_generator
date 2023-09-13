import sys

from typing import Dict, List
from yaml import safe_load

from .Track import Track
from .spotify.api import SpotifyAPI
from .fx_alternative.FXAlternative import FXAlternative


def main():
    with open(sys.argv[1], 'r') as file:
        config = safe_load(file)

    spotify = SpotifyAPI(
        grant_type=config['spotify']['grant_type'],
        client_id=config['spotify']['client_id'],
        client_secret=config['spotify']['client_secret'],
        redirect_uri=config['spotify']['redirect_uri'],
        scope=config['spotify']['scope'],
    )
    fx_alternative = FXAlternative()

    tracks: List[Track] = fx_alternative.get_song_history()

    playlist = spotify.find_playlist(name='FX Alternative')

    for track in tracks:
        spotify_track = spotify.search(artist=track.artist, title=track.title)

        if spotify_track is not None:
            track.id = spotify_track['id']
        else:
            print(
                "Track not found - {} : {} : {}"
                .format(track.id, track.artist, track.title)
            )

    adding: List[Track] = []
    exiting_ids: List[str] = [existing['track']['id']
                              for existing in playlist['tracks']['items']]
    for track in tracks:
        if track.id is None:
            continue
        if track.id in exiting_ids:
            continue
        adding.append(track)

    response = spotify.add_items_to_playlist(
        playlist_id=playlist['id'],
        tracks=[track.id for track in adding]
    )
    print(response.json())


if __name__ == "__main__":
    main()
