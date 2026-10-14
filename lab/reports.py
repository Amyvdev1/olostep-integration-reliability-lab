import json
from pathlib import Path


def markdown(report):
    credits = report['credits']
    usage = str(credits['value']) if credits['value'] is not None else 'unknown'
    cost = report['cost_usd']
    cost_value = str(cost['value']) if cost['value'] is not None else 'unknown'
    lines = ['# Integration evidence', '', f"Mode: **{report['mode']}** | Outcome: **{report['status']}**",
             '', f"Batch: `{report['batch_id']}`", '',
             f"Credits: **{usage}** ({credits['evidence']}; not inferred from success counts).", '',
             f"Cost USD: **{cost_value}** ({cost['evidence']}; not an invoice audit).", '',
             f"Read retries: {report['read_retries']}", '',
             '## Items', '', '| Item | Status | Evidence |', '|---|---|---|']
    for item in report['items']:
        identity = str(item['custom_id']).replace('|', '\\|').replace('\n', ' ')
        lines.append(f"| {identity} | {item['status']} | {item['evidence']} |")
    reconciliation = report.get('reconciliation')
    if reconciliation:
        lines += ['', '## Reconciliation', '',
                  f"Verification basis: `{reconciliation['identity_basis']}`.",
                  f"Expected: {report['expected_items']}; observed: {reconciliation['observed_count']}; provider total: {reconciliation['provider_total']}.",
                  f"Missing IDs: {json.dumps(reconciliation['missing_ids'])}.",
                  f"Unexpected IDs: {json.dumps(reconciliation['unexpected_ids'])}."]
    if report.get('error'):
        lines += ['', f"Stop reason: `{report['error']['code']}`."]
    lines += ['', '## Decisions', '']
    lines.extend(f"- {e['sequence']}. {e['action']}: {e['outcome']}" for e in report['events'])
    lines += ['', '## Limits', ''] + ['- ' + x for x in report['limitations']]
    return '\n'.join(lines) + '\n'


def save(report, directory):
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)
    (root / 'evidence.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    (root / 'evidence.md').write_text(markdown(report), encoding='utf-8')
