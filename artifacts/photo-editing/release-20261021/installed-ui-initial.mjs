// Real installed HTTPS assets; every API request is intercepted with invented data.
import { chromium, webkit, devices, expect } from '/Users/evilius/.codex/worktrees/workflow-studio/agents-agenticrag/web/node_modules/@playwright/test/index.mjs';
import { readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';

const out = dirname(fileURLToPath(import.meta.url));
const repo = '/Users/evilius/.codex/worktrees/workflow-studio/agents-agenticrag';
const fixtures = process.env.HOME + '/.local/share/workbench/qa/attachments-redesign-20261015';
const original = JSON.parse(await readFile(fixtures + '/fake-bootstrap.json', 'utf8'));
const models = JSON.parse(await readFile(fixtures + '/fake-models.json', 'utf8'));
const png = await readFile(repo + '/server/tests/fixtures/images/fake-synthetic.png');
const origin = 'https://jakes-mac-mini.tailc4d343.ts.net';
const results = [];
for (const [name, engine, width] of [['chromium', chromium, 1440], ['webkit', webkit, 390]]) {
  const browser = await engine.launch();
  const context = await browser.newContext({ ...(name === 'webkit' ? devices['iPhone 13'] : {}), viewport: { width, height: 844 }, serviceWorkers: 'block' });
  try {
    const page = await context.newPage(), errors = [], assets = [], requests = [];
    const bootstrap = structuredClone(original), connection = bootstrap.connections[0];
    bootstrap.settings = { ...bootstrap.settings, default_connection_id: connection.id, default_model_id: 'fake-vision', default_preset_id: null, new_chat_model: 'fixed', auto_title: false, 'web.default_on': false, 'appearance.reduce_motion': 'system' };
    const date = '2026-10-21T12:00:00Z', chatId = 'd'.repeat(32), refId = 'c'.repeat(32), jobId = 'a'.repeat(32);
    const ref = { id: refId, chat_id: chatId, available: true, original_bytes: png.length, working_bytes: png.length, width: 32, height: 32, original_format: 'PNG', created_at: date };
    const job = { id: jobId, parent_id: null, mode: 'edit', reference: ref, prompt: 'Change the synthetic background to cobalt.', seed: 42, state: 'complete', stage: 'Complete', completed_steps: 4, steps: 4, created_at: date, updated_at: date, image_bytes: png.length, metadata_bytes: 100, export_bytes: png.length };
    const chat = { id: chatId, title: 'Synthetic release check', title_source: 'manual', connection_id: connection.id, model_id: 'fake-vision', system_prompt: null, params: {}, web_enabled: false, library_enabled: false, current_leaf_id: null, pinned: false, created_at: date, updated_at: date };
    const user = { id: 'e'.repeat(32), chat_id: chatId, parent_id: null, role: 'user', kind: 'image', content: job.prompt, status: 'complete', created_at: date };
    const reply = { id: 'f'.repeat(32), chat_id: chatId, parent_id: user.id, role: 'assistant', kind: 'image', content: '', status: 'complete', created_at: date, images: [job] };
    let complete = false, submitted = null, interceptedPosts = 0, downloads = 0;
    page.on('pageerror', error => errors.push(String(error)));
    page.on('response', response => { if (/\/assets\/.*\.(?:js|css)$/.test(response.url())) assets.push({ path: new URL(response.url()).pathname, status: response.status() }); });
    page.on('download', () => downloads++);
    await page.route('**/api/**', async route => {
      const request = route.request(), path = new URL(request.url()).pathname.replace(/^\/api/, '');
      requests.push({ method: request.method(), path });
      if (request.method() !== 'GET') interceptedPosts++;
      if (request.resourceType() === 'eventsource' || (request.headers()['accept'] ?? '').includes('text/event-stream') || path.endsWith('/events')) {
        await route.fulfill({ contentType: 'text/event-stream', body: ': synthetic installed UI observer\n\n' }); return;
      }
      if (path.endsWith('/preview') || path.endsWith('/reference') || path.includes('/output/')) {
        await route.fulfill({ contentType: 'image/png', body: png }); return;
      }
      let data = [], status = 200;
      if (path === '/chats' && request.method() === 'POST') { status = 201; data = chat; }
      else if (path === `/chats/${chatId}/image-references` && request.method() === 'POST') { status = 201; data = ref; }
      else if (path === `/chats/${chatId}/images` && request.method() === 'POST') {
        submitted = request.postDataJSON(); complete = true; chat.current_leaf_id = reply.id; status = 202; data = { user, assistant: reply };
      }
      else if (request.method() !== 'GET') {
        await route.fulfill({ status: 503, json: { error: { code: 'synthetic_release_check', message: 'Synthetic observer: no model request was sent.' } } }); return;
      }
      else if (path === '/bootstrap') data = bootstrap;
      else if (path === '/models') data = models;
      else if (path === '/connections') data = bootstrap.connections;
      else if (path === '/library') data = { available: false, documents: [], collections: [], counts: { ready: 0 }, bytes: 0, event_id: 1 };
      else if (path === '/chats') data = { items: complete ? [chat] : [], next_cursor: null };
      else if (path === `/chats/${chatId}`) data = { chat, messages: complete ? [user, reply] : [], sources: {}, reads: {} };
      else if (path.includes('/context')) data = { used_tokens: 0, context_length: 32768, dropped_message_count: 0 };
      else if (path === '/workflows/runs') data = { items: [], next_cursor: null, paused_count: 0 };
      else if (path === '/transcription/status') data = { available: false, audio_extensions: ['.wav'] };
      else if (path === '/images/status') data = { available: true, editing_available: true, model: 'FLUX.2 klein 4B', width: 1024, height: 1024, steps: 4 };
      await route.fulfill({ status, json: data });
    });
    await page.goto(origin + '/');
    await expect(page).toHaveTitle('Aether');
    const normal = page.locator('.composer textarea');
    await expect(normal).toBeVisible(); await normal.fill('Synthetic ordinary draft');
    await page.getByRole('button', { name: 'Tools', exact: true }).click();
    await expect(page.getByRole('menuitemradio', { name: 'Model default', exact: true })).toBeVisible();
    const picker = page.waitForEvent('filechooser');
    await page.getByRole('menuitem', { name: 'Edit photo', exact: true }).click();
    await (await picker).setFiles({ name: 'Synthetic-photo.png', mimeType: 'image/png', buffer: png });
    const instruction = page.getByRole('textbox', { name: 'Photo edit instruction', exact: true });
    await expect(instruction).toBeVisible();
    await expect(page.locator('[data-slot="photo-reference"]')).toContainText('Ready');
    await instruction.fill(job.prompt);
    await page.screenshot({ path: out + `/editor-${width}-dark-${name}-synthetic.png` });
    await page.getByRole('button', { name: 'Edit photo', exact: true }).click();
    await expect(page).toHaveURL(origin + '/c/' + chatId);
    assert.equal(submitted.reference_id, refId); assert.equal(submitted.count, 1); assert.equal(submitted.seeds.length, 1);
    await expect(page.getByText('FLUX.2 klein 4B · Photo edit', { exact: true })).toBeVisible();
    await page.getByRole('button', { name: 'Open image 1', exact: true }).click();
    const viewer = page.getByRole('dialog', { name: 'Image viewer', exact: true });
    await viewer.getByRole('button', { name: 'Show reference', exact: true }).click();
    await expect(viewer.getByRole('img', { name: 'Normalized photo reference' })).toHaveAttribute('src', /\/reference$/);
    await expect(viewer.getByRole('button', { name: 'Save image', exact: true })).toHaveCount(0);
    await viewer.getByRole('button', { name: 'Show edited image', exact: true }).click();
    await expect(viewer.getByRole('button', { name: 'Save image', exact: true })).toBeVisible();
    await page.screenshot({ path: out + `/viewer-${width}-dark-${name}-synthetic.png` });
    await viewer.getByRole('button', { name: 'Close image viewer', exact: true }).click();
    await page.getByRole('button', { name: 'Leave photo edit mode', exact: true }).click();
    await expect(page.locator('.composer textarea')).toHaveValue('Synthetic ordinary draft');
    await page.locator('.composer textarea').fill('Synthetic normal typing after edit');
    await expect(page.getByRole('button', { name: 'Send message', exact: true })).toBeEnabled();
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
    await page.goto(origin + '/workflows');
    await expect(page.getByRole('heading', { name: 'Workflows', exact: true })).toBeVisible();
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
    assert.deepEqual(errors, []); assert(assets.length > 0 && assets.every(asset => asset.status === 200));
    results.push({ engine: name, width, real_https_assets: true, all_api_intercepted: true, edit_picker_ready: true, bound_reference_submission: true, completed_card_and_comparison: true, save_control_available: true, normal_draft_and_typing_preserved: true, send_enabled: true, workflows_open: true, no_overflow: true, page_errors: errors, failed_assets: [], intercepted_posts: interceptedPosts, live_api_mutations: 0, native_model_calls: 0, native_share_not_invoked: true, downloads });
  } finally { await context.close(); await browser.close(); }
}
await writeFile(out + '/installed-ui.json', JSON.stringify({ passed: true, origin, results, limitations: 'Synthetic API interception, service workers blocked. No physical iPhone/native-picker/share-sheet acceptance or new model qualification.' }, null, 2) + '\n');
console.log(JSON.stringify({ passed: true, browsers: results.length, native_model_calls: 0, live_api_mutations: 0 }));
