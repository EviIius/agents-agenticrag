// Actual installed HTTPS assets; every API response below contains invented data.
import { createRequire } from 'node:module';
import { writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';

const out = dirname(fileURLToPath(import.meta.url));
const root = new URL('../../', import.meta.url).pathname;
const require = createRequire(root + 'web/package.json');
const { chromium, webkit, devices, expect } = require('@playwright/test');
const source = await (await fetch('http://127.0.0.1:18787/api/bootstrap')).json();
const models = await (await fetch('http://127.0.0.1:18787/api/models')).json();
const connection = source.connections.find(c => c.name === 'Fake runtime' && c.base_url === 'http://127.0.0.1:18080');
assert(connection && models.length && models.every(m => m.model_id.startsWith('fake-')));
const origin = 'https://jakes-mac-mini.tailc4d343.ts.net';
const picture = `<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024"><defs><pattern id="p" width="100" height="100" patternUnits="userSpaceOnUse"><rect width="100" height="100" fill="white"/><rect width="50" height="50" fill="black"/><rect x="50" y="50" width="50" height="50" fill="black"/><circle cx="50" cy="50" r="30" fill="#ff3b30"/></pattern></defs><rect width="1024" height="1024" fill="url(#p)"/></svg>`;
const job = { id: 'b'.repeat(32), prompt: 'Synthetic release glass background', seed: 42, mode: 'generate', export_bytes: 0, state: 'complete', stage: 'Image saved', completed_steps: 4, steps: 4, created_at: '2026-10-25T12:00:00Z', updated_at: '2026-10-25T12:00:10Z', image_bytes: 2048, metadata_bytes: 100, sha256: 'a'.repeat(64), error: null };
const storage = { outputs: 1, versions: 0, image_bytes: 2048, metadata_bytes: 100, manifest_bytes: 100, database_bytes: 8192, backup_bytes: 0, free_bytes: 150e9, references: 0, reference_bytes: 0, reference_metadata_bytes: 0, export_bytes: 0, measurement_bytes: 0 };
const results = [];

async function glass(page, selector, overlay = false) {
  const panel = page.locator(selector).filter({ visible: true }).first();
  await expect(panel).toBeVisible();
  const value = await panel.evaluate(el => {
    const s = getComputedStyle(el), ctx = document.createElement('canvas').getContext('2d');
    ctx.fillStyle = s.backgroundColor; ctx.fillRect(0, 0, 1, 1);
    return { filter: s.backdropFilter, background: s.backgroundColor, alpha: ctx.getImageData(0, 0, 1, 1).data[3] / 255 };
  });
  assert(value.filter.includes('blur(18px)'));
  if (overlay) assert(value.alpha >= 0.92);
  return value;
}

for (const [name, engine, width] of [['chromium', chromium, 1440], ['webkit', webkit, 390]]) {
  const browser = await engine.launch();
  try {
    for (const theme of ['light', 'dark']) {
      const context = await browser.newContext({ ...(name === 'webkit' ? devices['iPhone 13'] : {}), viewport: { width, height: width === 390 ? 844 : 1000 }, serviceWorkers: 'block' });
      try {
        const page = await context.newPage(), errors = [], failedAssets = [], requests = [];
        let syntheticPatches = 0, pictureResponses = 0;
        const bootstrap = { ...source, connections: [{ ...connection, name: 'Synthetic runtime' }], data_dir: '/synthetic-blur-release', settings: { default_connection_id: connection.id, default_model_id: 'fake-vision', default_preset_id: null, new_chat_model: 'fixed', auto_title: false, 'web.default_on': false, 'appearance.palette': 'aero', 'appearance.theme': theme, 'appearance.greeting': 'english', 'appearance.reduce_motion': 'system', 'appearance.name': 'Taylor' } };
        page.on('pageerror', e => errors.push(String(e)));
        page.on('response', r => { if (/\/(?:assets\/|fonts\/|icons\/|theme-init\.js)/.test(r.url()) && r.status() !== 200) failedAssets.push({ path: new URL(r.url()).pathname, status: r.status() }); });
        await page.route('**/api/**', async route => {
          const req = route.request(), path = new URL(req.url()).pathname.replace(/^\/api/, '');
          requests.push({ method: req.method(), path });
          if (path.endsWith('/output/png')) { pictureResponses++; await route.fulfill({ contentType: 'image/svg+xml', body: picture }); return; }
          if (path === '/settings' && req.method() === 'PATCH') { Object.assign(bootstrap.settings, req.postDataJSON()); syntheticPatches++; await route.fulfill({ json: bootstrap.settings }); return; }
          if (req.method() !== 'GET') { await route.fulfill({ status: 503, json: { error: { code: 'synthetic_observer', message: 'No live mutation sent.' } } }); return; }
          if (path === '/images/events') { await route.fulfill({ contentType: 'text/event-stream', body: 'id: 1\nevent: image.snapshot\ndata: ' + JSON.stringify({ jobs: [job], storage }) + '\n\n' }); return; }
          if (path.endsWith('/events') || req.resourceType() === 'eventsource') { await route.fulfill({ contentType: 'text/event-stream', body: ': synthetic observer\n\n' }); return; }
          let data = [];
          if (path === '/bootstrap') data = bootstrap;
          else if (path === '/settings') data = bootstrap.settings;
          else if (path === '/models') data = models;
          else if (path === '/connections') data = bootstrap.connections;
          else if (path === '/chats') data = { items: [], next_cursor: null };
          else if (path === '/library') data = { available: false, documents: [], collections: [], counts: { ready: 0 }, bytes: 0, event_id: 1 };
          else if (path.includes('/context')) data = { used_tokens: 0, context_length: 32768, dropped_message_count: 0 };
          else if (path === '/workflows/runs') data = { items: [], next_cursor: null, paused_count: 0 };
          else if (path === '/transcription/status') data = { available: false, audio_extensions: ['.wav'] };
          else if (path === '/images/status') data = { available: true, editing_available: true, model: 'Synthetic image engine', width: 1024, height: 1024, steps: 4 };
          else if (path === '/images') data = { jobs: [job], storage };
          else if (path === '/images/jobs') data = [job];
          await route.fulfill({ json: data });
        });
        await page.emulateMedia({ reducedMotion: 'reduce', colorScheme: theme });
        await page.goto(origin + '/');
        await expect(page.locator('html')).toHaveAttribute('data-palette', 'aero');
        await expect(page.locator('html')).toHaveAttribute('data-theme', theme);
        const composer = await glass(page, '.composer'), topbar = await glass(page, '.topbar');
        if (width === 1440) await glass(page, '.bg-sidebar-bg');
        await page.locator('.composer textarea').fill('Synthetic typing check');
        await expect(page.getByRole('button', { name: 'Send message', exact: true })).toBeEnabled();
        await page.getByRole('button', { name: 'Tools', exact: true }).click();
        const tools = await glass(page, '[data-slot="dropdown-menu-content"]', true);
        await page.screenshot({ path: out + `/${name}-${theme}-${width}-tools-fake.png` });
        await page.keyboard.press('Escape');
        await page.goto(origin + '/images');
        const photo = page.getByRole('article').filter({ hasText: job.prompt }).locator('img');
        await expect(photo).toHaveJSProperty('naturalWidth', 1024);
        assert(pictureResponses > 0);
        if (width === 390) {
          await page.getByRole('button', { name: 'Open sidebar', exact: true }).click();
          await glass(page, '[data-slot="sheet-content"]', true);
        }
        await page.getByRole('button', { name: 'Settings', exact: true }).click();
        const dialog = page.getByRole('dialog', { name: 'Settings', exact: true });
        await dialog.getByRole('button', { name: 'Appearance', exact: true }).click();
        const settings = await glass(page, '[data-slot="dialog-content"]', true);
        await page.screenshot({ path: out + `/${name}-${theme}-${width}-settings-fake.png` });
        await page.keyboard.press('Escape');
        await page.goto(origin + '/');
        await expect(page.locator('.empty-chat .aero-scene')).toBeVisible();
        await page.emulateMedia({ reducedMotion: 'no-preference' });
        await expect.poll(() => page.locator('.aero-scene').evaluate(el => el.getAnimations({ subtree: true }).filter(a => a.playState === 'running').length)).toBeGreaterThan(0);
        await page.emulateMedia({ reducedMotion: 'reduce' });
        await expect.poll(() => page.locator('.aero-scene').evaluate(el => el.getAnimations({ subtree: true }).filter(a => a.playState === 'running').length)).toBe(0);
        await page.goto(origin + '/workflows');
        await expect(page.getByRole('heading', { name: 'Workflows', exact: true })).toBeVisible();
        assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
        assert.deepEqual(errors, []); assert.deepEqual(failedAssets, []);
        results.push({ engine: name, theme, width, composer, topbar, tools, settings, synthetic_picture_responses: pictureResponses, synthetic_preference_patches: syntheticPatches, intercepted_api_requests: requests.length, page_errors: errors, failed_assets: failedAssets, typing_send_enabled: true, workflows_open: true, normal_reduced_motion: true, live_api_mutations: 0, model_calls: 0 });
        await writeFile(out + '/installed-ui.json', JSON.stringify({ passed: results.length === 4, origin, scope: 'Actual HTTPS assets with all API responses intercepted; not an actual user send or physical iPhone/Safari application check', results }, null, 2) + '\n');
      } finally { await context.close(); }
    }
  } finally { await browser.close(); }
}
console.log(JSON.stringify({ passed: true, cases: results.length, live_api_mutations: 0, model_calls: 0 }));
