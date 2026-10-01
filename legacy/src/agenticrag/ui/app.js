/* Chat, public search, immutable page snapshots. */
const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const state = {
  bootstrap: null,
  projects: [],
  project: null,
  chatId: null,
  chats: [],
  busy: false,
  runId: null,
  image: null,
  runtime: null,
  models: [],
  approval: null,
  view: 'chat',
  epoch: 0
};
const node = (tag, cls, text) => {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (text !== undefined) n.textContent = text;
  return n;
};
const button = (text, handler, cls = '') => {
  const n = node('button', cls, text);
  n.type = 'button';
  n.addEventListener('click', () => Promise.resolve(handler()).catch(error => toast(error.message)));
  return n;
};
async function api(path, payload, method = 'POST') {
  const response = await fetch(path, payload === undefined ? {
    cache: 'no-store'
  } : {
    method,
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || result.message || `Request failed (${response.status})`);
  return result;
}

function toast(text) {
  $('#toast').textContent = text;
  $('#toast').hidden = false;
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => $('#toast').hidden = true, 7000);
}

function context() {
  return {
    collection: state.project.collection,
    scopes: state.project.scopes
  };
}

function sourceQuery() {
  const q = new URLSearchParams();
  for (const s of state.project.scopes) q.append('scope', s);
  return q;
}

function nav(open) {
  $('#sidebar').inert = matchMedia('(max-width:760px)').matches && !open;
  document.body.classList.toggle('nav-open', open);
  $('#sidebar-scrim').hidden = !open;
  $('#open-nav').setAttribute('aria-expanded', String(open));
  if (open) $('#close-nav').focus();
}

function view(name) {
  state.view = name;
  $$('.view').forEach(n => n.hidden = n.id !== `${name}-view`);
  $$('[data-view]').forEach(n => n.classList.toggle('active', n.dataset.view === name));
  nav(false);
  if (name === 'sources') loadSources().catch(e => toast(e.message));
  if (name === 'models') renderModels();
  if (name === 'settings') loadNotes().catch(e => toast(e.message));
}

function busy(value) {
  state.busy = value;
  for (const id of ['send', 'web-mode', 'attach-image', 'project-select', 'new-project', 'new-chat', 'new-chat-top', 'test-model', 'provider-form', 'scan-models']) {
    const n = $('#' + id);
    if (n instanceof HTMLFormElement) $$('input,select,button', n).forEach(e => e.disabled = value);
    else n.disabled = value;
  }
  $('#question').disabled = value;
  $('#stop').disabled = value && !state.runId;
  $('#stop').hidden = !value;
  $('#send').hidden = value;
  renderHistory();
  renderModels();
}

function modelName(id) {
  return (id || 'Select model').replace(/:workbench-/g, ' · ').replace(/-instruct.*$/, '').replace(/-q4_K_M$/, '').replace(/qwen3:30b-a3b.*/, 'Qwen3 30B A3B').replace('gemma4:12b', 'Gemma 4 12B').replace('gpt-oss:20b', 'GPT-OSS 20B');
}

function updateModel() {
  const p = state.bootstrap.providers.chat;
  $('#model-label').textContent = modelName(p.model);
  const loaded = state.runtime?.chat?.loaded;
  $('#model-status').classList.toggle('loaded', loaded === true);
  $('#model-shortcut').title = `${p.model||'No model selected'} · ${loaded===true?'loaded':loaded===false?'not loaded; loads on first question':'memory state unknown'}`;
  $('#connection-status').textContent = state.runtime?.chat?.error || (state.runtime?.chat?.reachable ? `${p.runtime} connected · ${loaded?'model loaded':'model will load on demand'}` : 'Check the connection before chatting.');
}

