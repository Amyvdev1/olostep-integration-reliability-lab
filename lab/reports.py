import json
from pathlib import Path


def markdown(report):
    lines = ['# Integration evidence', '', f"Mode: **{report['mode']}** | Outcome: **{report['status']}**",
             '', f"Batch: `{report['batch_id']}`", '',
             'Credits: **unknown** (not inferred from success counts).', '',
             f"Read retries: {report['read_retries']}", '',
             '## Items', '', '| Item | Status | Evidence |', '|---|---|---|']
    for item in report['items']:
        identity = str(item['custom_id']).replace('|', '\\|').replace('\n', ' ')
        lines.append(f"| {identity} | {item['status']} | {item['evidence']} |")
    lines += ['', '## Decisions', '']
    lines.extend(f"- {e['sequence']}. {e['action']}: {e['outcome']}" for e in report['events'])
    lines += ['', '## Limits', ''] + ['- ' + x for x in report['limitations']]
    return '\n'.join(lines) + '\n'


def save(report, directory):
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)
    (root / 'evidence.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    (root / 'evidence.md').write_text(markdown(report), encoding='utf-8')
