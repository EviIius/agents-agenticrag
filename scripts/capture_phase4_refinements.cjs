const { chromium } = require(process.cwd() + '/web/node_modules/playwright');
const fs = require('node:fs/promises');
const AxeBuilder = require(process.cwd() + '/web/node_modules/@axe-core/playwright').default;
const output = process.argv[2];
(async () => {
 const browser = await chromium.launch();
 for (const width of [390,1440]) for (const theme of ['light','dark']) {
  const context = await browser.newContext({viewport:{width,height:width===390?844:900}});
  const page = await context.newPage();
  const root=process.env.WORKBENCH_REVIEW_URL || 'http://127.0.0.1:5173';
  const seedFile='artifacts/phase-4/baseline/review-fixture-fake.json';
  const seed=JSON.parse(await fs.readFile(seedFile,'utf8'));
  if (!seed.models.length || !seed.models.every(m=>m.model_id.startsWith('fake-')) || !seed.bootstrap.connections.every(c=>c.base_url==='http://127.0.0.1:18080')) throw new Error('Review captures require the committed synthetic fixture.');
  const bootstrap=structuredClone(seed.bootstrap);
  bootstrap.app_name=process.env.WORKBENCH_REVIEW_BEFORE ? "Workbench" : "Atelier";
  const models=structuredClone(seed.models);
  const model=models.find(m=>m.model_id==='fake-reasoning');
  const fixed='2026-10-04T12:00:00+00:00';
  Object.assign(bootstrap.settings,{'appearance.theme':theme,default_connection_id:model.connection_id,default_model_id:model.model_id,new_chat_model:'fixed',user_name:'','web.default_on':false});
  const chat={id:'fake-review-chat',title:'Synthetic review conversation',title_source:'user',connection_id:model.connection_id,model_id:model.model_id,pinned:false,params:{},web_enabled:false,created_at:fixed,updated_at:fixed,current_leaf_id:'fake-assistant'};
  const stats={ttft_ms:800,total_ms:2000,prompt_tokens:32,completion_tokens:64,tokens_per_sec:32,tokens_estimated:false,context_length:16384,dropped_message_count:0,reasoning_ms:1000,finish_reason:'stop'};
  const user={id:'fake-user',chat_id:chat.id,role:'user',content:'Explain a small experiment.',status:'complete',attachments:[],created_at:fixed};
  const assistant={id:'fake-assistant',chat_id:chat.id,parent_id:user.id,role:'assistant',content:'A synthetic answer for reviewing the interface. Start with a clear question, change one thing, then compare the result. [1]',reasoning:'Synthetic reasoning for this review.',status:'complete',stats,model:{connection_id:model.connection_id,model_id:model.model_id,display_name:model.display_name},created_at:fixed,web:{status:'used',queries:['Synthetic query'],providers:['fake'],timings:{plan:150,search:400,fetch:500,rank:10},source_count:1,ranking:'keyword',plan_fallback:false}};
  assistant.content='A synthetic example of one code surface and one table. [1]\n\n```python\nprint(\"synthetic example\")\n```\n\n| Item | Value |\n|---|---|\n| First | 42 |\n| Second | 84 |';
  const source={n:1,url:'https://example.org/fake',title:'Synthetic review source',site_name:'Example',domain:'example.org',published_at:fixed,fetched_at:fixed,kind:'page',cited:true,passages:[{source_url:'https://example.org/fake',heading:'Example',ord:0,text:'Synthetic evidence for reviewing the citation card.',selection_applied:false}]};
  const recording={id:'fake-recording',kind:'audio',filename:'fake-recording.wav',mime_type:'audio/wav',bytes:64,audio_available:false,transcript:{status:'ready',channels:'mix',duration_seconds:75,word_count:18,token_estimate:35,elapsed_seconds:1,engine_model:'fake-whisper',warnings:[],correction_count:0}};
  const transcript={attachment:recording,text:'Synthetic transcript. Review the next release and follow up on Friday.',raw_text:'Synthetic transcript. Review the next release and follow up on Friday.',segments:[{start:0,end:75,text:'Synthetic transcript.',raw_text:'Synthetic transcript.',speaker:'Speaker 1'}],corrections:[]};
  let pending=[];
  await page.addInitScript(t=>{localStorage.setItem('workbench-theme',t); Date.prototype.getHours=()=>12;},theme);
  await page.route('**/api/**', async route=>{
   const url=new URL(route.request().url()), path=url.pathname;
   let body;
   if(path==='/api/bootstrap') body=bootstrap;
   else if(path==='/api/models') body=models;
   else if(path==='/api/chats') body={items:[chat],next_cursor:null};
   else if(path==='/api/chats/'+chat.id) body={chat,messages:[user,assistant],sources:{[assistant.id]:[source]},reads:{[assistant.id]:[]}};
   else if(path.endsWith('/context')) body={used_tokens:320,context_length:16384,dropped_message_count:0};
   else if(path==='/api/runs/active') body=[];
   else if(path==='/api/attachments/pending') body=pending;
   else if(path==='/api/attachments/fake-recording/transcript') body=transcript;
   else if(path==='/api/search/status') body=[];
   else if(path==='/api/transcription/status') body={available:true,audio_extensions:['.wav'],model:'fake-whisper',glossary_terms:0};
   else if(path.startsWith('/api/favicons/')) return route.fulfill({status:404});
   else return route.fulfill({status:404});
   await route.fulfill({json:body});
  });
  const settle=async()=>{
   await page.evaluate(()=>document.fonts.ready);
   await page.evaluate(async()=>{
    const start=performance.now();let clear=0;
    while(performance.now()-start<1000){
     await new Promise(requestAnimationFrame);
     const busy=document.getAnimations().some(a=>a.playState==='running'&&Number.isFinite(a.effect?.getComputedTiming().endTime));
     clear=busy?0:clear+1;if(clear>=2)return;
    }
    throw new Error('Finite capture motion did not settle');
   });
  };
  const shot=async name=>{await settle(); await fs.mkdir(output,{recursive:true});await page.screenshot({path:`${output}/${name}-${width}-${theme}-fake.png`,animations:'disabled'});if(process.env.WORKBENCH_REVIEW_AUDIT){await settle();const result=await new AxeBuilder({page}).analyze();await fs.writeFile(`${output}/axe-${name}-${width}-${theme}-fake.json`,JSON.stringify(result.violations,null,2));if(result.violations.some(v=>['serious','critical'].includes(v.impact)))throw new Error(`Accessibility gate failed: ${name} ${width} ${theme}`);} };
  await page.goto(root+'/c/'+chat.id);
  await page.getByText('A synthetic example of one code surface and one table.',{exact:false}).waitFor();
  await page.getByRole('article',{name:'assistant message'}).hover();
  await shot('surfaces');
  await page.getByRole('button',{name:'Actions for '+chat.title,exact:true}).last().click();
  await page.getByRole('menuitem',{name:'Delete',exact:true}).waitFor();
  await shot('chat-menu');
  await page.keyboard.press('Escape');
  await page.evaluate(()=>{const dt=new DataTransfer();dt.items.add(new File(['Synthetic drop preview'],'fake-example.txt',{type:'text/plain'}));document.querySelector('.app-main').dispatchEvent(new DragEvent('dragenter',{bubbles:true,dataTransfer:dt}));});
  await page.getByRole('status').filter({hasText:'Drop images'}).waitFor();
  await shot('drop-target');
  let release;
  const hold=new Promise(resolve=>release=resolve);
  await page.route(/\/api\/chats(?:\?.*)?$/,async route=>{await hold;await route.fulfill({json:{items:[chat],next_cursor:null}})});
  await page.goto(root+'/');
  await page.getByRole('button',{name:'Choose model',exact:true}).waitFor();
  if(width===390) await page.getByRole('button',{name:'Open sidebar',exact:true}).click();
  const historyScope=width===390 ? page.getByRole('dialog',{name:'Chat history'}) : page.locator('.sidebar-desktop');
  if(process.env.WORKBENCH_REVIEW_BEFORE) await historyScope.getByText('Loading chats…',{exact:true}).waitFor();
  else await historyScope.getByRole('status',{name:'Loading chats'}).waitFor();
  await shot('history-loading');
  release();
  await page.route('**/api/bootstrap',route=>route.abort());
  await page.goto(root+'/');
  await page.getByRole('heading',{name:/Can't reach/}).waitFor();
  await shot('offline');
  await context.close();
 }
 await browser.close();
})().catch(error=>{console.error(error);process.exit(1)});