function webLabels() {
  const mode = state.project.web_mode;
  $('#web-mode').value = mode;
  $('#web-state').textContent = {
    off: 'Off',
    ask: 'Ask',
    on: 'On'
  } [mode];
  $('#web-control').title = `Web ${mode} · ${state.bootstrap.web_search_provider}`;
  $('#composer-note').textContent = mode === 'off' ? 'Chat with your selected model. Web is off.' : mode === 'ask' ? 'Web Ask requests permission before sending a search query.' : `Web On · Searches with ${state.bootstrap.web_search_provider}`;
  $('#retention').value = state.project.web_retention;
}
async function projects() {
  state.projects = (await api('/api/v1/projects')).projects;
  const select = $('#project-select');
  select.replaceChildren(...state.projects.map(p => {
    const n = node('option', '', p.name);
    n.value = p.id;
    return n;
  }));
}
async function selectProject(id) {
  if (state.busy) return;
  state.epoch++;
  state.project = state.projects.find(p => p.id === id) || state.projects[0];
  $('#project-select').value = state.project.id;
  $('#project-title').textContent = state.project.name;
  localStorage.setItem('agenticrag.projectId', state.project.id);
  webLabels();
  newChat();
  await refreshChats();
  if (state.view === 'sources') await loadSources();
  if (state.view === 'settings') await loadNotes();
}
async function refreshChats() {
  const q = new URLSearchParams({
    collection: state.project.collection
  });
  if ($('#chat-filter').value) q.set('q', $('#chat-filter').value);
  state.chats = (await api('/api/v1/chats?' + q)).chats;
  renderHistory();
}

function renderHistory() {
  if (!state.project) return;
  $('#history').replaceChildren(...state.chats.map(chat => {
    const row = node('div', 'history-row' + (chat.id === state.chatId ? ' current' : ''));
    const open = button((chat.pinned ? '• ' : '') + chat.title, () => loadChat(chat.id));
    open.title = chat.title;
    open.disabled = state.busy;
    const more = button('⋯', () => chatActions(chat), 'history-menu');
    more.disabled = state.busy;
    more.setAttribute('aria-label', 'Actions for ' + chat.title);
    row.append(open, more);
    return row;
  }));
}

function edit(title, label, value, save) {
  $('#edit-title').textContent = title;
  $('#edit-label').textContent = label;
  $('#edit-value').value = value;
  $('#edit-value').maxLength = /note/i.test(title) ? 1000 : 100;
  $('#edit-dialog').showModal();
  $('#edit-value').focus();
  $('#edit-form').onsubmit = async e => {
    e.preventDefault();
    const input = $('#edit-value').value.trim();
    if (!input) return;
    try {
      await save(input);
      $('#edit-dialog').close();
    } catch (error) {
      toast(error.message);
    }
  };
}

function chatActions(chat) {
  const dialog = $('#source-dialog');
  $('#source-title').textContent = chat.title;
  $('#source-meta').textContent = 'Conversation actions';
  $('#source-text').replaceChildren();
  $('#source-actions').replaceChildren(button('Rename', () => {
    dialog.close();
    edit('Rename chat', 'Title', chat.title, async title => {
      await api('/api/v1/chats/' + chat.id, {
        action: 'rename',
        title
      }, 'PUT');
      await refreshChats();
      if (state.chatId === chat.id) $('#chat-title').textContent = title;
    });
  }), button(chat.pinned ? 'Unpin' : 'Pin', async () => {
    await api('/api/v1/chats/' + chat.id, {
      action: 'pin',
      pinned: !chat.pinned
    }, 'PUT');
    dialog.close();
    await refreshChats();
  }), button('Export', async () => {
    const data = await api('/api/v1/chats/' + chat.id);
    const text = data.messages.map(m => `## ${m.role}\n\n${m.content}`).join('\n\n');
    const link = node('a');
    link.href = URL.createObjectURL(new Blob([text], {
      type: 'text/markdown'
    }));
    link.download = chat.title.replace(/[^a-z0-9 -]/gi, '').slice(0, 80) + '.md';
    link.click();
    setTimeout(() => URL.revokeObjectURL(link.href), 1000);
  }), button('Delete', async () => {
    if (!confirm('Delete this saved conversation?')) return;
    await api('/api/v1/chats/' + chat.id, {}, 'DELETE');
    dialog.close();
    if (state.chatId === chat.id) newChat();
    await refreshChats();
  }));
  const move = node('select');
  move.setAttribute('aria-label', 'Move chat to project');
  state.projects.forEach(p => {
    const opt = node('option', '', p.name);
    opt.value = p.id;
    opt.selected = p.collection === chat.collection;
    move.append(opt);
  });
  move.onchange = async () => {
    try {
      await api('/api/v1/chats/' + chat.id, {
        action: 'move',
        project_id: move.value
      }, 'PUT');
      dialog.close();
      if (state.chatId === chat.id) newChat();
      await refreshChats();
    } catch (e) {
      toast(e.message);
    }
  };
  $('#source-actions').append(move);
  dialog.showModal();
}

