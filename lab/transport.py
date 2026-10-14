"""Small REST adapter. No SDK retry layer is hidden underneath this adapter."""
import json
import os
import socket
from urllib import request, error


class Failure(Exception):
    def __init__(self, code, status=None):
        self.code, self.status = code, status
        super().__init__(code)


class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


class Live:
    mode = 'live'

    def __init__(self):
        self.key = os.environ.get('OLOSTEP_API_KEY')
        if not self.key:
            raise Failure('missing_api_key')
        self.opener = request.build_opener(NoRedirect)

    def call(self, method, path, payload=None, timeout=10):
        if not path.startswith('/') or '://' in path:
            raise Failure('invalid_api_path')
        req = request.Request('https://api.olostep.com/v1' + path,
            data=json.dumps(payload).encode() if payload is not None else None,
            headers={'Authorization': 'Bearer ' + self.key,
                     'Content-Type': 'application/json'}, method=method)
        try:
            with self.opener.open(req, timeout=timeout) as response:
                raw = response.read(5_000_001)
                if len(raw) > 5_000_000:
                    raise Failure('response_too_large')
                data = json.loads(raw)
                if not isinstance(data, dict):
                    raise Failure('invalid_response')
                return data
        except error.HTTPError as exc:
            # Do not persist server bodies, URLs or request headers.
            raise Failure('http_error', exc.code) from None
        except (error.URLError, TimeoutError, socket.timeout):
            raise Failure('network_or_timeout') from None
        except (ValueError, UnicodeError):
            raise Failure('invalid_json') from None
