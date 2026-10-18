import {chromium,webkit,expect,devices} from '/Users/evilius/Documents/GitHub/agents-agenticrag/web/node_modules/@playwright/test/index.mjs';
import {readFile,writeFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
const repo='/Users/evilius/Documents/GitHub/agents-agenticrag';
const qa="/Users/evilius/.local/share/workbench/qa/image-memory-handoff-20261017";
const fixtures=process.env.HOME+'/.local/share/workbench/qa/attachments-redesign-20261015';
const original=JSON.parse(await readFile(fixtures+'/fake-bootstrap.json','utf8'));
const models=JSON.parse(await readFile(fixtures+'/fake-models.json','utf8'));
const origin='https://jakes-mac-mini.tailc4d343.ts.net';
models.find(m=>m.model_id==='fake-vision').reasoning={options:['off','low','medium','xhigh'],default:'medium'};
const png=await readFile(repo+'/server/tests/fixtures/images/fake-synthetic.png');
const results=[];
for(const [name,engine,width] of [['chromium',chromium,1440],['webkit',webkit,390]]) {
 const browser=await engine.launch();
 const context=await browser.newContext({...(name==='webkit'?devices['iPhone 13']:{}),viewport:{width,height:844},serviceWorkers:'block'});
 const page=await context.newPage(),errors=[],requests=[];
 let phase='text',nativeCalls=0,uploadCount=0;
 const bootstrap=structuredClone(original),connection=bootstrap.connections[0];
 bootstrap.settings={...bootstrap.settings,default_connection_id:connection.id,default_model_id:'fake-vision',default_preset_id:null,new_chat_model:'fixed',auto_title:false,'web.default_on':false,'appearance.reduce_motion':'system'};
 page.on('pageerror',error=>errors.push(String(error)));
 await page.route('**/api/**',async route=>{
  const r=route.request(),path=new URL(r.url()).pathname.replace(/^\/api/,'');requests.push({method:r.method(),path});
  if(r.method()==='POST' && /\/(?:messages|generate|regenerate|clean|transcribe|runs)(?:\/|$)/.test(path)) {nativeCalls++;await route.abort();return;}
  if(r.resourceType()==='eventsource'||(r.headers()['accept']??'').includes('text/event-stream')||path.endsWith('/events')) {await route.fulfill({status:200,contentType:'text/event-stream',body:': synthetic observer\n\n'});return;}
  if(path==='/attachments/fake-photo' && r.method()==='GET') {await route.fulfill({contentType:'image/png',body:png});return;}
  let data=[];let status=200;
  if(r.method()==='POST'&&path==='/attachments') {
   uploadCount++;status=201;
   data=phase==='text'?{id:'fake-paste',kind:'text',filename:'Pasted text 1.txt',mime_type:'text/plain',bytes:5400,audio_available:true}:{id:'fake-photo',kind:'image',filename:'Harbor-fake.png',mime_type:'image/png',bytes:png.length,audio_available:true};
  } else if(r.method()!=='GET') data={};
  else if(path==='/bootstrap') data=bootstrap;
  else if(path==='/models') data=models;
  else if(path==='/connections') data=bootstrap.connections;
  else if(path==='/library') data={available:false,embedding:{connection_id:connection.id,model_id:'fake-embedding'},requires_local:true,documents:[],collections:[],counts:{ready:0},bytes:0,event_id:1};
  else if(path==='/chats') data={items:[],next_cursor:null};
  else if(path==='/workflows/runs') data={items:[],next_cursor:null,paused_count:0};
  else if(path==='/transcription/status') data={available:false,audio_extensions:['.wav']};
  else if(path==='/images/status') data={available:false,enabled:false};
  await route.fulfill({status,json:data});
 });
 await page.goto(origin+'/');
 await expect(page).toHaveTitle('Aether');
 const field=page.locator('.composer textarea');await expect(field).toBeVisible();
 if(name==='webkit') await expect.poll(()=>page.locator('.composer input[type=file]').evaluate(el=>{const r=el.getBoundingClientRect();return r.width>=44&&r.height>=44&&document.elementFromPoint(r.x+r.width/2,r.y+r.height/2)===el;})).toBe(true);
 await expect(page.getByRole('button',{name:'Tools',exact:true})).toBeVisible();
 await page.getByRole('button',{name:'Tools',exact:true}).click();
 await expect(page.getByRole('menuitemradio',{name:'Model default',exact:true})).toBeVisible();
 await expect(page.getByRole('menuitemradio',{name:'High',exact:true})).toHaveCount(0);
 await page.getByRole('menuitemcheckbox',{name:'Search the web',exact:true}).click();await page.keyboard.press('Escape');
 await expect(page.getByRole('button',{name:'Turn Search off',exact:true})).toBeVisible();
 await page.getByRole('button',{name:'Turn Search off',exact:true}).click();
 const raw='Synthetic long paste fake. '.repeat(200);
 await field.fill('Before: ');
 await field.evaluate((el,text)=>{const data=new DataTransfer();data.setData('text/plain',text);el.dispatchEvent(new ClipboardEvent('paste',{clipboardData:data,bubbles:true,cancelable:true}));},raw);
 await expect(page.getByRole('button',{name:'Review file Pasted text 1.txt',exact:true})).toBeVisible();
 await page.getByRole('button',{name:'Keep as text',exact:true}).click();await expect(field).toHaveValue('Before: '+raw);
 phase='photo';await field.fill('');
 await page.locator('.composer input[type=file]').setInputFiles({name:'Harbor-fake.png',mimeType:'image/png',buffer:png});
 await expect(page.getByRole('button',{name:'Open photo Harbor-fake.png',exact:true})).toBeVisible();
 await page.getByRole('button',{name:'Open photo Harbor-fake.png',exact:true}).click();
 await expect(page.getByRole('dialog',{name:'Image viewer',exact:true})).toBeVisible();await page.keyboard.press('Escape');
 await page.getByRole('button',{name:'Remove Harbor-fake.png',exact:true}).click();
 await expect(page.locator('.composer .attachment-photo')).toHaveCount(0);
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
 await writeFile(qa+'/observer-api-'+name+'.json',JSON.stringify({requests,errors,nativeCalls,uploadCount},null,2)+'\n');
 assert.equal(nativeCalls,0);assert.equal(uploadCount,2);assert.deepEqual(errors,[]);
 results.push({engine:name,width,device_profile:name==='webkit'?'iPhone 13':'Desktop Chromium',native_picker_hit_target:name==='webkit'?true:'not applicable',app_title_aether:true,model_default_and_reported_levels:true,tools_and_chip:true,long_paste_and_undo:true,photo_upload_viewer_remove:true,no_overflow:true,api_requests_intercepted:requests.length,native_inference_requests:nativeCalls,page_errors:errors,service_workers:'blocked for isolated API fixture interception; built PWA tested by full main suite',privacy:'Synthetic fixtures only; no live API data, screenshots, videos or native picker capture.'});
 await context.close();await browser.close();
}
await writeFile(repo+'/artifacts/image-memory-recovery/installed-ui.json',JSON.stringify({origin,results},null,2)+'\n');
console.log(JSON.stringify({passed:true,engines:results.map(r=>r.engine),native_inference_requests:0,actual_static_bundle:true,all_api_data_synthetic:true}));
