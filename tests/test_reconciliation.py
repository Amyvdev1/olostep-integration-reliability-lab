import json
import tempfile
import unittest
from pathlib import Path
from lab.fixtures import Fixture, URLS
from lab.runner import Runner
from lab.transport import Failure, retry_delay
from lab.checkpoints import load, save
from lab.reports import markdown
from test_workflow import Clock, execute


class ReconciliationTests(unittest.TestCase):
    def test_checkpoint_storage_failure_preserves_batch_without_recreating(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            blocked = Path(directory) / 'not-a-directory'
            blocked.write_text('occupied', encoding='utf-8')
            api = Fixture('success')
            report = Runner(api, checkpoint_dir=blocked).run(URLS)
            self.assertEqual(report['error']['code'], 'checkpoint_write_failed')
            self.assertEqual(report['batch_id'], 'batch_fixture')
            self.assertEqual(len(api.calls), 1)
            self.assertEqual(api.calls[0][0], 'POST')

    def test_human_report_preserves_unknown_usage_and_reconciliation_basis(self):
        report = execute('success')
        text = markdown(report)
        self.assertIn('Cost USD: **unknown** (unknown', text)
        self.assertIn('Verification basis: `manifest`', text)
        self.assertIn('Missing IDs: []', text)

    def test_retry_after_is_respected_within_budget(self):
        class Limited(Fixture):
            def call(self, method, path, payload=None, **kwargs):
                if path == '/batches/batch_fixture' and self.reads == 0:
                    self.reads += 1
                    raise Failure('http_error', 429, retry_after=3)
                return super().call(method, path, payload, **kwargs)
        result = execute(api=Limited('success'), jitter=lambda: 0.1)
        retry = next(e for e in result['events'] if e['action'] == 'retry_read')
        self.assertEqual(retry['delay_seconds'], 3.1)
        self.assertEqual(result['status'], 'complete')

    def test_retry_after_exceeding_deadline_prevents_another_request(self):
        class Limited(Fixture):
            def call(self, method, path, payload=None, **kwargs):
                if path == '/batches/batch_fixture':
                    self.reads += 1
                    raise Failure('http_error', 429, retry_after=60)
                return super().call(method, path, payload, **kwargs)
        api = Limited('success')
        result = execute(api=api)
        self.assertEqual(result['error']['code'], 'deadline_exceeded')
        self.assertEqual(api.reads, 1)

    def test_retry_after_parser(self):
        self.assertEqual(retry_delay('3'), 3)
        self.assertEqual(retry_delay('Wed, 21 Oct 2015 07:28:00 GMT'), 0)
        for value in ('garbage', '-2', 'nan', 'inf', None):
            self.assertIsNone(retry_delay(value))

    def test_invalid_checkpoint_and_conflicting_manifest_rejected(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            target = Path(directory) / 'bad.json'
            target.write_text('{broken', encoding='utf-8')
            with self.assertRaises(Failure): load(target)
            target.write_text(json.dumps({'version':1,'mode':'live','batch_id':'../escape','expected_ids':['x']}))
            with self.assertRaises(Failure): load(target)
            save(directory, 'batch_1', ['page-1'], 'fixture')
            with self.assertRaisesRegex(Failure, 'checkpoint_conflict'):
                save(directory, 'batch_1', ['page-2'], 'fixture')

    def test_distinct_fixture_content_survives_retrieval(self):
        report = execute('success')
        contents = [i['content'] for i in report['items']]
        self.assertEqual(len(set(contents)), 3)
        self.assertIn('```python', contents[0])
        self.assertIn('# Authentication', contents[1])
        self.assertIn('| Timeout | Resume by ID |', contents[2])

    def test_resume_empty_inventory_does_not_complete(self):
        class Empty(Fixture):
            def call(self, method, path, payload=None, **kwargs):
                if '/items?' in path: return {'items': []}
                if path == '/batches/batch_fixture':
                    return {'status': 'completed', 'total_urls': 3}
                return super().call(method, path, payload, **kwargs)
        report = Runner(Empty()).run(batch_id='batch_fixture')
        self.assertEqual(report['status'], 'incomplete')
        self.assertEqual(report['error']['code'], 'item_count_mismatch')

    def test_unknown_total_on_resume_is_not_complete(self):
        class Unknown(Fixture):
            def call(self, method, path, payload=None, **kwargs):
                data = super().call(method, path, payload, **kwargs)
                if path == '/batches/batch_fixture': data.pop('total_urls', None)
                return data
        c = Clock()
        report = Runner(Unknown('success'), clock=c.now, sleep=c.sleep).run(batch_id='batch_fixture')
        self.assertEqual(report['error']['code'], 'completeness_unknown')

    def test_wrong_ids_with_same_count_do_not_complete(self):
        class Wrong(Fixture):
            def call(self, method, path, payload=None, **kwargs):
                data = super().call(method, path, payload, **kwargs)
                if '/items?' in path:
                    for item in data['items']: item['custom_id'] = 'wrong-' + item['custom_id']
                return data
        report = execute(api=Wrong('success'))
        self.assertEqual(report['error']['code'], 'item_identity_mismatch')
        self.assertEqual(len(report['reconciliation']['missing_ids']), 3)

    def test_provider_total_disagreement_is_visible(self):
        class WrongTotal(Fixture):
            def call(self, method, path, payload=None, **kwargs):
                data = super().call(method, path, payload, **kwargs)
                if path == '/batches/batch_fixture': data['total_urls'] = 4
                return data
        self.assertEqual(execute(api=WrongTotal('success'))['error']['code'], 'provider_total_mismatch')

    def test_checkpoint_exists_before_first_poll_and_survives_interruption(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as folder:
            class Interrupt(Fixture):
                def call(self, method, path, payload=None, **kwargs):
                    if path == '/batches/batch_fixture':
                        data = json.loads((Path(folder) / 'batch_fixture.json').read_text())
                        assert data['expected_ids'] == ['page-1', 'page-2', 'page-3']
                        raise KeyboardInterrupt
                    return super().call(method, path, payload, **kwargs)
            with self.assertRaises(KeyboardInterrupt):
                Runner(Interrupt(), checkpoint_dir=folder).run(URLS)
            saved = json.loads((Path(folder) / 'batch_fixture.json').read_text())
            self.assertNotIn('url', json.dumps(saved))
            c = Clock()
            api = Fixture('success')
            report = Runner(api, clock=c.now, sleep=c.sleep).run(
                batch_id=saved['batch_id'], expected_ids=saved['expected_ids'])
            self.assertEqual(report['status'], 'complete')
            self.assertTrue(all(method == 'GET' for method, _ in api.calls))

    def test_usage_is_captured_with_fixture_provenance(self):
        class Usage(Fixture):
            def call(self, method, path, payload=None, **kwargs):
                data = super().call(method, path, payload, **kwargs)
                if path == '/batches/batch_fixture': data.update(credits_consumed=0, cost_usd=0.02)
                return data
        report = execute(api=Usage('success'))
        self.assertEqual(report['credits'], {'value': 0, 'evidence': 'fixture'})
        self.assertEqual(report['cost_usd']['value'], 0.02)

    def test_invalid_usage_remains_unknown(self):
        for value in (True, -1, '5', float('nan'), float('inf')):
            class BadUsage(Fixture):
                def call(self, method, path, payload=None, **kwargs):
                    data = super().call(method, path, payload, **kwargs)
                    if path == '/batches/batch_fixture': data['credits_consumed'] = value
                    return data
            self.assertIsNone(execute(api=BadUsage('success'))['credits']['value'])


if __name__ == '__main__': unittest.main()
