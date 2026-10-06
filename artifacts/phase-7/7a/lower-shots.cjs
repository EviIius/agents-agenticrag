const {chromium, webkit}=require('/Users/evilius/Documents/GitHub/agents-agenticrag/web/node_modules/playwright');
(async()=>{
 for(const [engine,type] of Object.entries({chromium,webkit})){
  const browser=await type.launch();
  try {
   for(const width of [390,1440]){
    const page=await browser.newPage({viewport:{width,height:900}});
    await page.goto('http://127.0.0.1:5173/design?library');
    await page.getByRole('button',{name:'dark',exact:true}).click();
    for(const state of ['Embedding','Ready']){
     await page.getByRole('combobox',{name:'Library preview state'}).selectOption(state);
     await page.waitForTimeout(500);
     await page.getByRole('button',{name:'Delete all library files',exact:true}).scrollIntoViewIfNeeded();
     await page.waitForTimeout(500);
     await page.screenshot({path:`/Users/evilius/Documents/GitHub/agents-agenticrag/artifacts/phase-7/7a/screenshots/library-${state.toLowerCase()}-files-${width}-dark-${engine}-fake.png`,animations:'disabled'});
    }
    await page.close();
   }
  } finally {await browser.close();}
 }
})().catch(e=>{console.error(e);process.exitCode=1});
