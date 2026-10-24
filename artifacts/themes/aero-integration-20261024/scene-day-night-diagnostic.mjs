import { createRequire } from 'node:module';
import { mkdir, writeFile } from 'node:fs/promises';
const root='/Users/evilius/.codex/worktrees/aero-theme-preview/agents-agenticrag';
const require=createRequire(root+'/web/package.json');
const { chromium, webkit, devices }=require('@playwright/test');
const output=root+'/artifacts/themes/aero-integration-20261024';
await mkdir(output,{recursive:true});
const rows=[];
for(const [engine,browserType] of Object.entries({chromium,webkit})) {
 const browser=await browserType.launch();
 try {
  for(const mode of ['Light','Dark']) {
   const context=await browser.newContext(engine==='webkit' ? {...devices['iPhone 13']} : {viewport:{width:1440,height:1000}});
   try {
    const page=await context.newPage();
    const api=[];
    await page.route('**/api/**',route=>{api.push(route.request().url());return route.abort();});
    await page.emulateMedia({reducedMotion:'no-preference',colorScheme:mode.toLowerCase()});
    await page.goto('http://127.0.0.1:5173/design?themes');
    const controls=page.getByRole('region',{name:'Controls'});
    await controls.getByRole('button',{name:'Aero',exact:true}).click();
    await controls.getByRole('button',{name:mode,exact:true}).click();
    await page.locator('.theme-lab-window').scrollIntoViewIfNeeded();
    // Measure the ambient scene after the bounded decorative greeting.
    await page.waitForTimeout(5000);
    const metrics=await page.evaluate(async()=>{
     const times=[];let previous=0;
     for(let i=0;i<180;i++) await new Promise(resolve=>requestAnimationFrame(now=>{if(previous)times.push(now-previous);previous=now;resolve();}));
     times.sort((a,b)=>a-b);
     return {samples:times.length,median_ms:times[Math.floor(times.length*.5)],p95_ms:times[Math.floor(times.length*.95)],running_scene_animations:document.querySelector('.theme-lab-window .aero-scene').getAnimations({subtree:true}).filter(a=>a.playState==='running').length};
    });
    rows.push({engine,mode,api_calls:api,scope:'Mac browser ambient-scene rAF diagnostic; not physical iPhone GPU/FPS certification',...metrics});
    await writeFile(output+'/scene-day-night-diagnostic.json',JSON.stringify(rows,null,2)+'\n');
    if(api.length || metrics.samples!==179 || !metrics.running_scene_animations || metrics.median_ms>=20) throw new Error(JSON.stringify(rows.at(-1)));
   } finally {await context.close();}
  }
 } finally {await browser.close();}
}
console.log(JSON.stringify(rows,null,2));
