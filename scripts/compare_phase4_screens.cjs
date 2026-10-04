// Decode screenshots in the browser canvas: no extra package or image runtime.
const { chromium } = require(process.cwd() + '/web/node_modules/playwright');
const fs = require('node:fs/promises');
(async () => {
 const before = process.argv[2], after = process.argv[3];
 const browser = await chromium.launch();
 const page = await browser.newPage();
 const results=[];
 for(const name of (await fs.readdir(before)).filter(name=>name.endsWith('.png'))){
  const urls=await Promise.all([before,after].map(async dir=>'data:image/png;base64,'+(await fs.readFile(`${dir}/${name}`)).toString('base64')));
  const diff=await page.evaluate(async urls=>{
   const pixels=await Promise.all(urls.map(async url=>{const image=new Image();image.src=url;await image.decode();const canvas=document.createElement('canvas');canvas.width=image.width;canvas.height=image.height;const context=canvas.getContext('2d');context.drawImage(image,0,0);return context.getImageData(0,0,image.width,image.height);}));
   const [a,b]=pixels;
   if(a.width!==b.width||a.height!==b.height)return {sizeChanged:true};
   let changed=0, beyondAntialiasing=0,maxDelta=0;
   for(let i=0;i<a.data.length;i+=4){let delta=0;for(let c=0;c<4;c++)delta=Math.max(delta,Math.abs(a.data[i+c]-b.data[i+c]));if(delta)changed++;if(delta>8)beyondAntialiasing++;maxDelta=Math.max(maxDelta,delta);}
   return {changed,beyondAntialiasing,maxDelta,pixels:a.width*a.height};
  },urls);
  results.push({name,...diff});
 }
 await browser.close();
 console.log(JSON.stringify({threshold:8,results},null,2));
 if(results.some(r=>r.sizeChanged||r.beyondAntialiasing))process.exitCode=1;
})().catch(error=>{console.error(error);process.exit(1)});
