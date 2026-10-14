"""Create a clean handoff archive without caches, credentials or raw takes."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

root = Path(__file__).resolve().parents[1]
destination = root.parent / 'olostep-integration-reliability-lab.zip'
excluded = {'__pycache__', 'node_modules', '.git', '.venv', 'output', 'raw'}
with ZipFile(destination, 'w', ZIP_DEFLATED) as archive:
    for file in sorted(root.rglob('*')):
        relative = file.relative_to(root)
        if not file.is_file() or any(part in excluded for part in relative.parts):
            continue
        if file.name.startswith('article-review-') or file.name == 'video-review.png':
            continue
        if file.name.startswith('.env') or '.sqlite' in file.name or file.suffix in ('.webm', '.log'):
            continue
        archive.write(file, Path(root.name) / relative)
print(destination)
