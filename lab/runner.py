"""Bounded lifecycle with evidence rather than optimistic success counters."""
import time
import re
import math
from datetime import datetime, timezone
from urllib.parse import urlencode, urlparse, quote
from .transport import Failure


class Runner:
    def __init__(self, transport, budget=30, attempts=3, clock=time.monotonic, sleep=time.sleep):
        if not math.isfinite(budget) or budget <= 0 or not 1 <= attempts <= 5:
            raise ValueError('Positive budget and 1..5 attempts required')
        self.api, self.budget, self.attempts = transport, budget, attempts
        self.clock, self.sleep = clock, sleep

    def event(self, action, outcome, **details):
        self.report['events'].append({'sequence': len(self.report['events']) + 1,
            'elapsed_seconds': round(self.clock() - self.start, 4),
            'action': action, 'outcome': outcome, **details})

    def remaining(self):
        seconds = self.deadline - self.clock()
        if seconds <= 0:
            raise Failure('deadline_exceeded')
        return seconds

    def pause(self, seconds):
        self.sleep(min(seconds, self.remaining()))
        self.remaining()

    def read(self, path):
        for attempt in range(self.attempts):
            try:
                result = self.api.call('GET', path, timeout=min(10, self.remaining()))
                self.remaining()
                return result
            except Failure as exc:
                retryable = exc.code == 'network_or_timeout' or exc.status in (429, 500, 502, 503, 504)
                if not retryable or attempt == self.attempts - 1:
                    raise
                self.report['read_retries'] += 1
                self.event('retry_read', 'scheduled', attempt=attempt + 1, reason=exc.code, status=exc.status)
                self.pause(2 ** attempt)

    def items(self, batch_id, status):
        cursor, seen = None, set()
        for _ in range(100):
            params = {'status': status, 'limit': 50}
            if cursor is not None:
                params['cursor'] = cursor
            page = self.read(f'/batches/{quote(batch_id, safe="")}/items?' + urlencode(params))
            if not isinstance(page.get('items'), list):
                raise Failure('invalid_items_response')
            self.event('list_items', 'received', category=status, count=len(page['items']))
            yield from page['items']
            cursor = page.get('cursor')
            if cursor is None or cursor == '':
                return
            if not isinstance(cursor, int) or isinstance(cursor, bool) or cursor < 0:
                raise Failure('invalid_cursor')
            key = str(cursor)
            if key in seen:
                raise Failure('repeated_cursor')
            seen.add(key)
        raise Failure('pagination_limit')

    def run(self, urls=None, batch_id=None):
        self.start = self.clock()
        self.deadline = self.start + self.budget
        self.report = {'schema_version': 1, 'mode': self.api.mode,
            'started_at': datetime.now(timezone.utc).isoformat(), 'status': 'running',
            'batch_id': batch_id, 'expected_items': len(urls) if urls else None,
            'credits': {'value': None, 'evidence': 'unknown'},
            'read_retries': 0, 'events': [], 'items': [],
            'policy': {'deadline_seconds': self.budget, 'read_attempts': self.attempts,
                       'create_attempts': 1},
            'limitations': ['Fixture responses are synthetic, not Olostep performance evidence.',
                           'Credits are not inferred from successful item counts.',
                           'Webhook inbox is a local simulation, not a public receiver.']}
        try:
            if not batch_id:
                if not urls or len(urls) > 10:
                    raise Failure('provide_1_to_10_urls')
                for url in urls:
                    parsed = urlparse(url)
                    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
                        raise Failure('use_public_https_urls_without_queries')
                self.event('create_batch', 'requested')
                try:
                    result = self.api.call('POST', '/batches',
                        {'items': [{'custom_id': f'page-{i+1}', 'url': url} for i, url in enumerate(urls)]},
                        timeout=min(10, self.remaining()))
                except Failure as exc:
                    if exc.code == 'network_or_timeout' or (exc.status and exc.status >= 500):
                        raise Failure('creation_unknown_do_not_resubmit') from None
                    raise
                batch_id = result.get('id')
                if not isinstance(batch_id, str) or not re.fullmatch(r'[\w-]+', batch_id):
                    raise Failure('invalid_batch_id')
                self.report['batch_id'] = batch_id
                self.event('create_batch', 'accepted', batch_id=batch_id)
            if not re.fullmatch(r'[\w-]+', batch_id):
                raise Failure('invalid_batch_id')
            while True:
                state = self.read('/batches/' + batch_id).get('status')
                self.event('poll', str(state))
                if state == 'completed':
                    break
                if state not in ('in_progress', 'pending', 'processing'):
                    raise Failure('unexpected_batch_state')
                self.pause(1)
            seen = set()
            for status in ('completed', 'failed'):
                for item in self.items(batch_id, status):
                    if not isinstance(item, dict) or not isinstance(item.get('custom_id'), str):
                        raise Failure('invalid_item')
                    identity = item['custom_id']
                    if identity in seen:
                        raise Failure('duplicate_item_identity')
                    seen.add(identity)
                    row = {'custom_id': identity, 'url': item.get('url'), 'status': status,
                           'evidence': self.api.mode, 'content': None}
                    self.report['items'].append(row)
                    if status == 'completed':
                        rid = item.get('retrieve_id')
                        if not isinstance(rid, str) or not rid:
                            row.update(status='unresolved', reason='missing_retrieve_id')
                        else:
                            try:
                                content = self.read('/retrieve?' + urlencode({'retrieve_id': rid, 'formats': 'markdown'}))
                                value = content.get('markdown_content')
                                if content.get('size_exceeded') is True:
                                    row.update(status='unresolved', reason='hosted_content_requires_review')
                                elif not isinstance(value, str) or not value.strip():
                                    row.update(status='unresolved', reason='missing_content')
                                else:
                                    row['content'] = value
                            except Failure as exc:
                                row.update(status='unresolved', reason=exc.code)
                                if exc.code == 'deadline_exceeded' or exc.status in (401, 403):
                                    raise
                    self.event('retrieve' if status == 'completed' else 'failed_item', row['status'], item=identity)
            expected = self.report['expected_items']
            if expected is not None and len(seen) != expected:
                raise Failure('item_count_mismatch')
            self.report['status'] = 'partial' if any(i['status'] != 'completed' for i in self.report['items']) else 'complete'
        except Failure as exc:
            self.report['status'] = 'incomplete'
            self.report['error'] = {'code': exc.code, 'http_status': exc.status}
            self.event('stop', exc.code)
        self.report['elapsed_seconds'] = round(self.clock() - self.start, 4)
        self.report['counts'] = {s: sum(i['status'] == s for i in self.report['items'])
                                 for s in ('completed', 'failed', 'unresolved')}
        return self.report
