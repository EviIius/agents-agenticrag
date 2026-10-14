/* Bounded native UI trial. Run only after CI-C gates; stdin is Codex's semantic review. */
import { createRequire } from 'node:module';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { createInterface } from 'node:readline/promises';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import { observeStudioEvents } from './observe.mjs';
const out=dirname(fileURLToPath(import.meta.url));
const root=resolve(out,'../../..');
const require=createRequire(resolve(root,'web/package.json'));
const { chromium, expect }=require('@playwright/test');
const url='http://127.0.0.1:5173';
const apiURL='http://127.0.0.1:18787';
const brief='Create a short announcement for a fictional art workshop. The workshop is called Cobalt Saturday; it meets at 10:00, admits 12 participants, costs $20, and provides pencils and paper. Do not add a date, address or registration link.';
const outline='Extract a concise factual outline from the brief. Preserve each supplied detail and its scope. Use only explicitly stated facts; leave unspecified information unspecified. Brief: {{start.brief}}';
const draft='Write a short announcement using the original brief as the authoritative source. The outline is an organizational aid and may contain mistakes. Preserve every explicit fact and its scope. Omit claims unsupported by the original brief. Original brief: {{start.brief}}\nOutline: {{outline.text}}';
const sample='Cobalt Saturday fictional art workshop; 10:00; 12 participants; $20; pencils and paper provided. No date, address or registration link.';
const suffix='\n\nSynthetic host edit: prepared for review.';
let browser,context,page,active,deadline,definition,rl;
const outcomes=[],timeline=[];
async function save(name,data){await writeFile(resolve(out,name),JSON.stringify(data,null,2)+'\n');}
async function api(path,data,method=data===undefined ? 'GET' : 'POST'){
  const response=await fetch(apiURL+'/api'+path,{method,headers:data===undefined ? {} : {'content-type':'application/json'},body:data===undefined ? undefined : JSON.stringify(data)});
  const body=await response.json();if(!response.ok)throw new Error(`${method} ${path}: ${response.status} ${JSON.stringify(body)}`);return body;
}
async function status(){return fetch(apiURL+'/trial/status').then(r=>r.json());}
function facts(text){return [/Cobalt Saturday/i,/10(?::00|\s*(?:a\.?m\.?))/i,/\b12\b/,/\$\s*20|20\s*dollars/i,/pencils/i,/paper/i].map(re=>re.test(text));}
async function retainRun(run,name){await save(name,run);if(page)timeline.push(...await page.evaluate(()=>{const events=window.nativeWorkflowEvents??[];window.nativeWorkflowEvents=[];return events;}));await save('timeline.json',timeline);}
async function semantic(run,name,rl){
  const raw=run.nodes.n_draft.output.text;const supplied=facts(raw);
  await retainRun(run,name+'-paused.json');
  await save(name+'-fact-check.json',{six_details_present:supplied,no_urls:!/(https?:\/\/|www\.)/i.test(raw),status:'Manual semantic review pending'});
  if(!supplied.every(Boolean) || /https?:\/\/|www\./i.test(raw))throw new Error('Required synthetic details missing or unexpected URL; no further calls');
  console.log(`SEMANTIC REVIEW ${name}: ${resolve(out,name+'-paused.json')}`);
  const answer=await rl.question('Codex review (approve or fail): ');
  if(answer.trim()!=='approve')throw new Error('Manual review failed; no further calls');
  await save(name+'-fact-check.json',{six_details_present:supplied,no_urls:true,manual_review:'Codex reviewed exact outline/draft against the original brief: no added event facts'});
}
async function startRun(){
  await page.goto(url+`/workflows/${definition.id}`);await expect(page.locator('.wf-save-status')).toHaveText('Saved');
  await page.getByRole('button',{name:'Run',exact:true}).click();
  await page.getByRole('textbox',{name:'Brief',exact:true}).fill(brief);
  const accepted=page.waitForResponse(r=>r.url().includes(`/defs/${definition.id}/runs`) && r.request().method()==='POST');
  await page.getByRole('button',{name:'Run workflow',exact:true}).click();
  const response=await accepted;if(response.status()!==202)throw new Error('Run not accepted');active=(await response.json()).id;return active;
}
async function paused(){
  await expect(page.locator('.wf-block[data-run="paused"]')).toContainText('Waiting for you',{timeout:180000});
  await page.getByRole('button',{name:'View result for Generate draft',exact:true}).click();
  await expect(page.getByRole('textbox',{name:'Review result'})).toBeVisible();
  return api(`/workflows/runs/${active}/v2`);
}
async function completed(){await expect(page.locator('.wf-run-card [role=status]').first()).toContainText('Ready for review',{timeout:30000});return api(`/workflows/runs/${active}/v2`);}
async function main(){
  const ready=await status();
  if(ready.native_calls!==0)throw new Error('Trial host has already run inference');
  const model={connection_id:ready.connection_id,model_id:ready.model_id};
  const node=(id,key,kind,title,config,y)=>({id,key,kind,title,config,position:{x:320,y},disabled:false});
  const graph={schema:'atelier.workflow/1',nodes:[
    node('n_start','start','start','Start',{fields:[{name:'brief',label:'Brief',type:'long_text',required:true}]},80),
    node('n_outline','outline','generate','Generate outline',{model,instructions:'',prompt:outline,format:'text',params:{}},280),
    node('n_draft','draft','generate','Generate draft',{model,instructions:'',prompt:draft,format:'text',params:{}},480),
    node('n_review','review','review','Approve or edit',{show:'{{draft.text}}',editable:true,message:'Review the synthetic announcement.'},680),
    node('n_save','save','output','Save results',{include:[{label:'Announcement',ref:'{{review.value}}'}],formats:['md','json'],include_sources:false},880)
  ],edges:[['n_start','n_outline','out'],['n_outline','n_draft','out'],['n_draft','n_review','out'],['n_review','n_save','approved']].map(([source,target,source_port],i)=>({id:`e_${i}`,source,target,source_port,target_port:'in'})),notes:[],settings:{default_model:model,keep_test_runs_days:7}};
  definition=await api('/workflows/defs',{name:'Synthetic native Cobalt Saturday trial',graph});
  const validation=await api(`/workflows/defs/${definition.id}/validate`,{graph});if(validation.issues.some(i=>i.severity==='error'))throw new Error(JSON.stringify(validation.issues));
  await save('frozen-definition.json',definition);await save('frozen-inputs.json',{brief,outline,draft,sample,suffix,budget:7,maximum_elapsed_seconds:600,definition_sha256:createHash('sha256').update(JSON.stringify(definition)).digest('hex')});
  browser=await chromium.launch();
  const videoDir=resolve(process.env.HOME,'.local/share/workbench/qa/workflow-studio/native-trial-repair/videos');await mkdir(videoDir,{recursive:true});
  context=await browser.newContext({viewport:{width:1440,height:900},recordVideo:{dir:videoDir}});page=await context.newPage();page.setDefaultTimeout(30000);
  page.on('pageerror',e=>{timeline.push({kind:'pageerror',at:Date.now(),message:e.message});});
  page.on('response',async r=>{if(r.url().endsWith('/workflows/stream'))timeline.push({kind:'event-stream',at:Date.now(),status:r.status()});});
  await page.addInitScript(observeStudioEvents);
  rl=createInterface({input:process.stdin,output:process.stdout});
  deadline=setTimeout(()=>{console.error('Ten-minute overall trial deadline');if(active)void api(`/workflows/runs/${active}/v2/cancel`,{});process.exitCode=1;rl?.close();void browser?.close();},600000);
  for(let i=1;i<=2;i++){
    const before=(await status()).native_calls,t0=Date.now();await startRun();
    await expect(page.locator('.wf-stream-preview').first()).not.toBeEmpty({timeout:180000});
    const run=await paused();await semantic(run,`run-${i}`,rl);
    if(!timeline.some(e=>e.kind==='node.text'))throw new Error('No actual browser node.text events captured');
    // Reload proves the review is durable before approving it.
    await page.reload();await expect(page.locator('.wf-block[data-run="paused"]')).toContainText('Waiting for you');
    await page.getByRole('button',{name:'View result for Generate draft',exact:true}).click();
    const original=run.nodes.n_draft.output.text;if(i===2)await page.getByRole('textbox',{name:'Review result'}).fill(original+suffix);
    await page.screenshot({path:resolve(out,`review-${i}-synthetic.png`)});
    await page.getByRole('button',{name:'Approve',exact:true}).click();
    const done=await completed();await retainRun(done,`run-${i}-complete.json`);
    const text=done.results[0].items[0].value;if(text!==(i===2 ? original+suffix : original))throw new Error('Review/save binding mismatch');
    if((await status()).native_calls-before!==2)throw new Error('Unexpected call count for complete run');
    const second=(await api(`/workflows/runs/${active}/v2/export?format=json`)).run;
    if(second.nodes.n_outline.output.text!==run.nodes.n_outline.output.text || second.nodes.n_draft.output.text!==original)throw new Error('Raw outputs changed');
    outcomes.push({name:`run-${i}`,run_id:active,native_calls:2,elapsed_ms:Date.now()-t0,edited:i===2});await save('outcomes.json',outcomes);active=null;
  }
  const beforeCancel=(await status()).native_calls;await startRun();
  const draftNode=page.locator('.wf-block[data-run="running"]').filter({has:page.locator('.wf-block-title').filter({hasText:/^Generate draft$/})});
  await expect(draftNode.locator('.wf-stream-preview')).not.toBeEmpty({timeout:180000});
  await page.getByRole('button',{name:'Cancel workflow',exact:true}).click();
  await expect(page.locator('.wf-run-card [role=status]').first()).toContainText('Cancelled');
  const cancelled=await api(`/workflows/runs/${active}/v2`);await retainRun(cancelled,'cancelled-run.json');
  if(cancelled.nodes.n_outline.state!=='complete' || cancelled.nodes.n_draft.state!=='cancelled' || !cancelled.nodes.n_draft.output?.text || cancelled.nodes.n_review.attempt!==0 || cancelled.nodes.n_save.attempt!==0)throw new Error('Cancellation/partial-output gate failed');
  if((await status()).native_calls-beforeCancel!==2)throw new Error('Unexpected cancellation call count');
  outcomes.push({name:'cancel',run_id:active,native_calls:2});active=null;
  const tested=await api(`/workflows/defs/${definition.id}/runs`,{request_key:crypto.randomUUID(),inputs:{brief},mode:'test',node_id:'n_draft',samples:{'outline.text':sample,'start.brief':brief}});active=tested.id;
  await page.goto(url+`/workflows/${definition.id}/runs/${tested.id}`);const testDone=await completed();await retainRun(testDone,'single-block-test.json');
  if(testDone.mode!=='test' || testDone.nodes.n_draft.state!=='complete' || !facts(testDone.nodes.n_draft.output.text).every(Boolean))throw new Error('Single-block test failed');
  const list=await api(`/workflows/runs?def_id=${definition.id}`);if(list.items.some(r=>r.id===tested.id))throw new Error('Test leaked into normal history');
  console.log(`SEMANTIC REVIEW single-block: ${resolve(out,'single-block-test.json')}`);if((await rl.question('Codex review (approve or fail): ')).trim()!=='approve')throw new Error('Single-block semantic review failed');
  const final=await status();if(final.native_calls!==7 || final.capacity_busy)throw new Error('Budget/capacity gate failed');
  outcomes.push({name:'single-block',run_id:tested.id,native_calls:1});await save('outcomes.json',outcomes);await save('trial-result.json',{passed:true,native_calls:7,outcomes,limitations:['Synthetic task only; no Web accuracy or mixed image/chat memory qualification','Save directly binds review.value; no distinct Compose block']});active=null;rl.close();
}
try {await main();console.log('Native workflow trial passed.');}
catch(error){await save('trial-result.json',{passed:false,error:error.stack,outcomes,active_run:active,native_calls:(await status().catch(()=>({native_calls:null}))).native_calls});console.error(error);process.exitCode=1;}
finally{clearTimeout(deadline);rl?.close();if(active)await api(`/workflows/runs/${active}/v2/cancel`,{}).catch(()=>{});await context?.close();await browser?.close();}
