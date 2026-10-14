"""Run from the project root: python -m examples.python.resume BATCH_ID.
Uses OLOSTEP_API_KEY. Reads an existing operation; never creates one.
"""
import sys
from lab.runner import Runner
from lab.transport import Live
from lab.reports import save

if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python -m examples.python.resume BATCH_ID')
    report = Runner(Live(), budget=600).run(batch_id=sys.argv[1])
    save(report, 'output/resumed')
    print(report['status'])
