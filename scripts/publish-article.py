"""Render a local reading copy, not an external publication. Requires markdown."""
from pathlib import Path
import markdown

root = Path(__file__).resolve().parents[1]
body = markdown.markdown((root / 'docs/article-for-hamza.md').read_text(encoding='utf-8'))
style = '''
*{box-sizing:border-box}body{margin:0;background:#f2f0e8;color:#182526;font:17px/1.8 Georgia,serif}
main{max-width:850px;margin:55px auto;padding:60px 75px;background:#fffef8;border-top:5px solid #49663c}
.folio{font:11px/1.5 Arial,sans-serif;letter-spacing:3px;color:#526a51;margin-bottom:42px}
h1{font-size:47px;line-height:1.12;letter-spacing:-1.5px;margin:0 0 25px}h2{font-size:21px;line-height:1.5;font-weight:normal;color:#57635d}
h3{font:600 22px/1.4 Arial,sans-serif;margin-top:38px;color:#1d3c35}a{color:#3b654c;text-decoration-thickness:1px;text-underline-offset:3px}
strong{color:#1d3c35}code{font:13px monospace;background:#eef1e8;padding:2px 4px}li{margin:9px 0}
@media(max-width:700px){main{padding:28px;margin:0}h1{font-size:35px}}
@media print{body{background:white;font-size:11pt;line-height:1.55}main{max-width:none;margin:0;padding:0;border:0}h1{font-size:31pt}h2{font-size:15pt}h3{font-size:14pt;break-after:avoid}p,li{orphans:3;widows:3}a{color:#244434} .folio{margin-bottom:25px}}
'''
html = '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>The Last Mile of an API Integration — Amy V</title><style>'+style+'</style><main><div class="folio">AMY V / ENGINEERING CASE STUDY / 2026</div>'+body+'</main></html>'
(root / 'docs/article-for-hamza.html').write_text(html, encoding='utf-8')
print('Created local article reading copy.')
