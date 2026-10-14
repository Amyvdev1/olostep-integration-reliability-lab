"""Synthetic responses shaped around the public batch reference, not recordings."""
from .transport import Failure

SCENARIOS = ('success', 'partial', 'transient', 'timeout', 'exhausted',
             'unauthorized', 'cursor-loop', 'missing-content', 'ambiguous-create')
URLS = ['https://example.com/quickstart', 'https://example.com/auth',
        'https://example.com/recovery']
CONTENT = {
    'ret_1': '# Quickstart\n\nSubmit known URLs, then retain the batch ID.\n\n```python\nbatch_id = "batch_example"\n```\n',
    'ret_2': '# Authentication\n\nKeep credentials in the environment.\n\n```sh\n# OLOSTEP_API_KEY is configured privately\n```\n',
    'ret_3': '# Recovery\n\nResume reads against the existing operation.\n\n| Outcome | Action |\n|---|---|\n| Timeout | Resume by ID |\n'
}


class Fixture:
    mode = 'fixture'

    def __init__(self, scenario='partial'):
        if scenario not in SCENARIOS:
            raise ValueError('Unknown scenario')
        self.scenario = scenario
        self.calls = []
        self.reads = 0

    def call(self, method, path, payload=None, timeout=10):
        self.calls.append((method, path))
        if self.scenario == 'unauthorized':
            raise Failure('http_error', 401)
        if method == 'POST':
            if self.scenario == 'ambiguous-create':
                raise Failure('network_or_timeout')
            return {'id': 'batch_fixture', 'status': 'in_progress'}
        if path == '/batches/batch_fixture':
            self.reads += 1
            if self.scenario == 'exhausted' or (self.scenario == 'transient' and self.reads == 1):
                raise Failure('http_error', 503)
            return {'id': 'batch_fixture', 'total_urls': 3, 'status': 'in_progress' if
                    self.scenario == 'timeout' or self.reads == 1 else 'completed'}
        if '/items?' in path:
            failed = 'status=failed' in path
            partial = self.scenario == 'partial'
            if failed:
                return {'items': [{'custom_id': 'page-3', 'url': URLS[2]}] if partial else []}
            items = [{'custom_id': f'page-{n}', 'url': URLS[n-1], 'retrieve_id': f'ret_{n}'}
                     for n in range(1, 3 if partial else 4)]
            if 'cursor=2' in path:
                result = {'items': items[2:]}
            else:
                result = {'items': items[:2], 'cursor': 2}
            if self.scenario == 'cursor-loop':
                result['cursor'] = 2
            return result
        if path.startswith('/retrieve?'):
            if self.scenario == 'missing-content' and 'ret_2' in path:
                return {'markdown_content': None}
            from urllib.parse import urlparse, parse_qs
            rid = parse_qs(urlparse(path).query).get('retrieve_id', [''])[0]
            return {'markdown_content': CONTENT.get(rid)}
        raise Failure('unexpected_fixture_request')