function newChat() {
  if (state.busy) return;
  state.chatId = null;
  localStorage.removeItem('agenticrag.activeChatId');
  $('#thread').replaceChildren($('#empty-template').content.cloneNode(true));
  $('#chat-title').textContent = 'New chat';
  $('#question').value = '';
  renderHistory();
  view('chat');
}
async function loadChat(id) {
  if (state.busy) return;
  const epoch = ++state.epoch;
  const chat = await api('/api/v1/chats/' + id);
  if (epoch !== state.epoch) return;
  const p = state.projects.find(p => p.collection === chat.collection);
  if (p && p.id !== state.project.id) {
    state.project = p;
    $('#project-select').value = p.id;
    $('#project-title').textContent = p.name;
    webLabels();
  }
  state.chatId = id;
  localStorage.setItem('agenticrag.activeChatId', id);
  localStorage.setItem('agenticrag.projectId', state.project.id);
  $('#chat-title').textContent = chat.title;
  $('#thread').replaceChildren();
  for (const m of chat.messages) {
    if (m.role === 'user') userMessage(m.content);
    else if (m.result) resultMessage(m.result);
    else resultMessage({
      answer: m.content,
      citations: [],
      events: []
    });
  }
  view('chat');
  renderHistory();
  scrollBottom();
}

function userMessage(text) {
  $('#empty')?.remove();
  const item = node('article', 'message user');
  item.append(node('div', 'user-text', text));
  $('#thread').append(item);
  return item;
}

function answerShell() {
  const item = node('article', 'message assistant');
  item.append(node('div', 'meta', 'Working…'), node('div', 'answer'));
  $('#thread').append(item);
  return item;
}

function markdown(container, text, citations = []) {
  container.innerHTML = DOMPurify.sanitize(marked.parse(text || ''), {
    FORBID_TAGS: ['style', 'input', 'form', 'iframe'],
    FORBID_ATTR: ['style']
  });
  $$('a', container).forEach(a => {
    a.target = '_blank';
    a.rel = 'noopener noreferrer';
  });
  $$('table', container).forEach(table => {
    const wrap = node('div', 'table-wrap');
    table.replaceWith(wrap);
    wrap.append(table);
  });
  if (!citations.length) return;
  const walker = document.createTreeWalker(container, NodeFilter.SHOW_TEXT);
  const leaves = [];
  while (walker.nextNode())
    if (!walker.currentNode.parentElement.closest('pre,code,a,button')) leaves.push(walker.currentNode);
  for (const leaf of leaves) {
    const text = leaf.textContent;
    const matches = [...text.matchAll(/\[(\d+)\]/g)];
    if (!matches.length) continue;
    const fragment = document.createDocumentFragment();
    let pos = 0;
    for (const m of matches) {
      fragment.append(document.createTextNode(text.slice(pos, m.index)));
      const c = citations[Number(m[1]) - 1];
      if (c) {
        const b = button(m[1], () => openSource(c.source_version_id, c), 'cite');
        b.setAttribute('aria-label', `Open source ${m[1]}`);
        fragment.append(b);
      } else fragment.append(document.createTextNode(m[0]));
      pos = m.index + m[0].length;
    }
    fragment.append(document.createTextNode(text.slice(pos)));
    leaf.replaceWith(fragment);
  }
}

function eventLabel(event) {
  return {
    web_search_completed: 'Searched the web',
    web_page_read: 'Read and saved page',
    web_page_failed: 'Page unavailable',
    generation_started: 'Writing answer',
    generation_completed: 'Answer ready',
    web_approval_requested: 'Web permission requested',
    web_approval_resolved: 'Web permission resolved',
    abstained: 'No readable evidence'
  } [event.kind] || event.kind.replaceAll('_', ' ');
}

