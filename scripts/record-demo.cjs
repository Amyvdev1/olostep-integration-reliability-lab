// Local browser verification and real screen recording. Requires Playwright.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const fs = require('node:fs');
const path = require('node:path');
(async()=>{
 const browser = await chromium.launch({headless:true});
 const context = await browser.newContext({viewport:{width:1440,height:1080},recordVideo:{dir:'media/raw',size:{width:1440,height:1080}}});
 const page = await context.newPage(); const errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8765');
 await page.getByRole('button',{name:'Run workflow'}).click();
 await page.waitForFunction(()=>document.getElementById('outcome').textContent==='partial');
 await page.screenshot({path:'media/console-desktop.png',fullPage:true});
 await page.waitForTimeout(12000);
 await page.getByRole('button',{name:'Guided walkthrough'}).click();
 await page.waitForTimeout(20000);
 for(const seconds of [17,17,17,22]){
  await page.getByRole('button',{name:'Next chapter'}).click();
  await page.waitForTimeout(seconds*1000);
 }
 const downloadPromise=page.waitForEvent('download');
 await page.getByRole('button',{name:'Export JSON'}).click();
 const download=await downloadPromise;await download.saveAs('media/recorded-evidence.json');
 const exported=await page.evaluate(()=>report);
 if(exported.schema_version!==2||exported.status!=='complete'||exported.credits.value!==null||exported.reconciliation.identity_basis!=='manifest')throw Error('Export evidence mismatch');
 await page.screenshot({path:'media/console-complete.png',fullPage:true});
 const video=page.video();await context.close();
 await video.saveAs('media/walkthrough.webm');
 const mobile=await browser.newPage({viewport:{width:390,height:844}});
 await mobile.goto('http://127.0.0.1:8765');
 await mobile.getByRole('button',{name:'Run workflow'}).click();
 await mobile.waitForFunction(()=>document.getElementById('outcome').textContent==='partial');
 const overflow=await mobile.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
 await mobile.screenshot({path:'media/console-mobile.png',fullPage:true});
 if(overflow)throw Error('Mobile horizontal overflow');
 if(errors.length)throw Error(errors.join('\n'));
 fs.writeFileSync('media/browser-verification.json',JSON.stringify({desktop:'1440x1080',mobile:'390x844',horizontalOverflow:overflow,pageErrors:errors,exportStatus:exported.status,recording:'actual browser interactions with fixture mode'},null,2));
 await browser.close();console.log('Browser checks and recording complete.');
})().catch(e=>{console.error(e);process.exit(1)});
