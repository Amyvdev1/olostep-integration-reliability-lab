import argparse
import json
from .fixtures import Fixture, SCENARIOS, URLS
from .runner import Runner
from .transport import Live, Failure
from .reports import save
from .checkpoints import load as load_checkpoint


def main():
    parser = argparse.ArgumentParser(description='Independent Olostep reliability reference')
    parser.add_argument('--scenario', choices=SCENARIOS, default='partial')
    parser.add_argument('--live', action='store_true')
    parser.add_argument('--allow-billable', action='store_true')
    parser.add_argument('--url', action='append')
    parser.add_argument('--resume', help='Existing batch ID; does not create a new batch')
    parser.add_argument('--checkpoint', help='Resume from a saved manifest; never creates work')
    parser.add_argument('--page-size', type=int, default=50)
    parser.add_argument('--budget', type=float, default=30)
    parser.add_argument('--output', default='output/latest')
    parser.add_argument('--serve', action='store_true')
    args = parser.parse_args()
    manifest = None
    if args.checkpoint:
        if args.resume or args.url:
            parser.error('--checkpoint cannot be combined with --resume or --url')
        try:
            saved = load_checkpoint(args.checkpoint)
        except Failure as exc:
            parser.error(str(exc))
        if saved['mode'] != ('live' if args.live else 'fixture'):
            parser.error('Checkpoint mode must match --live or fixture mode')
        args.resume, manifest = saved['batch_id'], saved['expected_ids']
    if args.resume and args.url:
        parser.error('--resume cannot be combined with --url')
    if args.serve:
        from .server import serve
        serve()
        return 0
    if args.live and not args.resume and not args.allow_billable:
        parser.error('Live creation requires --allow-billable and --url; provider usage may cost credits.')
    if args.live and not args.resume and not args.url:
        parser.error('Provide a permitted public URL with --url.')
    try:
        api = Live() if args.live else Fixture(args.scenario)
        runner = Runner(api, budget=args.budget, page_size=args.page_size, checkpoint_dir='output/checkpoints')
        report = runner.run(urls=(args.url if args.live else URLS) if not args.resume else None,
                            batch_id=args.resume, expected_ids=manifest)
        save(report, args.output)
        print(json.dumps({'status': report['status'], 'mode': report['mode'],
                          'counts': report['counts'], 'report': args.output,
                          'error': report.get('error')}, indent=2))
        return 2 if report['status'] == 'incomplete' else 0
    except (Failure, ValueError) as exc:
        print(str(exc))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
