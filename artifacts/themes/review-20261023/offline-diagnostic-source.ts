import { test, expect } from "@playwright/test";
import { writeFileSync } from "node:fs";
import { fakeAppURL } from "../test-runtime";
test("compare old and new cached assets under WebKit offline emulation", async ({page, context}) => {
 await page.goto(fakeAppURL);
 await page.evaluate(()=>navigator.serviceWorker.ready);
 await expect.poll(()=>page.evaluate(()=>!!navigator.serviceWorker.controller)).toBe(true);
 await page.reload();
 const urls=["/icons/apple-touch-icon.png","/icons/lime/apple-touch-icon.png","/manifest.webmanifest","/manifests/lime.webmanifest"];
 const online=await page.evaluate(async urls=>Promise.all(urls.map(async url=>({url,ok:(await fetch(url)).ok}))),urls);
 await context.setOffline(true);
 const offline=await page.evaluate(async urls=>Promise.all(urls.map(async url=>{
  let fetched;try {const response=await fetch(url);fetched={ok:response.ok,bytes:(await response.arrayBuffer()).byteLength};}catch(error){fetched={error:String(error)};}
  const cached=await caches.match(url);
  return {url,fetched,cache:cached?{ok:cached.ok,bytes:(await cached.arrayBuffer()).byteLength}:null};
 })),urls);
 writeFileSync(`../artifacts/themes/review-20261023/offline-diagnostic-${test.info().project.name}.json`,JSON.stringify({online,offline},null,2));
});
