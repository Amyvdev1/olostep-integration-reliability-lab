import copy
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from lab.fixtures import Fixture, URLS
from lab.runner import Runner
from lab.transport import Failure, Live
from lab.inbox import Inbox
from lab.reports import save, markdown


class Clock:
    def __init__(self): self.value = 0
    def now(self): return self.value
    def sleep(self, seconds): self.value += seconds


def execute(scenario='success', api=None, **kwargs):
    clock = Clock()
    return Runner(api or Fixture(scenario), clock=clock.now, sleep=clock.sleep,
                  budget=5, **kwargs).run(URLS)


class WorkflowTests(unittest.TestCase):
    def test_success_paginates_and_retrieves_all(self):
        report = execute()
        self.assertEqual(report['counts']['completed'], 3)
        self.assertEqual(report['status'], 'complete')
        self.assertTrue(all(i['content'] for i in report['items']))

    def test_partial_completion_is_not_full_success(self):
        report = execute('partial')
        self.assertEqual(report['status'], 'partial')
        self.assertEqual(report['counts'], {'completed': 2, 'failed': 1, 'unresolved': 0})

    def test_transient_read_is_retried_once(self):
        report = execute('transient')
        self.assertEqual(report['status'], 'complete')
        self.assertEqual(report['read_retries'], 1)

    def test_deadline_retains_resume_id(self):
        report = execute('timeout')
        self.assertEqual(report['error']['code'], 'deadline_exceeded')
        self.assertEqual(report['batch_id'], 'batch_fixture')
        self.assertEqual(report['elapsed_seconds'], 5)

    def test_exhaustion_is_bounded(self):
        report = execute('exhausted')
        self.assertEqual(report['status'], 'incomplete')
        self.assertEqual(report['read_retries'], 2)

    def test_unauthorized_is_not_retried(self):
        api = Fixture('unauthorized')
        report = execute(api=api)
        self.assertEqual(len(api.calls), 1)
        self.assertEqual(report['error']['http_status'], 401)

    def test_repeated_cursor_stops(self):
        self.assertEqual(execute('cursor-loop')['error']['code'], 'repeated_cursor')

    def test_unknown_credits_are_not_zero(self):
        self.assertIsNone(execute()['credits']['value'])

    def test_null_content_is_unresolved(self):
        report = execute('missing-content')
        self.assertEqual(report['status'], 'partial')
        self.assertEqual(report['counts']['unresolved'], 1)

    def test_ambiguous_creation_never_retries(self):
        api = Fixture('ambiguous-create')
        report = execute(api=api)
        self.assertEqual(len(api.calls), 1)
        self.assertEqual(report['error']['code'], 'creation_unknown_do_not_resubmit')

    def test_resume_does_not_create(self):
        api, clock = Fixture('success'), Clock()
        report = Runner(api, clock=clock.now, sleep=clock.sleep).run(batch_id='batch_fixture')
        self.assertEqual(report['status'], 'complete')
        self.assertTrue(all(method == 'GET' for method, _ in api.calls))

    def test_invalid_id_never_reaches_transport(self):
        api = Fixture()
        result = Runner(api).run(batch_id='../other')
        self.assertEqual(result['error']['code'], 'invalid_batch_id')
        self.assertEqual(api.calls, [])

    def test_secret_in_url_is_rejected(self):
        api = Fixture()
        report = Runner(api).run(['https://example.com/?token=secret'])
        self.assertEqual(api.calls, [])
        self.assertNotIn('secret', json.dumps(report))

    def test_empty_urls_rejected(self):
        self.assertEqual(Runner(Fixture()).run([])['status'], 'incomplete')

    def test_bad_policy_rejected(self):
        for value in (0, -1, float('nan'), float('inf')):
            with self.assertRaises(ValueError): Runner(Fixture(), budget=value)

    def test_missing_live_key(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(Failure, 'missing_api_key'): Live()

    def test_export_labels_fixture_and_preserves_unknown(self):
        report = execute('partial')
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as folder:
            save(report, folder)
            data = json.loads((Path(folder) / 'evidence.json').read_text())
            self.assertIsNone(data['credits']['value'])
            self.assertIn('**fixture**', markdown(data))
            self.assertIn('partial', markdown(data))

    def test_malformed_item_response(self):
        class Bad(Fixture):
            def call(self, method, path, payload=None, **kwargs):
                if '/items?' in path: return {'items': None}
                return super().call(method, path, payload, **kwargs)
        self.assertEqual(execute(api=Bad())['error']['code'], 'invalid_items_response')


class InboxTests(unittest.TestCase):
    def test_duplicate_persists_across_restarts_and_conflicts_rejected(self):
        event = {'id': 'event_1', 'object': 'event.batch.completed',
                 'delivery_attempt': '1/5', 'data': {'id': 'batch_1', 'items_completed': 2}}
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as folder:
            path = str(Path(folder) / 'inbox.sqlite')
            inbox = Inbox(path)
            self.assertEqual(inbox.accept(event, 'batch_1'), 'accepted_notification')
            inbox.close()
            inbox = Inbox(path)
            event['delivery_attempt'] = '2/5'
            self.assertEqual(inbox.accept(event, 'batch_1'), 'duplicate_ignored')
            changed = copy.deepcopy(event)
            changed['data']['items_completed'] = 99
            self.assertEqual(inbox.accept(changed, 'batch_1'), 'conflict_rejected')
            self.assertEqual(inbox.accept(event, 'wrong_batch'), 'rejected')
            inbox.close()

    def test_malformed_event_rejected(self):
        inbox = Inbox(':memory:')
        for event in (None, {}, {'id': 2}, {'data': []}):
            self.assertEqual(inbox.accept(event, 'batch_1'), 'rejected')
        inbox.close()


if __name__ == '__main__': unittest.main()
