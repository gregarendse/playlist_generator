import json
import math
import requests

from os import path
from random import random

from hashlib import sha256
from base64 import b64encode

from typing import Dict, List
from requests.auth import HTTPBasicAuth

from .http import Authorization, HttpListener, authorization_token


class SpotifyAPI(object):

    @staticmethod
    def generateRandom(length: int) -> str:
        text: str = ''
        possible: str = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'

        for i in range(length):
            text += possible[math.floor(random() * len(possible))]

        return text

    @staticmethod
    def generateCodeChallenge(input: str):
        h = sha256()
        h.update(input.encode('utf-8'))

        b = b64encode(h.digest()).decode('utf-8')

        print(b)

        b = b.replace('+', '-')
        b = b.replace('/', '_')
        b = b.replace('=', '')

        print(b)

        return b

    code_verifier: str = None

    def __init__(self,
                 client_id: str,
                 client_secret: str,
                 grant_type: str = 'authorization_code',
                 redirect_uri: str = 'http://localhost:8080/callback',
                 scope: str = 'playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public'
                 ) -> None:
        self.state = self.generateRandom(16)
        self.grant_type = grant_type
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope

        if path.exists('playlister.key'):
            with open('playlister.key', 'r') as file:
                auth = json.loads(file.read())
                self.refresh_token = auth['refresh_token']

            token = self.get_token(
                'refresh_token', refresh_token=self.refresh_token)
            self.access_token = token['access_token']
        else:
            self.code_verifier = self.generateRandom(128)

            print(self.code_verifier)
            code_challenge: str = self.generateCodeChallenge(
                self.code_verifier)
            print(code_challenge)

            auth = requests.Request(
                method='GET',
                url='https://accounts.spotify.com/authorize',
                params={
                    'response_type': 'code',
                    'client_id': self.client_id,
                    'scope': self.scope,
                    'redirect_uri': self.redirect_uri,
                    'state': self.state
                }
            ).prepare()

            print(auth.url)

            self.code = authorization_token.code

            response: requests.Response = requests.post(
                'https://accounts.spotify.com/api/token',
                data={
                    'grant_type': 'authorization_code',
                    'code': self.code,
                    'redirect_uri': self.redirect_uri
                },
                auth=HTTPBasicAuth(self.client_id, self.client_secret)
            )

            with open('playlister.key', 'w+') as file:
                file.write(str(response.content))

            self.access_token = response.json()['access_token']

        self.s = requests.Session()
        self.s.headers.update({
            'Authorization': 'Bearer {}'.format(self.access_token)
        })

    def get_token(self, grant_type: str, code: str = None, refresh_token: str = None):
        data: Dict[str, str] = dict()
        data['grant_type'] = grant_type
        data['redirect_uri'] = self.redirect_uri

        if code is not None:
            data['code'] = code
        if refresh_token is not None:
            data['refresh_token'] = refresh_token

        response: requests.Response = requests.post(
            'https://accounts.spotify.com/api/token',
            data=data,
            auth=HTTPBasicAuth(self.client_id, self.client_secret)
        )

        return response.json()

    @staticmethod
    def match(left: str, right: str) -> bool:
        if left == right:
            return True

        left = str(left).upper().replace('-', ' ')
        right = str(right).upper().replace('-', ' ')

        length = min(len(left), len(right))

        if len(left) > len(right):
            for i in range(length):
                if left[i:length + i] == right[:]:
                    return True
        else:
            for i in range(length):
                if left[:] == right[i:length + i]:
                    return True

        return False

    def search(self, artist: str, title: str):

        params: Dict[str, str] = dict()
        params['type'] = 'track'
        params['q'] = "{} {}".format(title, artist)
        # params['q'] = "artist:{artist} track:{title}".format(
        #     artist=artist, title=title)

        request = self.s.prepare_request(
            requests.Request(
                method='GET',
                url='https://api.spotify.com/v1/search/',
                params=params
            )
        )

        tracks = self.s.send(request).json()['tracks']['items']

        for track in tracks:
            if self.match(track['name'], title) and self.match(track['artists'][0]['name'], artist):
                return track

        print(artist + " | " + title)
        for track in tracks:
            print(track['artists'][0]['name'] + " | " + track['name'])
        return None

    def get_playlists(self):
        request = self.s.prepare_request(
            requests.Request(
                method='GET',
                url='https://api.spotify.com/v1/me/playlists/'
            )
        )
        return self.s.send(request).json()

    def get_artist(self, id: str):
        response: requests.Response = requests.get(
            'https://api.spotify.com/v1/artists/{}'.format(id),
        )

        return response.json()

    def find_playlist(self, name: str):
        playlists: List[Dict[str, object]] = self.get_playlists()['items']

        playlists = list(
            filter(
                lambda playlist: playlist['name'] == name, playlists
            )
        )

        if len(playlists) == 0:
            print('Playlist not found')
            return None
        else:
            next = playlists[0]['tracks']['href']
            playlists[0]['tracks']['items'] = []
            while next is not None:
                response = self.s.get(next).json()
                next = response['next']
                playlists[0]['tracks']['items'].extend(response['items'])

            return playlists[0]

    def add_items_to_playlist(self, playlist_id: str, tracks: List[str]):

        if tracks is None:
            tracks = []

        data = {
            'uris': ['spotify:track:{}'.format(track) for track in tracks]
        }

        request = self.s.prepare_request(
            requests.Request(
                method='POST',
                url='https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
                    .format(playlist_id=playlist_id),
                json=data
            )
        )

        response = self.s.send(request)

        return response
