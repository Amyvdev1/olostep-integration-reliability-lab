"""Durable local webhook simulator; deliberately not a public HTTP endpoint."""
import hashlib
import json
import sqlite3


class Inbox:
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.execute('CREATE TABLE IF NOT EXISTS events (id TEXT PRIMARY KEY, digest TEXT NOT NULL, batch TEXT NOT NULL)')
        self.db.commit()

    def accept(self, event, expected_batch):
        if (not isinstance(event, dict) or event.get('object') != 'event.batch.completed'
                or not isinstance(event.get('id'), str) or not event['id']
                or not isinstance(event.get('data'), dict)
                or event['data'].get('id') != expected_batch):
            return 'rejected'
        # Delivery-attempt metadata may change without changing the event.
        semantic = {'object': event['object'], 'data': event['data']}
        digest = hashlib.sha256(json.dumps(semantic, sort_keys=True).encode()).hexdigest()
        with self.db:
            result = self.db.execute('INSERT OR IGNORE INTO events VALUES (?, ?, ?)',
                                     (event['id'], digest, expected_batch))
            if result.rowcount:
                return 'accepted_notification'
            old = self.db.execute('SELECT digest FROM events WHERE id=?', (event['id'],)).fetchone()[0]
            return 'duplicate_ignored' if old == digest else 'conflict_rejected'

    def close(self):
        self.db.close()
