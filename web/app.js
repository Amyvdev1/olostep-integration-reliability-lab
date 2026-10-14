const $ = id => document.getElementById(id);
let report, chapter = -1;
const chapters = [
 ['partial','A completed batch is not a complete dataset.','The provider operation finishes, but one source fails. The runner inventories failed items separately and exports a partial result. Two usable pages are not three.'],
 ['transient','Retry the read. Preserve the operation.','A simulated 503 interrupts polling. A bounded retry recovers without creating another batch. The event trail makes the recovery visible.'],
 ['timeout','A deadline should end waiting—not erase context.','The workflow stops with an incomplete outcome and preserves its batch ID. Resume that existing operation from the CLI rather than submitting all URLs again.'],
 ['ambiguous-create','Sometimes the correct answer is: unknown.','If creation times out, the server may already have accepted it. This implementation does not automatically repeat the POST. Reconcile the operation first.'],
 ['success','Make the evidence portable.','Every page is retrieved through cursor pagination. Credits remain unknown. The local webhook inbox accepts one event and ignores its duplicate. Export the report to inspect the underlying evidence.']
];
function element(tag, text, className){const e=document.createElement(tag);e.textContent=text;if(className)e.className=className;return e;}
async function run(){
 $('run').disabled=true;$('download').disabled=true;
 try{
  const response=await fetch('/api/run?scenario='+encodeURIComponent($('scenario').value));
  if(!response.ok)throw new Error('The local runner could not complete this request.');
  report=await response.json();
  $('outcome').textContent=report.status;
  $('usable').textContent=report.counts.completed+' / '+report.expected_items;
  $('retries').textContent=report.read_retries;
  $('events').replaceChildren(...report.events.map(event=>{const li=element('li','');li.append(element('b',String(event.sequence).padStart(2,'0')),element('span',event.action.replaceAll('_',' ')),element('small',event.outcome.replaceAll('_',' ')));return li;}));
  $('items').replaceChildren(...report.items.map(item=>{const box=element('div','','item');const top=element('div','','item-top');top.append(element('strong',item.custom_id),element('span',item.status,'status '+item.status));box.append(top,element('a',item.url||'Source not available'));if(item.content){const details=element('details','');details.append(element('summary','Inspect retrieved Markdown'),element('pre',item.content));box.append(details);}else box.append(element('p',item.reason||'No retrieved content. Failure retained in evidence.'));return box;}));
  if(!report.items.length)$('items').append(element('p','No content retrieved. Inspect the stop decision and retained batch ID in the export.'));
  $('webhook').textContent=report.webhook_demo.join(' → ').replaceAll('_',' ')+'. Simulated inbox only; authoritative results must be retrieved through the authenticated API.';
  $('download').disabled=false;
 }catch(error){$('outcome').textContent='Unavailable';$('lesson-body').textContent=error.message;}finally{$('run').disabled=false;}
}
async function next(){chapter++;if(chapter>=chapters.length){chapter=-1;$('next').hidden=true;return;}const [scenario,title,body]=chapters[chapter];$('scenario').value=scenario;$('lesson-number').textContent='WALKTHROUGH / '+(chapter+1)+' OF '+chapters.length;$('lesson-title').textContent=title;$('lesson-body').textContent=body;$('next').hidden=false;$('next').textContent=chapter===chapters.length-1?'Finish walkthrough':'Next chapter →';await run();$('lesson').scrollIntoView({behavior:'smooth',block:'start'});}
$('run').addEventListener('click',run);
$('tour').addEventListener('click',()=>{chapter=-1;next();});
$('next').addEventListener('click',next);
$('download').addEventListener('click',()=>{const url=URL.createObjectURL(new Blob([JSON.stringify(report,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='olostep-fixture-evidence.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