function trace(item, events) {
  let details = $('.trace', item);
  if (!details) {
    details = node('details', 'trace');
    details.append(node('summary', '', 'Search details'));
    item.append(details);
  }
  const list = node('ol');
  for (const event of events) {
    const d = event.detail || {};
    const row = node('li', event.kind === 'web_page_failed' ? 'failed' : '', `${eventLabel(event)}${d.reason?' · '+d.reason:''}${d.url?' · '+d.url:''}${d.query?' · '+d.query:''}`);
    list.append(row);
  }
  details.replaceChildren(node('summary', '', 'Search details'), list);
}

function resultMessage(result, item = answerShell()) {
  const name = result.provider?.split(':').slice(1).join(':').split('@')[0];
  $('.meta', item).textContent = `${result.workflow==='web_chat'?'Web':'Chat'}${name?' · '+modelName(name):''}${result.elapsed_ms?' · '+(result.elapsed_ms/1000).toFixed(1)+' s':''}${result.incomplete?' · incomplete':result.abstained?' · no supported answer':''}`;
  markdown($('.answer', item), result.answer, result.citations || []);
  $$('.source-chips,.message-actions,.trace', item).forEach(n => n.remove());
  if (result.citations?.length) {
    const sources = node('div', 'source-chips');
    result.citations.forEach((c, i) => {
      let label = c.logical_path;
      try {
        label = new URL(label).hostname;
      } catch {}
      sources.append(button(`${i+1} · ${label}`, () => openSource(c.source_version_id, c)));
    });
    item.append(sources);
  }
  const actions = node('div', 'message-actions');
  actions.append(button('Copy response', async () => {
    await navigator.clipboard.writeText(result.answer);
    toast('Response copied.');
  }));
  actions.append(button('Save note', () => edit('Save a project note', 'Note (up to 1,000 characters)', result.answer.slice(0, 1000), async content => {
    await api(`/api/v1/projects/${state.project.id}/notes`, {
      content,
      source_chat_id: state.chatId
    });
    toast('Note saved.');
  })));
  item.append(actions);
  if (result.events?.length) trace(item, result.events);
  return item;
}

function scrollBottom() {
  const n = $('#thread');
  n.scrollTop = n.scrollHeight;
}

function nearBottom() {
  const n = $('#thread');
  return n.scrollHeight - n.scrollTop - n.clientHeight < 100;
}

