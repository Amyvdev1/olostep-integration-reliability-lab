const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const {pathToFileURL}=require('node:url');
const path=require('node:path');
(async()=>{const browser=await chromium.launch({headless:true});const page=await browser.newPage();
await page.goto(pathToFileURL(path.resolve('docs/article-for-hamza.html')).href);
await page.pdf({path:'docs/article-for-hamza.pdf',format:'A4',printBackground:true,
margin:{top:'20mm',bottom:'20mm',left:'22mm',right:'22mm'},displayHeaderFooter:true,
headerTemplate:'<span></span>',footerTemplate:'<div style="font-size:9px;width:100%;text-align:center;color:#52645b">Amy V · Independent Olostep case study · <span class="pageNumber"></span> / <span class="totalPages"></span></div>'});
await browser.close();console.log('PDF exported.');})().catch(e=>{console.error(e);process.exit(1)});
