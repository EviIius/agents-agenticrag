// Previous compiled UI + schema-14-aware candidate server; fake jobs only.
import {spawn} from 'node:child_process';
import {createWriteStream} from 'node:fs';
import {readFile,writeFile} from 'node:fs/promises';
import {dirname,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
const out=dirname(fileURLToPath(import.meta.url)),root=resolve(out,'../../..');
const privateDir=process.env.HOME+'/.local/share/workbench/qa/photo-editing-pe1-c-prep-20261020';
const {chromium,webkit,devices,expect}=await import(pathToFileURL(root+'/web/node_modules/@playwright/test/index.mjs'));
const children=[];
function start(module,port){
 const child=spawn(root+'/server/.venv/bin/python',['-m','uvicorn',module+':app','--host','127.0.0.1','--port',String(port),'--workers','1'],{cwd:root+'/server',detached:true,stdio:['ignore','pipe','pipe'],env:{...process.env,PYTHONPATH:privateDir+':'+root+'/server',PE1_COMPAT_STATIC:privateDir+'/previous-static',WORKBENCH_IMAGE_HOME:'',WORKBENCH_TRANSCRIBE_HOME:''}});
 const log=createWriteStream(privateDir+'/'+module+'-compat.log');child.stdout.pipe(log);child.stderr.pipe(log);children.push(child);
}
async function ready(url){for(let i=0;i<100;i++){try{if((await fetch(url)).ok)return;}catch{}await new Promise(r=>setTimeout(r,100));}throw new Error('Owned server unavailable');}
async function stop(child){const done=()=>child.exitCode!==null||child.signalCode!==null;if(done())return;try{process.kill(-child.pid,'SIGTERM');}catch(e){if(e.code!=='ESRCH')throw e;return;}await Promise.race([new Promise(r=>child.once('exit',r)),new Promise(r=>setTimeout(r,5000))]);if(!done()){try{process.kill(-child.pid,'SIGKILL');}catch(e){if(e.code!=='ESRCH')throw e;}if(!done())await new Promise(r=>child.once('exit',r));}}
const origin='http://127.0.0.1:18787',rows=[];
async function post(path,data){const response=await fetch(origin+path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});if(!response.ok)throw new Error(await response.text());return response.json();}
try{
 for(const port of [18080,18787]){try{await fetch(`http://127.0.0.1:${port}/api/health`);throw new Error('QA port already owned');}catch(e){if(e.message==='QA port already owned')throw e;}}
 start('tests.fake_runtime',18080);await ready('http://127.0.0.1:18080/api/tags');
 start('compat_serve',18787);await ready(origin+'/api/health');
 assert.equal(await (await fetch(origin+'/')).text(),await readFile(privateDir+'/previous-static/index.html','utf8'));
 for(const [name,engine,width] of [['chromium',chromium,1440],['webkit',webkit,390]]){
  const chat=await post('/api/chats',{});
  const form=new FormData();form.append('file',new Blob([await readFile(root+'/server/tests/fixtures/images/fake-synthetic.png')],{type:'image/png'}),'synthetic.png');
  const upload=await fetch(origin+`/api/chats/${chat.id}/image-references`,{method:'POST',body:form});assert.equal(upload.status,201);const ref=await upload.json();
  const initial=await post(`/api/chats/${chat.id}/images`,{request_key:crypto.randomUUID(),prompt:'Synthetic compatibility fallback edit',count:1,seeds:[42],reference_id:ref.id});
  assert.equal(initial.assistant.images[0].mode,'edit');
  const browser=await engine.launch(),context=await browser.newContext({...(name==='webkit'?devices['iPhone 13']:{}),viewport:{width,height:900},serviceWorkers:'block'});
  const page=await context.newPage(),errors=[],assets=[];
  page.on('pageerror',e=>errors.push(String(e)));
  page.on('response',r=>{if(/\/assets\/.*\.js$/.test(r.url()))assets.push({path:new URL(r.url()).pathname,status:r.status()});});
  await page.goto(origin+'/c/'+chat.id);
  await expect(page.getByRole('button',{name:'Open image 1',exact:true})).toBeVisible();
  const retry=page.waitForResponse(r=>r.request().method()==='POST'&&r.url().endsWith('/images/retry'));
  await page.getByRole('button',{name:'Try again',exact:true}).click();
  const response=await retry;assert.equal(response.status(),202);const result=await response.json();
  assert.equal(result.assistant.images[0].mode,'edit');assert.equal(result.assistant.images[0].reference.id,ref.id);
  assert.notEqual(result.assistant.images[0].id,initial.assistant.images[0].id);
  await expect(page.getByRole('button',{name:'Open image 1',exact:true})).toBeVisible();
  const output=await fetch(origin+`/api/images/jobs/${initial.assistant.images[0].id}/output/png`);assert.equal(output.status,200);
  const bytes=new Uint8Array(await output.arrayBuffer());assert.deepEqual([...bytes.slice(0,8)],[137,80,78,71,13,10,26,10]);
  assert.equal(errors.length,0,JSON.stringify(errors));assert(assets.length>0&&assets.every(r=>r.status===200));
  rows.push({engine:name,previous_compiled_ui:true,candidate_schema_aware_backend:true,reference_preserved_on_retry:true,output_available:true,page_errors:errors,asset_failures:assets.filter(r=>r.status!==200),native_calls:0});
  page.removeAllListeners();await context.close();await browser.close();
 }
 await writeFile(out+'/compatibility-browser.json',JSON.stringify({passed:true,synthetic_only:true,results:rows,limits:'This fallback retains the schema-14-aware server. Returning to the complete schema-13 server remains unsafe and is prohibited.'},null,2)+'\n');
 console.log(JSON.stringify({passed:true,previous_ui_candidate_backend:true,browsers:rows.length,native_calls:0}));
}catch(e){console.error(e);throw e;}finally{for(const child of children.reverse())await stop(child);}
