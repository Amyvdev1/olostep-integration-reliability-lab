"""Atomic, minimal resume manifests. No URLs, content or credentials stored."""
import json
import os
import re
import tempfile
from pathlib import Path
from .transport import Failure


def validate(data):
    if not isinstance(data, dict) or data.get('version') != 1:
        raise Failure('invalid_checkpoint')
    if data.get('mode') not in ('fixture', 'live') or not isinstance(data.get('batch_id'), str) or not re.fullmatch(r'[\w-]{1,128}', data['batch_id']):
        raise Failure('invalid_checkpoint')
    ids = data.get('expected_ids')
    if (not isinstance(ids, list) or not 1 <= len(ids) <= 10 or
            any(not isinstance(x, str) or not x or len(x) > 200 for x in ids) or len(set(ids)) != len(ids)):
        raise Failure('invalid_checkpoint')
    return data


def load(path):
    try:
        with Path(path).open('rb') as stream:
            raw = stream.read(65537)
        if len(raw) > 65536:
            raise Failure('invalid_checkpoint')
        return validate(json.loads(raw))
    except (OSError, ValueError):
        raise Failure('checkpoint_unreadable') from None


def save(directory, batch_id, expected_ids, mode):
    data = validate({'version': 1, 'batch_id': batch_id, 'expected_ids': expected_ids, 'mode': mode})
    root = Path(directory)
    temp = None
    try:
        root.mkdir(parents=True, exist_ok=True)
        target = root / (batch_id + '.json')
        if target.exists() and load(target) != data:
            raise Failure('checkpoint_conflict')
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=root, delete=False) as stream:
            temp = Path(stream.name)
            json.dump(data, stream, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, target)
        return str(target)
    except OSError:
        raise Failure('checkpoint_write_failed') from None
    finally:
        if temp and temp.exists():
            temp.unlink()
