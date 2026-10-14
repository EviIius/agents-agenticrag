/* One frozen native cancel/recovery pair; --offline exercises the actual UI with fake runtime. */
import { createRequire } from 'node:module';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { createInterface } from 'node:readline/promises';
import { createHash } from 'node:crypto';
import { observeStudioEvents } from './observe.mjs';
const dir=dirname(fileURLToPath(import.meta.url)),root=resolve(dir,'../../..');
const offline=process.argv.includes('--offline'),out=offline?resolve(dir,'offline'):dir;
const {chromium,expect}=createRequire(resolve(root,'web/package.json'))('@playwright/test');
const origin='http://127.0.0.1:5173',apiOrigin='http://127.0.0.1:18787';
let browser,context,page,active,deadline,rl;
const timeline=[],outcomes=[];
await mkdir(out,{recursive:true});
const input=JSON.parse(await readFile(resolve(root,'artifacts/workflow-studio/native-trial-repair/frozen-inputs.json'),'utf8'));
async function save(name,value){await writeFile(resolve(out,name),JSON.stringify(value,null,2)+'\n');}
async function api(path,data){const r=await fetch(apiOrigin+'/api'+path,{method:data===undefined?'GET':'POST',headers:data===undefined?{}:{'content-type':'application/json'},body:data===undefined?undefined:JSON.stringify(data)});const body=await r.json();if(!r.ok)throw Error(`${path}: ${r.status} ${JSON.stringify(body)}`);return body;}
async function status(){if(offline)return {native_calls:0};return fetch(apiOrigin+'/trial/status').then(r=>r.json());}
async function events(){timeline.push(...await page.evaluate(()=>{const items=window.nativeWorkflowEvents??[];window.nativeWorkflowEvents=[];return items;}));await save('timeline.json',timeline);}
async function openTest(def,cancel){
 await page.goto(origin+'/workflows/'+def.id);
 await expect(page.locator('.wf-save-status')).toHaveText('Saved');
 const node=page.locator('.react-flow__node-block').filter({has:page.locator('.wf-block-title').filter({hasText:/^Generate draft$/})});
 await node.focus();await page.keyboard.press('Enter');
 await expect(page.getByRole('textbox',{name:'Block name',exact:true})).toHaveValue('Generate draft');
 await page.locator('.wf-inspector').getByRole('button',{name:'Actions for Generate draft',exact:true}).click();
 await page.getByRole('menuitem',{name:'Test this block',exact:true}).click();
 await page.getByRole('textbox',{name:'Sample start.brief',exact:true}).fill(input.brief);
 await page.getByRole('textbox',{name:'Sample outline.text',exact:true}).fill(input.sample);
 const accepted=page.waitForResponse(r=>r.url().includes('/defs/'+def.id+'/runs')&&r.request().method()==='POST');
 await page.getByRole('button',{name:'Test block',exact:true}).click();
 const response=await accepted;if(response.status()!==202)throw Error('Block test was not accepted');
 const run=await response.json();active=run.id;
 if(cancel)await page.evaluate(run_id=>{window.nativeCancelTarget={run_id,node_id:'n_draft'};},run.id);
 return run;
}
async function main(){
 const ready=offline?null:await status();
 if(ready&&ready.native_calls!==0)throw Error('Never reuse a native trial host');
 const model=offline?(()=>null)():{connection_id:ready.connection_id,model_id:ready.model_id};
 const fake=offline?(await api('/models')).find(m=>m.model_id==='fake-chat'):null;
 if(offline&&!fake)throw Error('Offline must use the fake runtime');
 const selected=model??{connection_id:fake.connection_id,model_id:fake.model_id};
 const before=JSON.parse(await readFile(resolve(root,'artifacts/workflow-studio/native-trial-repair/frozen-definition.json'),'utf8'));
 const graph=before.graph;graph.settings.default_model=selected;
 for(const node of graph.nodes)if(node.kind==='generate')node.config.model=selected;
 const def=await api('/workflows/defs',{name:'Synthetic native cancel and recover',graph});
 const validation=await api('/workflows/defs/'+def.id+'/validate',{graph});if(validation.issues.some(i=>i.severity==='error'))throw Error(JSON.stringify(validation.issues));
 await save('frozen-definition.json',def);await save('frozen-inputs.json',{...input,budget:offline?0:2,maximum_elapsed_seconds:180,definition_sha256:createHash('sha256').update(JSON.stringify(def)).digest('hex')});
 browser=await chromium.launch();
 const videoDir=resolve(process.env.HOME,'.local/share/workbench/qa/workflow-studio/native-controls/videos',offline?'offline':'native');await mkdir(videoDir,{recursive:true});
 context=await browser.newContext({viewport:{width:1440,height:900},recordVideo:{dir:videoDir}});page=await context.newPage();page.setDefaultTimeout(15000);
 await page.addInitScript(observeStudioEvents);
 deadline=setTimeout(()=>{console.error('Three-minute trial limit');if(active)void api('/workflows/runs/'+active+'/v2/cancel',{});rl?.close();void browser.close();process.exitCode=1;},180000);
 const first=await openTest(def,true);
 await expect(page.locator('.wf-run-card [role=status]').first()).toContainText('Cancelled',{timeout:15000});
 await events();const action=await page.evaluate(()=>window.nativeCancelResult);await save('cancel-action.json',action);
 const cancelled=await api('/workflows/runs/'+first.id+'/v2');await save('cancelled-run.json',cancelled);
 if(!action?.clicked||cancelled.nodes.n_draft.state!=='cancelled'||!cancelled.nodes.n_draft.output?.text||cancelled.nodes.n_review.attempt!==0||cancelled.nodes.n_save.attempt!==0)throw Error('Actual UI cancellation/partial/downstream gate failed');
 if(cancelled.nodes.n_outline.attempt!==0||cancelled.nodes.n_start.attempt!==0)throw Error('Sample ancestors unexpectedly ran');
 if(!offline){
  const state=await status(),calls=JSON.parse(await readFile(resolve(dir,'requests.json'),'utf8'));await save('after-cancel-status.json',state);
  if(state.native_calls!==1||state.capacity_busy||calls.length!==1||!calls[0].closed_at||calls[0].completed_stream||calls[0].done_at||calls[0].close_error!==null)throw Error('Native incomplete stream closure/capacity gate failed');
 }
 await page.screenshot({path:resolve(out,'cancelled-native-synthetic.png')});
 outcomes.push({name:'cancel',run_id:first.id,passed:true,native_calls:offline?0:1});await save('outcomes.json',outcomes);active=null;
 const second=await openTest(def,false);
 await expect(page.locator('.wf-run-card [role=status]').first()).toContainText('Ready for review',{timeout:30000});
 await events();const done=await api('/workflows/runs/'+second.id+'/v2');await save('recovered-run.json',done);
 if(done.mode!=='test'||done.nodes.n_draft.state!=='complete'||done.nodes.n_outline.attempt!==0||done.nodes.n_start.attempt!==0||done.nodes.n_review.attempt!==0||done.nodes.n_save.attempt!==0)throw Error('Single-block recovery execution gate failed');
 const history=await api('/workflows/runs?def_id='+def.id);await save('normal-history.json',history);if(history.items.length)throw Error('Tests leaked into normal history');
 await page.reload();await expect(page.locator('.wf-run-card [role=status]').first()).toContainText('Ready for review');await events();
 const durable=await api('/workflows/runs/'+second.id+'/v2');if(durable.nodes.n_draft.output.text!==done.nodes.n_draft.output.text)throw Error('Reload changed output');
 await page.screenshot({path:resolve(out,'recovered-native-synthetic.png')});
 outcomes.push({name:'single-block-recovery',run_id:second.id,passed:true,native_calls:offline?0:1});await save('outcomes.json',outcomes);active=null;
 if(!offline){
  const state=await status(),calls=JSON.parse(await readFile(resolve(dir,'requests.json'),'utf8'));await save('after-recovery-status.json',state);
  if(state.native_calls!==2||state.capacity_busy||calls.length!==2||!calls[1].closed_at||!calls[1].completed_stream||calls[1].close_error!==null)throw Error('Recovery native budget/closure gate failed');
  const text=done.nodes.n_draft.output.text,detailChecks=[/Cobalt Saturday/i,/10(?::00|\s*a\.?m\.?)/i,/\b12\b/,/\$\s*20|20\s*dollars/i,/pencils/i,/paper/i].map(r=>r.test(text));
  await save('recovered-fact-check.json',{six_details_present:detailChecks,manual_review:'pending'});
  if(!detailChecks.every(Boolean))throw Error('Recovery lacks required original details');
  rl=createInterface({input:process.stdin,output:process.stdout});console.log('SEMANTIC REVIEW '+resolve(out,'recovered-run.json'));
  const answer=await rl.question('Codex review (approve or fail): ');
  await save('recovered-fact-check.json',{six_details_present:detailChecks,manual_review:answer.trim()==='approve'?'Codex reviewed all source facts and extra claims: pass':'Codex manual source review failed'});
  if(answer.trim()!=='approve')throw Error('Recovery semantic review failed; no retry');
 }
 await save('trial-result.json',{passed:true,native_calls:offline?0:2,offline,outcomes,limitations:['One control pair, not general factual reliability or image/chat coexistence','No main/live publication']});
 console.log('Cancel/recovery pair passed; native calls '+(offline?0:2));
}
try{await main();}catch(error){await save('trial-result.json',{passed:false,error:error.stack,offline,outcomes,native_calls:(await status().catch(()=>({native_calls:null}))).native_calls,active_run:active});console.error(error);process.exitCode=1;}
finally{clearTimeout(deadline);rl?.close();if(active)await api('/workflows/runs/'+active+'/v2/cancel',{}).catch(()=>{});await context?.close();await browser?.close();}
