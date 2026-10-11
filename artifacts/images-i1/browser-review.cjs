const { chromium, webkit, expect } = require('../../web/node_modules/@playwright/test');
const { default: AxeBuilder } = require('../../web/node_modules/@axe-core/playwright');
const fs = require('node:fs');
const path = require('node:path');
(async () => {
 const results=[];
 for (const [name, engine, width] of [['webkit',webkit,390],['chromium',chromium,1440]]) {
  const browser=await engine.launch();
  try {
   const context=await browser.newContext({viewport:{width,height:844}});
   await context.request.patch('http://127.0.0.1:18082/api/settings',{data:{'appearance.theme':'dark'}});
   const page=await context.newPage();
   await page.goto('http://127.0.0.1:18082/images');
   await expect(page.locator('html')).toHaveAttribute('data-theme','dark');
   await page.getByRole('textbox',{name:'Prompt',exact:true}).fill(`Synthetic gallery review ${name}`);
   await page.getByRole('button',{name:'Generate one image',exact:true}).click();
   const card=page.getByRole('article').filter({hasText:`Synthetic gallery review ${name}`}).first();
   await expect(card.getByRole('button',{name:'Save',exact:true})).toBeVisible();
   await card.scrollIntoViewIfNeeded();
   await page.screenshot({path:path.join(__dirname,`browser/gallery-${width}-dark-${name}-fake.png`)});
   for (const label of ['Save','Details']) {
    await card.getByRole('button',{name:label,exact:true}).click();
    const dialog=page.getByRole('dialog');await expect(dialog).toBeVisible();
    if(label==='Save') await dialog.getByRole('button',{name:'Details (.json)',exact:true}).click();
    await page.waitForTimeout(350);
    const scan=await new AxeBuilder({page}).analyze();
    const issues=scan.violations.filter(v=>['serious','critical'].includes(v.impact??''));
    if(issues.length) throw new Error(JSON.stringify(issues));
    await page.screenshot({path:path.join(__dirname,`browser/gallery-${label.toLowerCase()}-${width}-dark-${name}-fake.png`)});
    results.push({browser:name,width,screen:label,seriousCritical:issues.length});
    await page.keyboard.press('Escape');
   }
  } finally {await browser.close();}
 }
 fs.writeFileSync(path.join(__dirname,'browser-review-corrected.json'),JSON.stringify({synthetic_only:true,checks:results},null,2)+'\n');
})().catch(error=>{process.stderr.write(String(error)+'\n');process.exitCode=1;});
