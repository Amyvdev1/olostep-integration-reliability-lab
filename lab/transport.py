"""Small REST adapter. No SDK retry layer is hidden underneath this adapter."""
import json
import os
import socket
import math
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib import request, error


class Failure(Exception):
    def __init__(self, code, status=None, retry_after=None):
        self.code, self.status = code, status
        self.retry_after = retry_after
        super().__init__(code)


class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def retry_delay(header):
    if header is None:
        return None
    try:
        seconds = float(header)
    except (ValueError, TypeError):
        try:
            date = parsedate_to_datetime(header)
            if date.tzinfo is None:
                date = date.replace(tzinfo=timezone.utc)
            seconds = max(0, (date - datetime.now(timezone.utc)).total_seconds())
        except (ValueError, TypeError, OverflowError):
            return None
    return seconds if math.isfinite(seconds) and seconds >= 0 else None


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
            raise Failure('http_error', exc.code,
                          retry_delay(exc.headers.get('Retry-After')) if exc.headers else None) from None
        except (error.URLError, TimeoutError, socket.timeout):
            raise Failure('network_or_timeout') from None
        except (ValueError, UnicodeError):
            raise Failure('invalid_json') from None