function showApproval(event) {
  if (state.approval === event.detail.run_id) return;
  state.approval = event.detail.run_id;
  $('#approval-query').textContent = event.detail.query;
  $('#approval-dialog').showModal();
  $('#approve-web').focus();
}
async function approve(allow) {
  if (!state.approval) return;
  const id = state.approval;
  const data = await api(`/api/v1/runs/${id}/web-approval`, {
    allow
  });
  if (!data.accepted) throw new Error('This web permission request is no longer pending.');
  state.approval = null;
  $('#approval-dialog').close();
}
async function watch(id, item) {
  let tokenText = '',
    seen = 0;
  const started = Date.now();
  for (;;) {
    const r = await api('/api/v1/runs/' + id);
    const follow = nearBottom();
    const events = r.events.filter(x => x.type === 'event').map(x => x.event);
    for (const e of events.slice(seen))
      if (e.kind === 'web_approval_requested') showApproval(e);
    seen = events.length;
    if (r.streamed_text !== tokenText) {
      tokenText = r.streamed_text;
      markdown($('.answer', item), tokenText);
    }
    const phase = events.at(-1);
    $('.meta', item).textContent = r.status === 'queued' ? 'Waiting for the model…' : `${phase?eventLabel(phase):'Working…'} · ${Math.round((Date.now()-started)/1000)} s`;
    if (events.length) trace(item, events);
    if (follow) scrollBottom();
    if (['completed', 'failed', 'stopped', 'interrupted'].includes(r.status)) {
      if (state.approval) {
        state.approval = null;
        $('#approval-dialog').close();
      }
      if (r.result) resultMessage(r.result, item);
      else {
        $('.meta', item).textContent = r.status === 'stopped' ? 'Stopped' : 'Request failed';
        if (!tokenText) $('.answer', item).textContent = r.error || 'The request was interrupted. Try again.';
        else $('.answer', item).append(node('p', 'muted', r.error || 'Answer interrupted.'));
      }
      break;
    }
    await new Promise(resolve => setTimeout(resolve, 300));
  }
}
async function sendQuestion(question) {
  if (state.busy || !question.trim()) return;
  if (!state.bootstrap.providers.chat?.model) {
    view('models');
    toast('Select a chat model first.');
    return;
  }
  busy(true);
  view('chat');
  let item;
  try {
    if (!state.chatId) {
      const chat = await api('/api/v1/chats', context());
      state.chatId = chat.id;
      localStorage.setItem('agenticrag.activeChatId', chat.id);
    }
    const image = state.image;
    userMessage(question + (image ? '\n[Attached image: ' + image.name + ']' : ''));
    item = answerShell();
    $('#chat-title').textContent = question.slice(0, 80);
    $('#question').value = '';
    clearImage();
    scrollBottom();
    state.runId = crypto.randomUUID().replaceAll('-', '');
    localStorage.setItem('agenticrag.activeRun', JSON.stringify({
      run_id: state.runId,
      chat_id: state.chatId,
      project_id: state.project.id
    }));
    await api('/api/v1/runs', {
      ...context(),
      run_id: state.runId,
      chat_id: state.chatId,
      workflow: 'chat',
      question,
      allow_web: state.project.web_mode === 'on',
      ...(image ? {
        image: {
          filename: image.name,
          mime_type: image.data_url.split(';')[0].slice(5),
          data_base64: image.data_url.split(',')[1]
        }
      } : {})
    });
    $('#stop').disabled = false;
    await watch(state.runId, item);
  } catch (error) {
    if (item) {
      $('.meta', item).textContent = 'Request failed';
      $('.answer', item).textContent = error.message;
    } else toast(error.message);
  } finally {
    busy(false);
    state.runId = null;
    localStorage.removeItem('agenticrag.activeRun');
    await refreshChats();
    refreshStatus().catch(() => {});
  }
}
async function resume() {
  let saved;
  try {
    saved = JSON.parse(localStorage.getItem('agenticrag.activeRun') || 'null');
  } catch {
    return;
  }
  if (!saved) return;
  try {
    const run = await api('/api/v1/runs/' + saved.run_id);
    if (!['running', 'queued'].includes(run.status)) {
      localStorage.removeItem('agenticrag.activeRun');
      if (run.status === 'completed' && run.chat_id === state.chatId) await loadChat(run.chat_id);
      return;
    }
    if (run.workflow !== 'chat') {
      toast('An earlier research request is still running. Its saved history remains available.');
      return;
    }
    await loadChat(run.chat_id);
    busy(true);
    state.runId = saved.run_id;
    userMessage(run.question);
    const item = answerShell();
    $('#stop').disabled = false;
    await watch(state.runId, item);
  } catch (error) {
    toast(error.message);
  } finally {
    busy(false);
    state.runId = null;
    localStorage.removeItem('agenticrag.activeRun');
    await refreshChats();
  }
}

function clearImage() {
  state.image = null;
  $('#attachment').hidden = true;
  $('#attachment').replaceChildren();
  $('#image-input').value = '';
}
async function attachImage(file) {
  if (!file) return;
  if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type) || file.size > 8 * 1024 * 1024) throw new Error('Choose a JPEG, PNG or WebP image under 8 MB.');
  const data_url = await readFile(file);
  state.image = {
    name: file.name,
    data_url
  };
  $('#attachment').hidden = false;
  $('#attachment').replaceChildren(document.createTextNode(file.name), button('Remove', clearImage));
}

