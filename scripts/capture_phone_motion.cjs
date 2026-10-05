const { chromium, webkit } = require(process.cwd() + '/web/node_modules/playwright');
const fs = require('node:fs/promises');
const AxeBuilder = require(process.cwd() + '/web/node_modules/@axe-core/playwright').default;
(async () => {
 const out='artifacts/phase-4/4d-phone-fix';
 const seed=JSON.parse(await fs.readFile('artifacts/phase-4/baseline/review-fixture-fake.json','utf8'));
 if(!seed.models.every(m=>m.model_id.startsWith('fake-')))throw Error('Synthetic models required');
 const observations=[];
 for(const [engine,driver] of [['chromium',chromium],['webkit',webkit]]) {
  const browser=await driver.launch();
  const context=await browser.newContext({viewport:{width:390,height:844},recordVideo:{dir:'artifacts/phase-4/motion/phone-fix',size:{width:390,height:844}},reducedMotion:'no-preference',isMobile:true,hasTouch:true});
  const page=await context.newPage();
  const bootstrap=structuredClone(seed.bootstrap);
  Object.assign(bootstrap.settings,{'appearance.theme':'dark','appearance.reduce_motion':'system',default_connection_id:seed.models[0].connection_id,default_model_id:seed.models[0].model_id,user_name:''});
  await page.route('**/api/**',async route=>{
   const path=new URL(route.request().url()).pathname;
   let body;
   if(path==='/api/bootstrap')body=bootstrap;
   else if(path==='/api/settings'){Object.assign(bootstrap.settings,route.request().postDataJSON()||{});body=bootstrap.settings;}
   else if(path==='/api/models')body=seed.models;
   else if(path==='/api/chats')body={items:[],next_cursor:null};
   else if(path==='/api/runs/active'||path==='/api/attachments/pending')body=[];
   else if(path==='/api/transcription/status')body={available:false,audio_extensions:['.wav'],glossary_terms:0};
   else return route.fulfill({status:404});
   await route.fulfill({json:body});
  });
  await page.goto('http://127.0.0.1:5173/');
  await page.getByRole('button',{name:'Choose model',exact:true}).click();
  await page.getByRole('button',{name:'Manage models…',exact:true}).click();
  const settings=page.getByRole('dialog',{name:'Settings',exact:true});
  await settings.getByRole('button',{name:'Appearance',exact:true}).click();
  await settings.getByRole('combobox',{name:'Reduce motion'}).click();
  await page.getByRole('option',{name:'Always',exact:true}).click();
  await page.getByRole('listbox').waitFor({state:'detached'});
  await page.screenshot({path:`${out}/appearance-always-390-dark-${engine}-fake.png`});
  const axe=(await new AxeBuilder({page}).analyze()).violations;
  if(axe.some(v=>['serious','critical'].includes(v.impact)))throw Error('Accessibility failure');
  observations.push({engine,selectorDismissed:true,reduceMotion:await page.locator('html').getAttribute('data-reduce-motion'),settingsAnimation:await settings.evaluate(el=>getComputedStyle(el).animationName),seriousCritical:0});
  await settings.getByRole('combobox',{name:'Reduce motion'}).click();
  await page.getByRole('option',{name:'Follow system',exact:true}).click();
  await settings.getByRole('button',{name:'Close settings'}).click();
  await page.reload();
  await page.locator('.composer textarea').waitFor();
  await page.waitForTimeout(500);
  await context.close(); await browser.close();
 }
 for (const name of await fs.readdir('artifacts/phase-4/motion/phone-fix')) {
  if(name.startsWith('page@')) await fs.rename(`artifacts/phase-4/motion/phone-fix/${name}`,`artifacts/phase-4/motion/phone-fix/synthetic-phone-${name.replace('page@','').replace('.webm','')}-fake.webm`);
 }
 await fs.writeFile(`${out}/synthetic-observation.json`,JSON.stringify(observations,null,2)+'\n');
})();
