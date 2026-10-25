// Real installed HTTPS assets; all API traffic is intercepted with synthetic data.
import { createRequire } from 'node:module';
import { writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';

const out = dirname(fileURLToPath(import.meta.url));
const root = new URL('../../../', import.meta.url).pathname;
const require = createRequire(root + 'web/package.json');
const { chromium, webkit, devices, expect } = require('@playwright/test');
const original = await (await fetch('http://127.0.0.1:18787/api/bootstrap')).json();
const models = await (await fetch('http://127.0.0.1:18787/api/models')).json();
const connection = original.connections.find(c => c.name === 'Fake runtime' && c.base_url === 'http://127.0.0.1:18080');
assert(connection);
assert(models.every(m => m.model_id.startsWith('fake-')));
models.find(m => m.model_id === 'fake-vision').reasoning = { options: ['off', 'low', 'medium', 'xhigh'], default: 'medium' };
const origin = 'https://jakes-mac-mini.tailc4d343.ts.net';
const palettes = ['cobalt', 'lime', 'paper', 'ember', 'orchid', 'midnight', 'mono', 'aero'];
const results = [];

for (const [name, engine, width] of [['chromium', chromium, 1440], ['webkit', webkit, 390]]) {
  const browser = await engine.launch();
  const context = await browser.newContext({ ...(name === 'webkit' ? devices['iPhone 13'] : {}), viewport: { width, height: 900 }, serviceWorkers: 'block' });
  try {
    const page = await context.newPage(), errors = [], assets = [], mutations = [];
    const bootstrap = {
      ...original, connections: [{ ...connection, name: 'Synthetic runtime' }],
      data_dir: '/synthetic-theme-observer', settings: {
        default_connection_id: connection.id, default_model_id: 'fake-vision',
        default_preset_id: null, new_chat_model: 'fixed', auto_title: false,
        'web.default_on': false, 'appearance.palette': 'cobalt',
        'appearance.theme': 'light', 'appearance.greeting': 'english',
        'appearance.reduce_motion': 'system', 'appearance.name': 'Taylor',
      },
    };
    page.on('pageerror', e => errors.push(String(e)));
    page.on('response', r => {
      if (/\/(?:assets\/.*\.(?:js|css)|theme-init\.js|icons\/|manifests\/)/.test(r.url()))
        assets.push({ path: new URL(r.url()).pathname, status: r.status() });
    });
    await page.route('**/api/**', async route => {
      const request = route.request(), path = new URL(request.url()).pathname.replace(/^\/api/, '');
      if (request.method() === 'PATCH' && path === '/settings') {
        const body = request.postDataJSON();
        Object.assign(bootstrap.settings, body);
        mutations.push({ path, keys: Object.keys(body) });
        await route.fulfill({ json: bootstrap.settings }); return;
      }
      if (request.method() !== 'GET') {
        await route.fulfill({ status: 503, json: { error: { code: 'synthetic_observer', message: 'No live request sent.' } } }); return;
      }
      if (path.endsWith('/events') || request.resourceType() === 'eventsource') {
        await route.fulfill({ contentType: 'text/event-stream', body: ': synthetic theme observer\n\n' }); return;
      }
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
      await route.fulfill({ json: data });
    });
    await page.emulateMedia({ reducedMotion: 'reduce', colorScheme: 'light' });
    await page.goto(origin + '/');
    await expect(page).toHaveTitle('Aether');
    await expect(page.locator('.composer textarea')).toBeVisible();
    if (width < 768) await page.getByRole('button', { name: 'Open sidebar', exact: true }).click();
    await page.getByRole('button', { name: 'Settings', exact: true }).click();
    const dialog = page.getByRole('dialog', { name: 'Settings', exact: true });
    await dialog.getByRole('button', { name: 'Appearance', exact: true }).click();
    for (const palette of palettes) {
      await dialog.locator(`[data-palette-option="${palette}"]`).click();
      await expect(page.locator('html')).toHaveAttribute('data-palette', palette);
      await expect.poll(() => bootstrap.settings['appearance.palette']).toBe(palette);
    }
    await page.screenshot({ path: out + `/appearance-${width}-${name}-synthetic.png` });
    await page.keyboard.press('Escape');
    await page.reload();
    await expect(page.locator('html')).toHaveAttribute('data-palette', 'aero');
    await expect(page.locator('.empty-chat .aero-scene')).toBeVisible();
    await expect(page.locator('.aero-bubble')).toHaveCount(9);
    const input = page.locator('.composer textarea');
    await input.fill('Synthetic ordinary typing check');
    await expect(input).toHaveValue('Synthetic ordinary typing check');
    await expect(page.getByRole('button', { name: 'Send message', exact: true })).toBeEnabled();
    await page.getByRole('button', { name: 'Tools', exact: true }).click();
    await expect(page.getByRole('menuitemradio', { name: 'Model default', exact: true })).toBeVisible();
    await page.keyboard.press('Escape');
    await page.emulateMedia({ reducedMotion: 'no-preference' });
    await expect.poll(() => page.locator('.aero-scene').evaluate(el => el.getAnimations({ subtree: true }).filter(a => a.playState === 'running').length)).toBeGreaterThan(0);
    await page.emulateMedia({ reducedMotion: 'reduce' });
    await expect.poll(() => page.locator('.aero-scene').evaluate(el => el.getAnimations({ subtree: true }).filter(a => a.playState === 'running').length)).toBe(0);
    await page.screenshot({ path: out + `/new-chat-${width}-${name}-synthetic.png` });
    await page.goto(origin + '/workflows');
    await expect(page.getByRole('heading', { name: 'Workflows', exact: true })).toBeVisible();
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    assert.deepEqual(errors, []);
    assert(assets.length && assets.every(a => a.status === 200));
    results.push({ engine: name, width, palettes_saved: palettes, aero_reloaded: true, scene_and_bubbles: true, typing_and_send_enabled: true, tools_default_visible: true, normal_and_reduced_scene: true, workflows_open: true, page_errors: errors, assets_checked: assets.length, synthetic_preference_requests: mutations.length, live_api_mutations: 0, model_calls: 0 });
    await writeFile(out + '/installed-ui.json', JSON.stringify({ passed: results.length === 2, origin, results, scope: 'Actual HTTPS assets with all API calls intercepted; not a physical iPhone check or real preference mutation' }, null, 2) + '\n');
  } finally { await context.close(); await browser.close(); }
}
console.log(JSON.stringify({ passed: true, engines: results.length, model_calls: 0, live_api_mutations: 0 }));