function readFile(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(new Error('File could not be read.'));
    reader.readAsDataURL(file);
  });
}
async function loadSources() {
  const q = sourceQuery();
  q.set('collection', state.project.collection);
  const sources = (await api('/api/v1/sources?' + q)).sources;
  $('#source-list').replaceChildren(...sources.map(s => {
    const row = node('div', 'source-row');
    const info = node('div', 'source-info');
    info.append(node('strong', '', s.title || s.logical_path), node('small', '', s.logical_path));
    row.append(info, button('Open', () => openSource(s.id)));
    return row;
  }));
  if (!sources.length) $('#source-list').append(node('p', 'muted', 'No saved sources yet. Open a web citation and choose Save to library, or add a file.'));
}
async function openSource(id, citation) {
  const source = await api('/api/v1/sources/' + encodeURIComponent(id) + '?' + sourceQuery());
  $('#source-title').textContent = source.web_page?.title || source.title || source.logical_path;
  $('#source-meta').textContent = 'Immutable source snapshot · ' + source.created_at;
  if (citation && Number.isInteger(citation.start_char) && Number.isInteger(citation.end_char)) {
    const supplied = citation.end_char - citation.start_char;
    $('#source-meta').textContent += ` · Model received ${supplied.toLocaleString()} of ${(source.text || '').length.toLocaleString()} characters` +
      (supplied === (source.text || '').length ? ' (complete extracted text)' : ' (partial excerpt)');
  }
  const actions = $('#source-actions');
  actions.replaceChildren();
  if (/^https:\/\//.test(source.logical_path)) {
    const link = node('a', 'button', 'Open original page');
    link.href = source.logical_path;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    actions.append(link);
  }
  if (source.web_page) {
    const save = button(source.web_page.saved_library_version_id ? 'Saved to library' : 'Save to library', async () => {
      save.disabled = true;
      try {
        await api('/api/v1/web-sources/' + id + '/save', {
          project_id: state.project.id
        });
        save.textContent = 'Saved to library';
        toast('Page saved to your library.');
      } catch (e) {
        save.disabled = false;
        throw e;
      }
    });
    save.disabled = !!source.web_page.saved_library_version_id;
    actions.append(save);
  }
  const container = $('#source-text');
  container.replaceChildren();
  const text = source.text || '';
  if (citation && Number.isInteger(citation.start_char) && Number.isInteger(citation.end_char)) {
    container.append(node('span', 'passage-label', 'Highlighted text is exactly the excerpt supplied to the model for this answer.'));
    container.append(document.createTextNode(text.slice(0, citation.start_char)), node('mark', '', text.slice(citation.start_char, citation.end_char)), document.createTextNode(text.slice(citation.end_char)));
  } else container.textContent = text;
  $('#source-dialog').showModal();
  if (citation) $('mark', container)?.scrollIntoView({
    block: 'center'
  });
}

function providerPayload(values) {
  return {
    role: 'chat',
    runtime: values.runtime,
    base_url: values.base_url,
    model: values.model,
    structured_output_mode: 'prompt',
    provider_kind: values.runtime === 'openai' ? 'openai' : 'local',
    ...(values.api_key ? {
      api_key: values.api_key
    } : {})
  };
}

function fillProvider() {
  const p = state.bootstrap.providers.chat;
  const form = $('#provider-form');
  for (const key of ['runtime', 'base_url', 'model'])
    if (p[key]) form.elements[key].value = p[key];
  form.elements.api_key.value = '';
}
async function refreshStatus() {
  state.runtime = await api('/api/v1/runtime-status?fresh=1');
  updateModel();
  renderModels();
}
async function scanModels() {
  const config = state.bootstrap.providers.chat;
  if (!config.model) return;
  const data = await api('/api/v1/probe', {
    role: 'chat'
  });
  state.models = data.models.filter(m => !/(embed|embedding)/i.test(m));
  await refreshStatus();
}

function renderModels() {
  if (!state.bootstrap) return;
  const selected = state.bootstrap.providers.chat?.model;
  $('#model-list').replaceChildren(...(state.models.length ? state.models : selected ? [selected] : []).map(model => {
    const row = node('div', 'model-row' + (model === selected ? ' selected' : ''));
    const info = node('div', 'model-info');
    info.append(node('strong', '', modelName(model)), node('small', '', model));
    if (model === selected) info.append(node('small', '', state.runtime?.chat?.loaded === true ? ' · loaded' : state.runtime?.chat?.loaded === false ? ' · not loaded; loads on request' : ' · memory state unknown'));
    const use = button(model === selected ? 'Selected' : 'Use', async () => {
      await api('/api/v1/configure', providerPayload({
        ...state.bootstrap.providers.chat,
        model
      }));
      state.bootstrap = await api('/api/v1/bootstrap');
      fillProvider();
      await refreshStatus();
      toast('Chat model selected.');
    });
    use.disabled = state.busy || model === selected;
    row.append(info, use);
    return row;
  }));
}
async function loadNotes() {
  const notes = (await api(`/api/v1/projects/${state.project.id}/notes`)).notes;
  $('#notes').replaceChildren(...notes.map(n => {
    const row = node('div', 'card');
    row.append(node('p', '', n.content));
    row.append(button('Edit', () => edit('Edit note', 'Note', n.content, async content => {
      await api('/api/v1/project-notes/' + n.id, {
        content
      }, 'PUT');
      await loadNotes();
    })), button('Delete', async () => {
      await api('/api/v1/project-notes/' + n.id, {}, 'DELETE');
      await loadNotes();
    }));
    return row;
  }));
}

