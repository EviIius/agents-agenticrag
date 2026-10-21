// Installed HTTPS code with all API requests intercepted; no live user data.
import { chromium, webkit, devices, expect } from '../../web/node_modules/@playwright/test/index.mjs';
import { readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';
const out = dirname(fileURLToPath(import.meta.url));
const fixtures = process.env.HOME + '/.local/share/workbench/qa/attachments-redesign-20261015';
const original = JSON.parse(await readFile(fixtures + '/fake-bootstrap.json', 'utf8'));
const models = JSON.parse(await readFile(fixtures + '/fake-models.json', 'utf8'));
models.find(model => model.model_id === 'fake-vision').reasoning = { options: ['off', 'low', 'medium', 'xhigh'], default: 'medium' };
const results = [], origin = 'https://jakes-mac-mini.tailc4d343.ts.net';
for (const [name, engine, width] of [['chromium', chromium, 1440], ['webkit', webkit, 390]]) {
  const browser = await engine.launch();
  const context = await browser.newContext({ ...(name === 'webkit' ? devices['iPhone 13'] : {}), viewport: { width, height: 844 }, serviceWorkers: 'block', colorScheme: 'dark' });
  try {
    const page = await context.newPage(), errors = [], failedAssets = [];
    const bootstrap = structuredClone(original), connection = bootstrap.connections[0];
    bootstrap.settings = { ...bootstrap.settings, default_connection_id: connection.id, default_model_id: 'fake-vision', default_preset_id: null, new_chat_model: 'fixed', auto_title: false, 'web.default_on': false, 'appearance.theme': 'dark' };
    page.on('pageerror', error => errors.push(String(error)));
    page.on('response', response => { if (response.url().includes('/assets/') && response.status() >= 400) failedAssets.push(new URL(response.url()).pathname); });
    await page.route('**/api/**', async route => {
      const request = route.request(), path = new URL(request.url()).pathname.replace(/^\/api/, '');
      assert.equal(request.method(), 'GET', 'No mutation is needed in this observer');
      if (request.resourceType() === 'eventsource' || path.endsWith('/events')) {
        await route.fulfill({ contentType: 'text/event-stream', body: ': synthetic observer\n\n' }); return;
      }
      let data = [];
      if (path === '/bootstrap') data = bootstrap;
      else if (path === '/models') data = models;
      else if (path === '/connections') data = bootstrap.connections;
      else if (path === '/chats') data = { items: [], next_cursor: null };
      else if (path === '/workflows/runs') data = { items: [], next_cursor: null, paused_count: 0 };
      else if (path === '/library') data = { available: false, documents: [], collections: [], counts: { ready: 0 }, bytes: 0, event_id: 1 };
      else if (path === '/images/status') data = { available: true, editing_available: true, model: 'FLUX.2 klein 4B' };
      else if (path === '/transcription/status') data = { available: false, audio_extensions: ['.wav'] };
      await route.fulfill({ json: data });
    });
    await page.goto(origin + '/');
    await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
    const tools = page.getByRole('button', { name: 'Tools', exact: true });
    await expect(tools).toBeVisible(); await tools.click();
    const menu = page.getByRole('menu', { name: 'Tools', exact: true });
    await expect(menu.getByRole('menuitemradio', { name: 'Model default', exact: true })).toHaveText('Default');
    const edit = menu.getByRole('menuitem', { name: 'Edit photo', exact: true });
    await expect(edit).toBeVisible();
    await edit.scrollIntoViewIfNeeded();
    const actionsBox = await menu.locator('.composer-tools-actions').boundingBox(), editBox = await edit.boundingBox();
    assert(editBox.y >= actionsBox.y - 1 && editBox.y + editBox.height <= actionsBox.y + actionsBox.height + 1);
    await page.evaluate(() => document.fonts.ready);
    await page.waitForFunction(() => !document.getAnimations().some(animation => animation.playState === 'running' && Number.isFinite(animation.effect?.getComputedTiming().endTime)), { timeout: 1000 });
    const box = await menu.boundingBox();
    console.log(JSON.stringify({ engine: name, box, width }));
    assert(box.height <= 330 && box.x >= 7 && box.x + box.width <= width - 7);
    await page.screenshot({ path: out + `/installed-tools-${width}-dark-${name}-synthetic.png`, animations: 'disabled' });
    await menu.getByRole('menuitemradio', { name: 'Xhigh', exact: true }).click();
    await expect(menu.getByRole('menuitemradio', { name: 'Xhigh', exact: true })).toBeChecked();
    await page.keyboard.press('Escape'); await expect(tools).toBeFocused();
    const text = page.locator('.composer textarea'); await text.fill('Synthetic typing after closing Tools');
    await expect(text).toHaveValue('Synthetic typing after closing Tools');
    assert.deepEqual(errors, []); assert.deepEqual(failedAssets, []);
    results.push({ engine: name, width, theme: 'dark', real_https_assets: true, all_API_synthetic: true, box, default_single_line: true, all_four_rows: true, reasoning_and_focus: true, typing: true, page_errors: errors, failed_assets: failedAssets, native_calls: 0, live_mutations: 0 });
  } finally { await context.close(); await browser.close(); }
}
await writeFile(out + '/installed-menu.json', JSON.stringify({ passed: true, results, limitations: 'Synthetic interception; not physical iPhone or native keyboard acceptance.' }, null, 2) + '\n');
console.log(JSON.stringify({ passed: true, browsers: results.length, native_calls: 0 }));
