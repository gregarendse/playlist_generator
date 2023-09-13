
from dataclasses import dataclass
import json
from functools import cached_property
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qsl, urlparse

import threading

@dataclass
class Authorization(object):
    code: str = None

authorization_token = Authorization()

class WebRequestHandler(BaseHTTPRequestHandler):

    @cached_property
    def url(self):
        return urlparse(self.path)

    @cached_property
    def query_data(self):
        return dict(parse_qsl(self.url.query))

    @cached_property
    def post_data(self):
        content_length = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(content_length)

    @cached_property
    def form_data(self):
        return dict(parse_qsl(self.post_data.decode("utf-8")))

    @cached_property
    def cookies(self):
        return SimpleCookie(self.headers.get("Cookie"))

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(self.get_response().encode("utf-8"))

    def do_POST(self):
        self.do_GET()

    def get_response(self):
        if self.url.path == '/callback':
            authorization_token.code = self.query_data['code']
            threading.Thread(target=self.server.shutdown, daemon=True).start()
            # self.server.shutdown_request(request=self.request)
        return json.dumps(
            {
                "path": self.url.path,
                "query_data": self.query_data,
            }
        )


class HttpListener(object):
    server = HTTPServer(("0.0.0.0", 8080), WebRequestHandler)

    def __init__(self) -> None:
        self.server.serve_forever()