function appearance() {
  const a = window.ragAppearance;
  for (const [id, key] of [
      ['theme', 'theme'],
      ['reading-font', 'fontRead'],
      ['text-size', 'textSize'], ['accent', 'accent'], ['ui-font', 'fontUi'], ['contrast', 'contrast'], ['motion', 'motion']
    ]) {
    $('#' + id).value = a.settings[key];
    $('#' + id).onchange = e => {
      a.settings[key] = e.target.value;
      localStorage.setItem('agenticrag.appearance', JSON.stringify(a.settings));
      a.apply();
    };
  }
  $('#theme-toggle').onclick = () => {
    a.settings.theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    localStorage.setItem('agenticrag.appearance', JSON.stringify(a.settings));
    a.apply();
    $('#theme').value = a.settings.theme;
  };
}

function updateViewport() {
  const viewport = window.visualViewport;
  if (!viewport || viewport.scale === 1) {
    document.documentElement.style.setProperty('--app-height', `${viewport?.height || innerHeight}px`);
  }
}

function bind() {
  updateViewport();
  window.visualViewport?.addEventListener('resize', updateViewport);
  window.addEventListener('resize', updateViewport);
  const template = node('template');
  template.id = 'empty-template';
  template.content.append($('#empty').cloneNode(true));
  document.body.append(template);
  $('#open-nav').onclick = () => nav(true);
  $('#close-nav').onclick = () => nav(false);
  $('#sidebar-scrim').onclick = () => nav(false);
  $$('[data-view]').forEach(b => b.onclick = () => view(b.dataset.view));
  $('#new-chat').onclick = newChat;
  $('#new-chat-top').onclick = newChat;
  $('#project-select').onchange = e => selectProject(e.target.value).catch(e => toast(e.message));
  $('#new-project').onclick = () => edit('New project', 'Name', '', async name => {
    const p = await api('/api/v1/projects', {
      name
    });
    await projects();
    await selectProject(p.id);
  });
  $('#chat-filter').oninput = () => {
    clearTimeout(bind.searchTimer);
    bind.searchTimer = setTimeout(() => refreshChats().catch(e => toast(e.message)), 250);
  };
  $('#composer').onsubmit = e => {
    e.preventDefault();
    sendQuestion($('#question').value);
  };
  $('#question').onkeydown = e => {
    if (e.key === 'Enter' && !e.shiftKey && !e.isComposing && !matchMedia('(pointer:coarse)').matches) {
      e.preventDefault();
      sendQuestion($('#question').value);
    }
  };
  $('#thread').onclick = e => {
    const b = e.target.closest('[data-prompt]');
    if (b) {
      $('#question').value = b.dataset.prompt;
      $('#question').focus();
    }
  };
  $('#web-mode').onchange = async e => {
    try {
      state.project = await api(`/api/v1/projects/${state.project.id}/settings`, {
        web_mode: e.target.value
      }, 'PUT');
      webLabels();
    } catch (error) {
      webLabels();
      toast(error.message);
    }
  };
  $('#retention').onchange = async e => {
    try {
      state.project = await api(`/api/v1/projects/${state.project.id}/settings`, {
        web_retention: e.target.value
      }, 'PUT');
      webLabels();
    } catch (error) {
      toast(error.message);
    }
  };
  $('#stop').onclick = () => api(`/api/v1/runs/${state.runId}/cancel`, {}).catch(e => toast(e.message));
  $('#approve-web').onclick = () => approve(true).catch(e => toast(e.message));
  $('#decline-web').onclick = () => approve(false).catch(e => toast(e.message));
  $('#approval-dialog').addEventListener('cancel', e => {
    e.preventDefault();
    approve(false).catch(e => toast(e.message));
  });
  $$('.close-dialog').forEach(b => b.onclick = () => b.closest('dialog').close());
  $('#model-shortcut').onclick = () => {
    view('models');
    scanModels().catch(e => toast(e.message));
  };
  $('#scan-models').onclick = () => scanModels().catch(e => toast(e.message));
  $('#test-model').onclick = async () => {
    const b = $('#test-model');
    b.disabled = true;
    try {
      const r = await api('/api/v1/check-model', {});
      toast(`Completion received in ${(r.latency_ms/1000).toFixed(1)} s: ${r.answer}`);
      await refreshStatus();
    } catch (e) {
      toast(e.message);
    } finally {
      b.disabled = false;
    }
  };
  $('#provider-form').onsubmit = async e => {
    e.preventDefault();
    if (state.busy) return;
    try {
      const values = Object.fromEntries(new FormData(e.target));
      await api('/api/v1/configure', providerPayload(values));
      state.bootstrap = await api('/api/v1/bootstrap');
      fillProvider();
      await scanModels();
      toast('Connection saved.');
    } catch (error) {
      toast(error.message);
    }
  };
  $('#provider-form').elements.runtime.onchange = e => {
    const profile = state.bootstrap.runtimes.find(p => p.id === e.target.value);
    $('#provider-form').elements.base_url.value = profile?.chat_base_url || (e.target.value === 'openai' ? 'https://api.openai.com/v1' : 'http://127.0.0.1:8080/v1');
  };
  $('#refresh-sources').onclick = () => loadSources().catch(e => toast(e.message));
  $('#source-upload').onchange = async e => {
    const file = e.target.files[0];
    if (!file) return;
    try {
      const data = await readFile(file);
      await api('/api/v1/ingest', {
        ...context(),
        filename: file.name,
        content_base64: data.split(',')[1]
      });
      await loadSources();
      toast('Source saved.');
    } catch (error) {
      toast(error.message);
    } finally {
      e.target.value = '';
    }
  };
  $('#attach-image').onclick = () => $('#image-input').click();
  $('#image-input').onchange = e => attachImage(e.target.files[0]).catch(e => toast(e.message));
  $('#dictate').onclick = () => {
    const Speech = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Speech) {
      toast('Use the microphone on your phone’s keyboard to dictate.');
      $('#question').focus();
      return;
    }
    const recognition = new Speech();
    recognition.lang = navigator.language;
    recognition.onresult = e => {
      $('#question').value += $('#question').value ? ' ' + e.results[0][0].transcript : e.results[0][0].transcript;
    };
    recognition.onerror = () => toast('Dictation could not start. Check microphone permission.');
    recognition.start();
  };
  window.addEventListener('resize', () => {
    $('#sidebar').inert = matchMedia('(max-width:760px)').matches && !document.body.classList.contains('nav-open');
  });
  $('#note-form').onsubmit = async e => {
    e.preventDefault();
    try {
      await api(`/api/v1/projects/${state.project.id}/notes`, {
        content: $('#note-text').value
      });
      $('#note-text').value = '';
      await loadNotes();
    } catch (error) {
      toast(error.message);
    }
  };
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') nav(false);
  });
  appearance();
}
async function initialize() {
  const savedChat = localStorage.getItem('agenticrag.activeChatId');
  bind();
  try {
    state.bootstrap = await api('/api/v1/bootstrap');
    await projects();
    await selectProject(localStorage.getItem('agenticrag.projectId') || 'default');
    fillProvider();
    updateModel();
    $('#about').textContent = `Chat & Web ${state.bootstrap.version} · ${state.bootstrap.web_search_provider}`;
    if (savedChat) await loadChat(savedChat);
    await resume();
    refreshStatus().catch(e => toast(e.message));
    scanModels().catch(() => {});
  } catch (error) {
    toast(error.message + ' Refresh to reconnect.');
  }
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js').then(reg => {
      if (reg.waiting) reg.waiting.postMessage({
        type: 'activate-update'
      });
      reg.addEventListener('updatefound', () => {
        const worker = reg.installing;
        worker?.addEventListener('statechange', () => {
          if (worker.state === 'installed') worker.postMessage({
            type: 'activate-update'
          });
        });
      });
    }).catch(() => {});
  }
}
initialize();
