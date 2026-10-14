import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from lab.transport import Live, Failure, NoRedirect
from lab.fixtures import Fixture
from test_workflow import execute


class EdgeTests(unittest.TestCase):
    def test_hosted_content_is_not_assumed_complete(self):
        class Hosted(Fixture):
            def call(self, method, path, payload=None, **kwargs):
                if path.startswith('/retrieve?'):
                    return {'size_exceeded': True, 'markdown_content': 'truncated',
                            'markdown_hosted_url': 'https://example.com/object'}
                return super().call(method, path, payload, **kwargs)
        report = execute(api=Hosted('success'))
        self.assertEqual(report['status'], 'partial')
        self.assertEqual(report['counts']['unresolved'], 3)
        self.assertTrue(all(i['reason'] == 'hosted_content_requires_review' for i in report['items']))

    def test_noninteger_cursor_rejected(self):
        class BadCursor(Fixture):
            def call(self, method, path, payload=None, **kwargs):
                data = super().call(method, path, payload, **kwargs)
                if '/items?' in path: data['cursor'] = {'unsafe': 'shape'}
                return data
        self.assertEqual(execute(api=BadCursor())['error']['code'], 'invalid_cursor')

    def test_duplicate_identity_not_counted_twice(self):
        class Duplicate(Fixture):
            def call(self, method, path, payload=None, **kwargs):
                data = super().call(method, path, payload, **kwargs)
                if '/items?' in path and data['items']:
                    data['items'].append(data['items'][0])
                return data
        self.assertEqual(execute(api=Duplicate())['error']['code'], 'duplicate_item_identity')

    def test_missing_items_prevent_complete_claim(self):
        class Missing(Fixture):
            def call(self, method, path, payload=None, **kwargs):
                if '/items?' in path: return {'items': []}
                return super().call(method, path, payload, **kwargs)
        self.assertEqual(execute(api=Missing())['error']['code'], 'item_count_mismatch')

    def test_live_adapter_sends_expected_request_without_exposing_key(self):
        with patch.dict('os.environ', {'OLOSTEP_API_KEY': 'private-test-key'}):
            client = Live()
        with patch.object(client.opener, 'open', return_value=io.BytesIO(b'{"id":"batch_x"}')) as opening:
            result = client.call('POST', '/batches', {'items': []})
            self.assertEqual(result['id'], 'batch_x')
            req = opening.call_args.args[0]
            self.assertEqual(req.full_url, 'https://api.olostep.com/v1/batches')
            self.assertEqual(req.get_header('Authorization'), 'Bearer private-test-key')
            self.assertEqual(json.loads(req.data), {'items': []})

    def test_provider_error_body_never_reaches_exception(self):
        with patch.dict('os.environ', {'OLOSTEP_API_KEY': 'private-test-key'}): client = Live()
        error = HTTPError('https://api.olostep.com', 401, 'private-test-key', {}, None)
        with patch.object(client.opener, 'open', side_effect=error):
            with self.assertRaises(Failure) as caught: client.call('GET', '/batches/x')
        self.assertNotIn('private-test-key', str(caught.exception))
        self.assertEqual(caught.exception.status, 401)

    def test_redirect_policy_does_not_forward_credentials(self):
        self.assertIsNone(NoRedirect().redirect_request(None, None, 302, '', {}, 'https://other.example'))

    def test_nonobject_json_rejected(self):
        with patch.dict('os.environ', {'OLOSTEP_API_KEY': 'test'}): client = Live()
        with patch.object(client.opener, 'open', return_value=io.BytesIO(b'[]')):
            with self.assertRaisesRegex(Failure, 'invalid_response'): client.call('GET', '/batches/x')


if __name__ == '__main__': unittest.main()
