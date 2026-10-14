import { createRequire } from 'node:module';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { writeFile } from 'node:fs/promises';
import { observeStudioEvents } from './prospective/observe.mjs';
const out=dirname(fileURLToPath(import.meta.url)),root=resolve(out,'../../..');
const {chromium,expect}=createRequire(resolve(root,'web/package.json'))('@playwright/test');
const apiURL='http://127.0.0.1:18787/api';
async function api(path, data){const r=await fetch(apiURL+path,{method:data?'POST':'GET',headers:data?{'content-type':'application/json'}:{},body:data?JSON.stringify(data):undefined});if(!r.ok)throw Error(await r.text());return r.json();}
const models=await api('/models'),m=models.find(m=>m.model_id==='fake-chat');
if(!m)throw Error('Offline observer must use fake-chat only');
const model={connection_id:m.connection_id,model_id:m.model_id};
const graph={schema:'atelier.workflow/1',nodes:[
{id:'n_start',key:'start',kind:'start',title:'Start',config:{fields:[{name:'brief',label:'Brief',type:'long_text',required:true}]},position:{x:320,y:80}},
{id:'n_outline',key:'outline',kind:'generate',title:'Generate outline',config:{model,instructions:'',prompt:'{{start.brief}}',format:'text',params:{}},position:{x:320,y:180}},
{id:'n_draft',key:'draft',kind:'generate',title:'Generate draft',config:{model,instructions:'',prompt:'{{start.brief}}',format:'text',params:{}},position:{x:320,y:280}},
{id:'n_review',key:'review',kind:'review',title:'Approve or edit',config:{show:'{{draft.text}}',editable:true},position:{x:320,y:480}}],edges:[{id:'e0',source:'n_start',target:'n_outline',source_port:'out',target_port:'in'},{id:'e1',source:'n_outline',target:'n_draft',source_port:'out',target_port:'in'},{id:'e2',source:'n_draft',target:'n_review',source_port:'out',target_port:'in'}],notes:[],settings:{default_model:model,keep_test_runs_days:7}};
const def=await api('/workflows/defs',{name:'Synthetic offline stream observer',graph});
const browser=await chromium.launch();const page=await browser.newPage();
try{
 await page.addInitScript(observeStudioEvents);
 await page.goto('http://127.0.0.1:5173/workflows/'+def.id);
 await expect(page.locator('.wf-save-status')).toHaveText('Saved');
 await page.getByRole('button',{name:'Run',exact:true}).click();
 await page.getByRole('textbox',{name:'Brief',exact:true}).fill('Synthetic offline event test');
 const accepted=page.waitForResponse(r=>r.url().includes('/defs/'+def.id+'/runs')&&r.request().method()==='POST');
 await page.getByRole('button',{name:'Run workflow',exact:true}).click();
 const run=await (await accepted).json();
 await page.evaluate(run_id=>{window.nativeCancelTarget={run_id,node_id:'n_draft'};},run.id);
 await expect(page.locator('.wf-run-card [role=status]').first()).toContainText('Cancelled');
 const events=await page.evaluate(()=>window.nativeWorkflowEvents);
 const text=events.filter(e=>e.kind==='node.text');if(!text.length)throw Error('Real graph stream events were not observed');
 const stopped=await api('/workflows/runs/'+run.id+'/v2');
 if(stopped.nodes.n_draft.state!=='cancelled'||!stopped.nodes.n_draft.output?.text||stopped.nodes.n_review.attempt!==0)throw Error('Partial output/downstream guard failed');
 const action=await page.evaluate(()=>window.nativeCancelResult);if(!action?.clicked)throw Error('Visible cancellation control was not clicked');
 await writeFile(resolve(out,'offline-cancel.json'),JSON.stringify({passed:true,native_calls:0,fake_only:true,run_id:run.id,action,node_text_events:text.length,events,stopped},null,2)+'\n');
 await api('/workflows/runs/'+run.id+'/v2/cancel',{});
 console.log('Offline actual-event cancellation passed: '+text.length+' actual fake-runtime node.text events, zero native calls.');
} finally {await browser.close();}
