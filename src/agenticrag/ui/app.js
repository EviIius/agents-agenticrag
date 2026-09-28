"use strict";

const state = {
  bootstrap: null,
  workflow: "agent",
  selectedSkills: new Set(),
  allowWeb: false,
  capabilityTab: "tools",
  selectedFile: null,
  chats: [],
  projects: [],
  activeProjectId: null,
  chatSearch: "",
  chatAttachment: null,
  activeChatId: null,
  activeTurns: 0,
  sourceCount: null,
  sourceContextKey: null,
  sourceRefreshTimer: null,
  installedChatModels: [],
  modelsDiscovered: false,
  evaluation: null,
  memoryNotes: [],
  memoryLoaded: false,
  memoryEditingId: null,
  recognition: null,
  voiceListening: false,
  runId: null,
  runController: null,
  stopRequested: false,
  followRunOutput: true,
  inspectorInvoker: null,
  runtimeStatus: null,
  sources: [],
  sourceFilter: "all",
  sourceQuery: "",
};

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const phoneLayout = () => window.matchMedia("(max-width: 600px)").matches;
const chatScroller = () => $("#conversation");
const screenScroller = () => {
  const view = $("[data-view-panel].is-active")?.dataset.viewPanel;
  if (view === "chat") return chatScroller();
  return { models: $(".model-workspace"), corpus: $(".corpus-layout"), capabilities: $(".capability-layout") }[view];
};

function prepareDesignShell() {
  $(".sidebar-brand-slot").append($(".topbar .brand"));
  $("#sidebar-new-chat-slot").append($("#new-chat-button"));
  $("#new-chat-button").append(el("kbd", "", "⌘N"));
  $("#ask-form").append($("#workflow-options"));
  $$("#workflow-options [data-workflow]").forEach((button) => {
    button.setAttribute("role", "menuitemradio");
    button.setAttribute("aria-checked", String(button.classList.contains("is-active")));
  });
  $("#workflow-options").addEventListener("keydown", (event) => {
    const items = $$("#workflow-options [data-workflow]").filter((button) => !button.disabled);
    if (!items.length) return;
    const index = items.indexOf(document.activeElement);
    let next = index;
    if (event.key === "ArrowDown") next = (index + 1) % items.length;
    else if (event.key === "ArrowUp") next = (index - 1 + items.length) % items.length;
    else if (event.key === "Home") next = 0;
    else if (event.key === "End") next = items.length - 1;
    else if (event.key === "Escape") { toggleModeMenu(false); $("#mode-pill").focus(); return; }
    else return;
    event.preventDefault();
    items[next]?.focus();
  });
  $("#composer-caption").after($(".starter-prompts"));
  $("#project-settings-content").append($("#knowledge-settings"), $("#refresh-button"));
  $("#knowledge-settings").open = true;
  $("#project-settings-button").addEventListener("click", () => $("#project-settings-dialog").showModal());
  $("#close-project-settings").addEventListener("click", () => $("#project-settings-dialog").close());
  const connectionsDialog = el("dialog", "project-dialog connections-dialog");
  connectionsDialog.id = "connections-dialog";
  const connectionsHead = el("div", "memory-dialog-heading");
  connectionsHead.append(el("h2", "", "Advanced connections"));
  const closeConnections = el("button", "secondary-button", "Done");
  closeConnections.type = "button";
  closeConnections.addEventListener("click", () => connectionsDialog.close());
  connectionsHead.append(closeConnections);
  const advancedConnections = $("#advanced-connections");
  advancedConnections.open = true;
  connectionsDialog.append(connectionsHead, advancedConnections);
  document.body.append(connectionsDialog);
  $("#sidebar-search-toggle").addEventListener("click", () => {
    const search = $("#chat-search");
    search.classList.toggle("is-visible");
    if (search.classList.contains("is-visible")) search.focus();
  });
  $("#mode-pill").addEventListener("click", () => toggleModeMenu($("#workflow-options").hidden));
  $("#chat-context-label").addEventListener("click", () => {
    $("#project-settings-dialog").showModal();
    $("#collection-input").focus();
  });
  $("#mobile-menu-toggle").addEventListener("click", () => setSidebarOpen(!$(".sidebar").classList.contains("is-open")));
  $("#sidebar-scrim").addEventListener("click", () => setSidebarOpen(false));
  $("#mobile-new-chat").addEventListener("click", () => { clearChat(); setView("chat"); });
  $(".sidebar-brand-slot .brand").addEventListener("click", () => setView("chat"));
  setSidebarOpen(false);
  updateDesignLabels();
}

function setSidebarOpen(open) {
  $(".sidebar").classList.toggle("is-open", open);
  $(".sidebar").inert = !open && window.matchMedia("(max-width: 1023px)").matches;
  $("#sidebar-scrim").hidden = !open;
  $("#mobile-menu-toggle").setAttribute("aria-expanded", String(open));
}

function toggleModeMenu(open) {
  const menu = $("#workflow-options");
  if (open) {
    $("#composer-add-menu").hidden = true;
    $("#chat-attachment-control").setAttribute("aria-expanded", "false");
  }
  menu.hidden = !open;
  $("#mode-pill").setAttribute("aria-expanded", String(open));
  if (open) menu.querySelector(".is-active")?.focus();
}

function updateDesignLabels() {
  const project = state.projects.find((item) => item.id === state.activeProjectId);
  $("#titlebar-project").textContent = project?.name || $("#mobile-context-summary").textContent || "My library";
  const panel = $("[data-view-panel].is-active")?.dataset.viewPanel || "chat";
  $("#titlebar-title").textContent = panel === "chat" ? (state.activeChatId ? $("#chat-title").textContent : "New chat") : ({ corpus: "Sources", models: "Models", capabilities: "Tools & agents" }[panel] || "Chat");
  $("#mode-pill-label").textContent = ({ direct: "Direct", fixed: "Fixed", agent: "Agentic", supervisor: "Supervisor" })[state.workflow];
  $("#mode-pill > span:first-child").textContent = ({ direct: "○", fixed: "▣", agent: "◇", supervisor: "△" })[state.workflow];
  updateModeMenu();
  $("#composer-caption").textContent = state.workflow === "direct"
    ? (state.allowWeb ? "Web search is on for this question · queries leave this Mac" : "Runs on this Mac · Direct mode doesn't search your sources")
    : `Runs on this Mac · answers cite ${$("#titlebar-project").textContent} · retrieved text is evidence, never instructions`;
  $("#memory-count").hidden = !state.memoryLoaded;
  if (state.memoryLoaded) $("#memory-count").textContent = String(state.memoryNotes.length);
  $(".workspace-identity small").textContent = `${state.sourceCount ?? "—"} sources · ${project?.name || $("#collection-input").value.trim() || "research"}`;
}

function updateModeMenu() {
  const modes = {
    direct: ["○", "Direct", "No sources", "Chat with the model and recent turns."],
    fixed: ["▣", "Fixed", "Cites sources", "Retrieve passages and answer with citations."],
    agent: ["◇", "Agentic", "Cites + reviews", "Plan searches, use tools, then review the answer."],
    supervisor: ["△", "Supervisor", "Usually cites", "Delegate to specialists and synthesize their reports."],
  };
  const names = { direct: "direct", fixed: "fixed_rag", agent: "bounded_agentic_rag", supervisor: "manager_multi_agent" };
  $$("#workflow-options [data-workflow]").forEach((button) => {
    const [glyph, name, tag, description] = modes[button.dataset.workflow];
    const group = state.evaluation?.groups?.find((item) => item.model === state.bootstrap?.providers?.chat?.model && item.workflow === names[button.dataset.workflow]);
    const heading = el("span", "mode-menu-heading");
    heading.append(el("span", "mode-glyph", glyph), el("strong", "", name), el("span", "mode-source-tag", tag));
    if (group?.mean_latency_ms != null) heading.append(el("time", "", `~${(group.mean_latency_ms / 1000).toFixed(1)}s`));
    button.replaceChildren(heading, el("small", "", description));
  });
  let footnote = $(".mode-menu-footnote", $("#workflow-options"));
  if (!footnote) { footnote = el("p", "mode-menu-footnote"); $("#workflow-options").append(footnote); }
  footnote.textContent = "Times reflect measured runs on this Mac, when available.";
}

function updateBackToTop() {
  const button = $("#back-to-top");
  const scroller = screenScroller();
  button.hidden = !scroller || scroller.scrollTop < 400;
  if (!button.hidden && $("#view-chat").classList.contains("is-active")) {
    const workspace = $("#workspace").getBoundingClientRect();
    const composer = $("#ask-form").getBoundingClientRect();
    button.style.bottom = `${Math.max(16, workspace.bottom - composer.top + 12)}px`;
  } else {
    button.style.removeProperty("bottom");
  }
}

function scrollChatToBottom() {
  const scroller = chatScroller();
  scroller.scrollTop = scroller.scrollHeight;
}

function updateMobileViewport() {
  if (!phoneLayout()) {
    document.documentElement.style.removeProperty("--mobile-viewport-height");
    document.documentElement.style.removeProperty("--mobile-viewport-top");
    document.body.classList.remove("is-composing");
    return;
  }
  const viewport = window.visualViewport;
  document.documentElement.style.setProperty(
    "--mobile-viewport-height", `${Math.round(viewport?.height || window.innerHeight)}px`,
  );
  document.documentElement.style.setProperty(
    "--mobile-viewport-top", `${Math.round(viewport?.offsetTop || 0)}px`,
  );
}

function resizeComposer() {
  const input = $("#question-input");
  input.style.height = "auto";
  input.style.height = `${phoneLayout() && !input.value ? 56 : Math.min(input.scrollHeight, phoneLayout() ? 118 : 180)}px`;
  updateBackToTop();
}

function startVoiceDictation() {
  const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!Recognition) {
    toast("Voice dictation is unavailable here. Use your keyboard microphone instead.", true);
    return;
  }
  const recognition = new Recognition();
  recognition.lang = navigator.language || "en-US";
  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.onresult = (event) => {
    const transcript = [...event.results].map((result) => result[0]?.transcript || "").join(" ").trim();
    if (transcript) {
      const input = $("#question-input");
      input.value = [input.value.trim(), transcript].filter(Boolean).join(" ");
      resizeComposer();
      input.focus();
    }
  };
  recognition.onerror = (event) => {
    if (event.error !== "no-speech" && event.error !== "aborted") {
      toast("Voice input stopped. You can use the keyboard microphone instead.", true);
    }
  };
  recognition.onend = () => {
    state.voiceListening = false;
    state.recognition = null;
    $("#dictate-button").textContent = "Dictate";
    $("#dictate-button").classList.remove("is-listening");
  };
  try {
    recognition.start();
    state.recognition = recognition;
    state.voiceListening = true;
    $("#dictate-button").textContent = "Stop listening";
    $("#dictate-button").classList.add("is-listening");
  } catch {
    toast("Voice input could not start. Use your keyboard microphone instead.", true);
  }
}

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function compactText(value, limit = 260) {
  const text = String(value || "").replace(/\s+/g, " ").trim();
  return text.length <= limit ? text : `${text.slice(0, limit - 1).trimEnd()}…`;
}

function conversationTitle(question) {
  const normalized = String(question || "").replace(/\s+/g, " ").trim();
  const firstSentence = normalized.split(/(?<=[.!?])\s+/, 1)[0];
  if (firstSentence.length <= 48) return firstSentence;
  return `${firstSentence.slice(0, 47).replace(/\s+\S*$/, "").replace(/[ ,;:]+$/, "")}…`;
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
  });
  let payload;
  try {
    payload = await response.json();
  } catch {
    throw new Error(`Workbench returned HTTP ${response.status} without JSON`);
  }
  if (!response.ok) throw new Error(payload.error || `Request failed with HTTP ${response.status}`);
  return payload;
}

function post(path, payload) {
  return api(path, { method: "POST", body: JSON.stringify(payload) });
}

async function streamQuestion(payload, onProgress, onReady, onToken, onEvent, onEvidence) {
  const controller = new AbortController();
  state.runController = controller;
  const response = await fetch("/api/v1/ask-stream", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload), signal: controller.signal,
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || `Run failed with HTTP ${response.status}`);
  }
  if (!response.body) throw new Error("This browser cannot read run progress");
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  while (true) {
    const { value, done } = await reader.read();
    buffer += decoder.decode(value || new Uint8Array(), { stream: !done });
    const frames = buffer.split("\n\n");
    buffer = frames.pop() || "";
    for (const frame of frames) {
      const line = frame.split("\n").find((item) => item.startsWith("data: "));
      if (!line) continue;
      const event = JSON.parse(line.slice(6));
      if (event.type === "started") onReady(event);
      if (event.type === "progress") onProgress(event.message);
      if (event.type === "token") onToken(event.text || "");
      if (event.type === "event") onEvent(event.event);
      if (event.type === "evidence") onEvidence(event.items || []);
      if (event.type === "completed") return event.result;
      if (event.type === "stopped") throw new Error("Run stopped");
      if (event.type === "error") throw new Error(event.message || "Run failed");
    }
    if (done) throw new Error("Run ended before an answer arrived");
  }
}

function currentContext() {
  const collection = $("#collection-input").value.trim();
  const scopes = $("#scope-input").value.split(",").map((item) => item.trim()).filter(Boolean);
  if (!collection) throw new Error("Enter a collection name");
  if (!scopes.length) throw new Error("Enter at least one access scope");
  return { collection, scopes };
}

function persistContext() {
  localStorage.setItem("agenticrag.collection", $("#collection-input").value);
  localStorage.setItem("agenticrag.scopes", $("#scope-input").value);
  if (state.activeChatId) {
    clearChat();
    toast("New knowledge settings start a new conversation. Your earlier chat is saved.");
  }
  updateContextLabels();
  updateEmptyState();
  refreshCorpusStatus();
  void refreshChats();
  if (!$("#view-corpus").hidden) void loadSources();
}

function contextInputChanged() {
  updateContextLabels();
  window.clearTimeout(state.sourceRefreshTimer);
  state.sourceRefreshTimer = window.setTimeout(refreshCorpusStatus, 180);
}

function updateContextLabels() {
  const collection = $("#collection-input").value.trim() || "no collection";
  const scopes = $("#scope-input").value.trim() || "no scope";
  const key = JSON.stringify([collection, scopes.split(",").map((item) => item.trim()).filter(Boolean).join(",")]);
  const sourceLabel = state.sourceContextKey === key && state.sourceCount !== null
    ? ` · ${state.sourceCount} source${state.sourceCount === 1 ? "" : "s"}` : "";
  const project = state.projects.find((item) => item.collection === collection && item.scopes.join(", ") === scopes);
  if ((project?.id || null) !== state.activeProjectId) {
    state.activeProjectId = project?.id || null;
    state.memoryLoaded = false;
    state.memoryNotes = [];
  }
  const label = project?.name || (collection === "research" && scopes === "private" ? "My library" : collection);
  $("#chat-context-label").textContent = `${label}${sourceLabel}`;
  $("#mobile-context-summary").textContent = label;
  updateDesignLabels();
}

function setMobileContextOpen(open) {
  $("#mobile-context-fields").hidden = !open;
  $("#mobile-context-toggle").setAttribute("aria-expanded", String(open));
}

function renderCorpusStatus() {
  const notice = $("#corpus-notice");
  notice.hidden = true;
  if (!notice.hidden) {
    $("#corpus-notice-title").textContent = "No sources in this library";
    $("#corpus-notice-detail").textContent = "Grounded modes need documents. Add one in Sources or choose another collection.";
  }
  updateContextLabels();
}

async function refreshCorpusStatus() {
  let context;
  try { context = currentContext(); } catch { return; }
  const key = JSON.stringify([context.collection, context.scopes.join(",")]);
  state.sourceContextKey = key;
  state.sourceCount = null;
  $("#sources-nav-count").hidden = true;
  renderCorpusStatus();
  const query = new URLSearchParams({ collection: context.collection });
  context.scopes.forEach((scope) => query.append("scope", scope));
  try {
    const result = await api(`/api/v1/sources?${query}`);
    if (state.sourceContextKey !== key) return;
    state.sourceCount = result.sources.length;
    $("#sources-nav-count").textContent = String(state.sourceCount);
    $("#sources-nav-count").hidden = false;
    renderCorpusStatus();
    updateEmptyState();
  } catch {
    if (state.sourceContextKey === key) state.sourceCount = null;
  }
}

function updateMemoryStatus() {
  const status = $("#memory-status");
  const turns = state.activeTurns;
  status.textContent = turns
    ? `${turns} turn${turns === 1 ? "" : "s"} in this conversation · saved on this Mac`
    : "Saved on this Mac · earlier turns available to the model";
}

function updateEmptyState() {
  const descriptions = {
    agent: ["Ask your sources.", "Agentic mode searches local documents, checks its work, and cites what it used."],
    fixed: ["Answers with sources.", "Fixed mode finds relevant passages and answers with citations."],
    supervisor: ["Explore a bigger question.", "Supervisor mode asks bounded specialists to investigate and combines their evidence."],
    direct: ["Start with a question.", "Direct mode chats with the local model and remembers this conversation. Switch to a grounded mode to use your sources."],
  };
  const [title, description] = descriptions[state.workflow];
  $("#chat-empty-title").textContent = title;
  $("#chat-empty-description").textContent = state.workflow !== "direct" && state.sourceCount === 0
    ? "Add a source to this library, then ask a question. You can use Direct mode without sources."
    : description;
  const directPrompts = [
    ["Explain a concept", "Explain retrieval-augmented generation in plain language."],
    ["Draft an outline", "Draft a concise outline for a research memo."],
    ["Compare approaches", "Compare fixed RAG and an agentic research workflow."],
  ];
  const sampleLibrary = $("#collection-input").value.trim() === "research" && $("#scope-input").value.trim() === "private";
  const corpusPrompts = sampleLibrary ? [
    ["Make one-pot Alfredo", "According to the one-pot chicken Alfredo source, how do I make it with less cleanup?"],
    ["Keep nachos crisp", "According to the nachos source, why add wet toppings after baking?"],
    ["Compare the four modes", "According to the mode guide, how do Direct, Fixed, Agentic, and Supervisor differ?"],
  ] : [
    ["Summarize key findings", "Summarize the strongest claims in this collection and cite each one."],
    ["Find uncertainty", "What evidence in this collection conflicts or remains uncertain?"],
    ["Compare sources", "Compare the methods described across the available sources."],
  ];
  $$('[data-prompt]').forEach((button, index) => {
    const [label, prompt] = (state.workflow === "direct" ? directPrompts : corpusPrompts)[index];
    button.textContent = label;
    button.dataset.prompt = prompt;
  });
  $("#question-input").placeholder = state.workflow === "direct" ? "Ask the local model…" : state.activeTurns ? "Ask a follow-up…" : `Ask a question about ${$("#titlebar-project").textContent}…`;
  $("#skill-picker-button").hidden = !["agent", "supervisor"].includes(state.workflow);
  $("#web-search-control").hidden = !["direct", "supervisor"].includes(state.workflow);
  $("#chat-context-label").hidden = state.workflow === "direct";
  if (state.workflow === "direct" || state.workflow === "fixed") $("#skill-picker").hidden = true;
  renderCorpusStatus();
}

function renderHistoryList() {
  const list = $("#history-list");
  list.replaceChildren();
  const mobile = $("#mobile-chat-select");
  mobile.replaceChildren();
  const placeholder = el("option", "", "Recent chats");
  placeholder.value = "";
  mobile.append(placeholder);
  if (!state.chats.length) {
    list.append(el("p", "", "Your conversations will appear here."));
    return;
  }
  let lastGroup = "";
  const now = new Date();
  const midnight = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
  state.chats.forEach((chat) => {
    const ageDays = Math.floor((midnight - new Date(chat.updated_at * 1000).getTime()) / 86400000);
    const group = ageDays <= 0 ? "Today" : ageDays === 1 ? "Yesterday" : ageDays < 7 ? "Previous 7 days" : "Earlier";
    if (group !== lastGroup) { list.append(el("div", "history-group", group)); lastGroup = group; }
    const option = el("option", "", chat.title);
    option.value = chat.id;
    mobile.append(option);
    const button = el("button", `history-item${chat.id === state.activeChatId ? " is-active" : ""}`);
    button.type = "button";
    button.title = chat.title;
    button.append(el("span", "history-item-title", chat.title), el("small", "", new Date(chat.updated_at * 1000).toLocaleDateString()));
    button.addEventListener("click", () => { setSidebarOpen(false); void loadChat(chat.id); });
    const row = el("div", `history-row${chat.id === state.activeChatId && state.runId ? " is-running" : ""}`);
    const menu = el("details", "history-menu");
    const toggle = el("summary", "", "⋯");
    toggle.setAttribute("aria-label", `Actions for ${chat.title}`);
    const remove = el("button", "", "Delete chat");
    remove.type = "button";
    remove.addEventListener("click", () => void deleteChat(chat.id));
    menu.append(toggle, remove);
    row.append(button, menu);
    list.append(row);
  });
  mobile.value = state.activeChatId || "";
}

async function refreshChats() {
  const query = new URLSearchParams({ collection: currentContext().collection });
  if (state.chatSearch) query.set("q", state.chatSearch);
  const result = await api(`/api/v1/chats?${query}`);
  state.chats = result.chats;
  renderHistoryList();
}

async function deleteChat(chatId) {
  if (!window.confirm("Delete this conversation and all its messages? This cannot be undone.")) return;
  try {
    await api(`/api/v1/chats/${encodeURIComponent(chatId)}`, { method: "DELETE" });
    if (chatId === state.activeChatId) clearChat();
    await refreshChats();
    toast("Conversation deleted.");
  } catch (error) { toast(error.message, true); }
}

async function refreshProjects() {
  const result = await api("/api/v1/projects");
  state.projects = result.projects;
  for (const selector of [$("#project-select"), $("#mobile-project-select")]) {
    selector.replaceChildren();
    state.projects.forEach((project) => {
      const option = el("option", "", project.name);
      option.value = project.id;
      selector.append(option);
    });
  }
  const context = currentContext();
  const match = state.projects.find((project) => project.collection === context.collection && project.scopes.join(",") === context.scopes.join(","));
  state.activeProjectId = match?.id || null;
  if (match) {
    $("#project-select").value = match.id;
    $("#mobile-project-select").value = match.id;
  }
  updateContextLabels();
}

function renderMemoryNotes() {
  const list = $("#memory-list");
  list.replaceChildren();
  if (!state.memoryNotes.length) {
    list.append(el("p", "", "No saved notes yet. Add one to carry context into future chats."));
    return;
  }
  state.memoryNotes.forEach((note) => {
    const card = el("article", "memory-note");
    card.append(el("p", "", note.content));
    const meta = el("div", "memory-note-meta");
    meta.append(el("span", "", new Date(note.updated_at * 1000).toLocaleDateString()));
    if (note.source_chat_id && note.source_chat_title) {
      const source = el("button", "", `From chat: ${note.source_chat_title}`);
      source.type = "button";
      source.addEventListener("click", () => {
        $("#memory-dialog").close();
        void loadChat(note.source_chat_id);
      });
      meta.append(source);
    } else meta.append(el("span", "", "Added by you"));
    const edit = el("button", "", "Edit");
    edit.type = "button";
    edit.addEventListener("click", () => {
      state.memoryEditingId = note.id;
      $("#memory-content").value = note.content;
      $("#memory-source-chat").value = "";
      $("#save-memory").textContent = "Save changes";
      $("#cancel-memory-edit").hidden = false;
      $("#memory-content").focus();
    });
    const remove = el("button", "", "Delete");
    remove.type = "button";
    remove.addEventListener("click", async () => {
      if (remove.textContent !== "Delete note?") {
        remove.textContent = "Delete note?";
        return;
      }
      try {
        await api(`/api/v1/project-notes/${note.id}`, { method: "DELETE" });
        await loadProjectMemory();
      } catch (error) { toast(error.message, true); }
    });
    meta.append(edit, remove);
    card.append(meta);
    list.append(card);
  });
}

async function loadProjectMemory() {
  if (!state.activeProjectId) return;
  const [{ notes }, { activity }] = await Promise.all([
    api(`/api/v1/projects/${state.activeProjectId}/notes`),
    api(`/api/v1/projects/${state.activeProjectId}/memory-activity`),
  ]);
  state.memoryNotes = notes;
  state.memoryLoaded = true;
  updateDesignLabels();
  renderMemoryNotes();
  const list = $("#memory-activity-list");
  list.replaceChildren();
  activity.slice(0, 10).forEach((item) => {
    list.append(el("span", "", `${item.action} · ${new Date(item.created_at * 1000).toLocaleString()}`));
  });
  if (!activity.length) list.append(el("span", "", "No changes yet."));
}

async function openMemoryDialog({ content = "", sourceChatId = "" } = {}) {
  if (!state.activeProjectId) {
    toast("Choose a project before saving memory.", true);
    return;
  }
  state.memoryEditingId = null;
  $("#memory-content").value = content.slice(0, 1000);
  $("#memory-source-chat").value = sourceChatId;
  $("#save-memory").textContent = "Save note";
  $("#cancel-memory-edit").hidden = true;
  setMobileContextOpen(false);
  $("#memory-dialog").showModal();
  try { await loadProjectMemory(); } catch (error) { toast(error.message, true); }
  if (content) $("#memory-content").focus();
}

async function selectProject(projectId) {
  const project = state.projects.find((item) => item.id === projectId);
  if (!project) throw new Error("Project was not found");
  if (!state.activeChatId) clearChat();
  state.activeProjectId = project.id;
  state.memoryLoaded = false;
  state.memoryNotes = [];
  $("#project-select").value = project.id;
  $("#mobile-project-select").value = project.id;
  $("#collection-input").value = project.collection;
  $("#scope-input").value = project.scopes.join(", ");
  $("#mobile-collection-input").value = project.collection;
  $("#mobile-scope-input").value = project.scopes.join(", ");
  persistContext();
  await refreshChats();
  if (!$("#view-corpus").hidden) await loadSources();
}

async function loadChat(chatId) {
  try {
    const chat = await api(`/api/v1/chats/${encodeURIComponent(chatId)}`);
    resetAttachment();
    $("#question-input").value = "";
    resizeComposer();
    $("#mobile-chat-history").open = false;
    state.activeChatId = chat.id;
    state.activeTurns = Math.floor(chat.messages.length / 2);
    $("#delete-chat-button").disabled = false;
    localStorage.setItem("agenticrag.activeChatId", chat.id);
    $("#chat-title").textContent = chat.title;
    updateDesignLabels();
    $("#collection-input").value = chat.collection;
    $("#scope-input").value = chat.scopes.join(", ");
    $("#mobile-collection-input").value = chat.collection;
    $("#mobile-scope-input").value = chat.scopes.join(", ");
    localStorage.setItem("agenticrag.collection", chat.collection);
    localStorage.setItem("agenticrag.scopes", chat.scopes.join(", "));
    const project = state.projects.find((item) => item.collection === chat.collection);
    if (project) {
      state.activeProjectId = project.id;
      $("#project-select").value = project.id;
      $("#mobile-project-select").value = project.id;
    }
    $$("#conversation .message").forEach((message) => message.remove());
    $("#chat-empty").hidden = chat.messages.length > 0;
    for (const item of chat.messages) {
      if (item.role === "user") appendMessage("user", item.content, item.workflow, false);
      else {
        const node = appendMessage("assistant", "", "saved response", false);
        renderResult({ answer: item.content, ...item.result, evidence: item.result?.evidence || [], events: item.result?.events || [] }, node, true);
      }
    }
    const lastWorkflow = chat.messages.at(-1)?.workflow;
    if (lastWorkflow) $(`[data-workflow="${lastWorkflow}"]`)?.click();
    updateMemoryStatus();
    updateContextLabels();
    updateEmptyState();
    await refreshCorpusStatus();
    renderHistoryList();
    setView("chat");
    scrollChatToBottom();
  } catch (error) {
    toast(error.message, true);
  }
}

function showAttachment(file) {
  state.chatAttachment = file;
  $("#attachment-preview").hidden = !file;
  $("#attachment-label").textContent = file?.name || "";
  $("#attachment-detail").textContent = file
    ? `${formatBytes(file.size)} · ${isImageFile(file) ? "Direct mode · vision model needed" : "Added to Sources when sent"}`
    : "";
  $(".attachment-preview-icon").textContent = file && isImageFile(file) ? "▧" : "▤";
}

function resetAttachment() {
  showAttachment(null);
  $("#chat-document-input").value = "";
  $("#chat-image-input").value = "";
}

function isImageFile(file) {
  return Boolean(file && (file.type.startsWith("image/") || /\.(?:png|jpe?g|webp)$/i.test(file.name)));
}

function imageMimeType(file) {
  if (file.type === "image/png" || file.type === "image/jpeg" || file.type === "image/webp") return file.type;
  if (/\.png$/i.test(file.name)) return "image/png";
  if (/\.webp$/i.test(file.name)) return "image/webp";
  return "image/jpeg";
}

function selectChatAttachment(file, kind) {
  if (!file) return;
  const supported = kind === "image"
    ? /\.(?:png|jpe?g|webp)$/i.test(file.name) || ["image/png", "image/jpeg", "image/webp"].includes(file.type)
    : /\.(?:txt|md|markdown|docx|pdf)$/i.test(file.name);
  if (!supported) {
    resetAttachment();
    toast(kind === "image" ? "Choose a JPEG, PNG, or WebP image." : "Choose a PDF, Word, Markdown, or text document.", true);
    return;
  }
  const limit = kind === "image" ? 8 * 1024 * 1024 : state.bootstrap.ingestion?.limits?.max_file_bytes;
  if (Number.isFinite(limit) && file.size > limit) {
    resetAttachment();
    toast(`Choose a file smaller than ${formatBytes(limit)}.`, true);
    return;
  }
  showAttachment(file);
  if (kind === "image") {
    $(`[data-workflow="direct"]`).click();
    state.allowWeb = false;
    $("#allow-web-input").checked = false;
    syncHostedCapabilities();
    updateDesignLabels();
    if (!$("#question-input").value.trim()) $("#question-input").value = "What is in this image?";
  } else {
    $(`[data-workflow="fixed"]`).click();
    if (!$("#question-input").value.trim()) $("#question-input").value = "Summarize this document and cite it.";
  }
  resizeComposer();
}

function clearChat() {
  state.activeChatId = null;
  state.activeTurns = 0;
  resetAttachment();
  localStorage.removeItem("agenticrag.activeChatId");
  $("#chat-title").textContent = "New conversation";
  $$("#conversation .message").forEach((message) => message.remove());
  $("#chat-empty").hidden = false;
  $("#new-chat-button").disabled = false;
  $("#delete-chat-button").disabled = true;
  closeInspector();
  $("#question-input").value = "";
  resizeComposer();
  $("#mobile-chat-history").open = false;
  updateMemoryStatus();
  renderHistoryList();
  updateDesignLabels();
  updateEmptyState();
  if (!phoneLayout()) $("#question-input").focus();
}

function setView(name) {
  closeInspector();
  setMobileContextOpen(false);
  $("#mobile-chat-history").open = false;
  $$("[data-view-panel]").forEach((panel) => {
    const active = panel.dataset.viewPanel === name;
    panel.hidden = !active;
    panel.classList.toggle("is-active", active);
  });
  $$("[data-view]").forEach((button) => {
    const active = button.dataset.view === name;
    button.classList.toggle("is-active", active);
    if (active) button.setAttribute("aria-current", "page");
    else button.removeAttribute("aria-current");
  });
  if (name === "corpus") loadSources();
  if (name === "models") void refreshEvaluation();
  if (name === "capabilities") renderCapabilities(state.capabilityTab);
  setSidebarOpen(false);
  updateDesignLabels();
  updateBackToTop();
  $("#workspace").focus({ preventScroll: true });
}

function setTheme(theme) {
  document.documentElement.dataset.theme = theme;
  localStorage.setItem("agenticrag.theme", theme);
  const toggle = $("#theme-toggle");
  toggle.setAttribute("aria-label", `Switch to ${theme === "dark" ? "light" : "dark"} theme`);
  $("meta[name='theme-color']").content = theme === "dark" ? "#0C0C0D" : "#FAFAF8";
}

function providerForm(role) {
  return $(`[data-provider-form="${role}"]`);
}

function formPayload(role) {
  const form = providerForm(role);
  const data = new FormData(form);
  return {
    role,
    runtime: String(data.get("runtime") || ""),
    base_url: String(data.get("base_url") || ""),
    model: String(data.get("model") || ""),
    structured_output_mode: role === "embedding" ? "json_schema" : String(data.get("structured_output_mode") || "json_schema"),
    api_key: String(data.get("api_key") || ""),
    provider_kind: (profileById(String(data.get("runtime") || "")) || {}).provider_kind || "local",
  };
}

function fillProviderForm(role, values) {
  if (!values) return;
  const form = providerForm(role);
  for (const key of ["runtime", "base_url", "model", "structured_output_mode"]) {
    if (values[key] !== undefined && form.elements[key]) form.elements[key].value = values[key];
  }
}

function profileById(id) {
  return state.bootstrap.runtimes.find((profile) => profile.id === id);
}

function applyRuntimeProfile(role, runtimeId) {
  const profile = profileById(runtimeId);
  if (!profile) return;
  const form = providerForm(role);
  form.elements.runtime.value = runtimeId;
  form.elements.base_url.value = profile[`${role}_base_url`];
  form.elements.model.value = "";
  form.elements.api_key.value = "";
  if (role === "chat") form.elements.structured_output_mode.value = profile.structured_output_mode;
  const message = $(`[data-form-message="${role}"]`);
  if (message) {
    message.className = "form-message";
    message.textContent = profile.provider_kind === "openai"
      ? "Hosted and billable. Requests and delegated web searches leave the local boundary; the key remains in process memory."
      : "Local profile selected. Enter a model ID or probe the loopback runtime.";
  }
}

function hydrateModels() {
  for (const role of ["chat", "embedding"]) {
    const select = $(`[data-runtime-select="${role}"]`);
    select.replaceChildren();
    state.bootstrap.runtimes.forEach((profile) => {
      const option = el("option", "", profile.name);
      option.value = profile.id;
      select.append(option);
    });
    const configured = state.bootstrap.providers[role];
    const initial = configured.configured === false ? null : configured;
    if (initial) fillProviderForm(role, initial);
    else applyRuntimeProfile(role, "ollama");
    if (configured.configured !== false) setProviderStatus(role, "idle", "Configured", configured.model);
  }
  renderModelLibrary();
}

function modelDisplayName(model) {
  if (/^qwen3-embedding:0\.6b$/i.test(String(model))) return "Qwen3 Embedding 0.6B";
  const family = String(model).split(":", 1)[0].toLowerCase();
  const names = { gemma4: "Gemma 4", "gpt-oss": "GPT-OSS", qwen3: "Qwen3", "llama3.3": "Llama 3.3" };
  const size = String(model).match(/(?:^|:)\s*(\d+)b\b/i);
  const context = String(model).match(/workbench-(\d+)k$/i);
  const label = names[family] || family;
  return size ? `${label} ${size[1]}B${model.includes("a3b") ? " A3B" : ""}${context ? ` · ${context[1]}K context` : ""}` : model;
}

function updateComposerRoute() {
  const labels = { direct: "Direct · no library search", fixed: "Fixed · cites sources", agent: "Agentic · uses tools", supervisor: "Supervisor · specialist team" };
  $("#composer-route-mode").textContent = labels[state.workflow] || state.workflow;
  const chat = state.bootstrap?.providers?.chat;
  $("#composer-route-model").textContent = chat?.configured === false ? "Choose a model" : modelDisplayName(chat?.model || "Choose a model");
}

function renderModelLibrary() {
  const providers = state.bootstrap.providers;
  for (const role of ["chat", "embedding"]) {
    const provider = providers[role];
    const configured = provider.configured !== false;
    $(`#active-${role}-model`).textContent = configured ? modelDisplayName(provider.model) : "Not selected";
    $(`#active-${role}-model`).title = configured ? provider.model : "";
    const status = state.runtimeStatus?.[role];
    $(`#active-${role}-runtime`).textContent = configured ? `${provider.model} · ${provider.runtime} · ${status?.reachable ? "Reachable" : status ? "Unreachable" : "Configured"}` : "Connect a model to begin";
  }
  updateComposerRoute();
  const list = $("#installed-chat-models");
  list.replaceChildren();
  $("#installed-model-count").textContent = state.modelsDiscovered ? `${state.installedChatModels.length} available` : "Checking…";
  $("#models-nav-count").hidden = !state.modelsDiscovered;
  if (state.modelsDiscovered) $("#models-nav-count").textContent = String(state.installedChatModels.length);
  if (!state.modelsDiscovered) {
    list.append(el("p", "empty-list", "Checking installed chat models…"));
    return;
  }
  if (!state.installedChatModels.length) {
    list.append(el("p", "empty-list", "No local chat models found. Check that Ollama is running, then refresh."));
    return;
  }
  const header = el("div", "model-table-header");
  ["Model", "Loaded memory", "Avg answer time", "Answer checks", "No-evidence", ""].forEach((label) => header.append(el("span", "", label)));
  list.append(header);
  const fixedGroups = state.evaluation?.groups?.filter((item) => item.workflow === "fixed_rag") || [];
  const maxMemory = Math.max(1, ...fixedGroups.map((item) => Number(item.mean_model_loaded_gb) || 0));
  const maxLatency = Math.max(1, ...fixedGroups.map((item) => Number(item.mean_latency_ms) || 0));
  for (const model of state.installedChatModels) {
    const active = providers.chat.configured !== false && providers.chat.model === model && providers.chat.runtime === "ollama";
    const row = el("div", `installed-model${active ? " is-active" : ""}`);
    const identity = el("div", "installed-model-identity");
    const group = fixedGroups.find((item) => item.model === model);
    const failure = group && group.completed_count < group.run_count ? `${group.run_count - group.completed_count} of ${group.run_count} runs failed` : "";
    identity.append(el("strong", "", modelDisplayName(model)), el("code", "", model),
      el("span", failure ? "model-warning" : "", failure || (/(?:^|:)70b/i.test(model) ? "Large model · slower replies" : active ? "Currently in use" : "Installed on this Mac")));
    const select = active ? el("span", "model-in-use", "In use") : el("button", "secondary-button", "Use");
    select.setAttribute("aria-label", active ? `${modelDisplayName(model)} in use` : `Use ${modelDisplayName(model)} for chat`);
    if (!active) { select.type = "button"; select.addEventListener("click", async () => {
      select.disabled = true;
      const message = $("#library-message");
      message.className = "form-message";
      message.textContent = `Switching to ${model}…`;
      try {
        const current = state.bootstrap.providers.chat;
        if (current.configured === false || current.runtime !== "ollama") applyRuntimeProfile("chat", "ollama");
        else fillProviderForm("chat", current);
        providerForm("chat").elements.api_key.value = "";
        providerForm("chat").elements.model.value = model;
        await configureProvider("chat", providerForm("chat"), true);
        message.className = "form-message is-success";
        message.textContent = `${model} is selected for chat.`;
      } catch (error) {
        message.className = "form-message is-error";
        message.textContent = error.message;
      } finally {
        renderModelLibrary();
      }
    }); }
    const checks = group?.metric_denominators || {};
    const value = (number, suffix = "") => number != null && Number.isFinite(Number(number)) ? `${number}${suffix}` : "—";
    const metrics = el("div", "model-metrics");
    const meter = (label, ratio) => { const cell = el("div", "model-metric"); cell.append(el("span", "", label)); if (Number.isFinite(ratio)) { const track = el("progress", "metric-track"); track.max = 1; track.value = Math.min(1, Math.max(0, ratio)); cell.append(track); } return cell; };
    metrics.append(
      meter(value(group?.mean_model_loaded_gb, " GB"), group?.mean_model_loaded_gb == null ? NaN : Number(group.mean_model_loaded_gb) / maxMemory),
      meter(value(group?.mean_latency_ms == null ? null : (group.mean_latency_ms / 1000).toFixed(1), " s"), group?.mean_latency_ms == null ? NaN : Number(group.mean_latency_ms) / maxLatency),
      meter(group?.answer_substring_accuracy == null ? "—" : `${Math.round(group.answer_substring_accuracy * (checks.answer_cases || 0))} / ${checks.answer_cases || 0}`, NaN),
      meter(group?.appropriate_abstention == null ? "—" : `${Math.round(group.appropriate_abstention * (checks.unanswerable_cases || 0))} / ${checks.unanswerable_cases || 0}`, NaN),
    );
    row.append(identity, metrics, select);
    list.append(row);
  }
}

async function refreshEvaluation() {
  try {
    state.evaluation = await api("/api/v1/evaluation");
    renderEvaluation();
    renderModelLibrary();
    updateModeMenu();
  } catch (error) {
    $("#evaluation-description").textContent = `Could not load comparison results: ${error.message}`;
  }
}

function renderEvaluation() {
  const report = state.evaluation;
  const container = $("#evaluation-results");
  container.replaceChildren();
  const groups = report?.available && Array.isArray(report.groups) ? report.groups.filter((group) => group.model === state.bootstrap.providers.chat.model && group.mean_latency_ms != null) : [];
  $("#evaluation-description").textContent = report?.available
    ? `${report.repeat < 2 || report.case_count < 20 ? "Early check · " : ""}${report.case_count} questions · ${report.repeat} run${report.repeat === 1 ? "" : "s"} each · measured on this Mac ${new Date(report.created_at).toLocaleDateString()}`
    : "No measured comparison yet. Run the saved question set to compare modes and models.";
  const modeNames = { direct: "Direct", fixed_rag: "Fixed", bounded_agentic_rag: "Agentic", manager_multi_agent: "Supervisor" };
  if (groups.length >= 2) {
    const card = el("article", "mode-timing-card");
    card.append(el("h3", "", `Mode timing · ${modelDisplayName(state.bootstrap.providers.chat.model)}`));
    const slowest = Math.max(...groups.map((group) => group.mean_latency_ms));
    for (const group of groups) {
      const row = el("div", "mode-time-row");
      row.append(el("span", "", modeNames[group.workflow] || group.workflow));
      const bar = el("progress", "metric-track");
      bar.max = slowest;
      bar.value = group.mean_latency_ms;
      row.append(bar, el("span", "", `${(group.mean_latency_ms / 1000).toFixed(1)}s`));
      card.append(row);
    }
    card.append(el("p", "", "Verifies each mode path; not a quality comparison."));
    container.append(card);
  }
  const connections = el("article", "connections-card");
  connections.append(el("h3", "", "Connections"));
  const runtime = state.runtimeStatus?.chat;
  connections.append(el("p", "", `Ollama · ${runtime?.reachable ? "Reachable" : runtime ? "Unreachable" : "Checking"}`),
    el("p", "", "LM Studio · llama.cpp · vLLM · Not connected"),
    el("p", "", state.bootstrap.providers.chat.provider_kind === "openai" ? "Hosted OpenAI · On" : "Hosted OpenAI · Off"));
  const add = el("button", "secondary-button", "Add endpoint");
  add.type = "button";
  add.addEventListener("click", () => $("#connections-dialog").showModal());
  connections.append(add);
  container.append(connections);
}

async function discoverLocalModels() {
  const button = $("#discover-models-button");
  const message = $("#library-message");
  button.disabled = true;
  message.className = "form-message";
  message.textContent = "Checking models installed in Ollama…";
  try {
    const profile = profileById("ollama");
    const result = await post("/api/v1/probe", {
      role: "chat", runtime: "ollama", base_url: profile.chat_base_url,
      model: state.bootstrap.providers.chat.model || "local-probe",
      structured_output_mode: "json_object", provider_kind: "local", api_key: "",
    });
    state.installedChatModels = result.models.filter((model) => !/(embed|embedding)/i.test(model));
    state.modelsDiscovered = true;
    message.className = "form-message is-success";
    message.textContent = `${state.installedChatModels.length} chat models found on this Mac.`;
  } catch (error) {
    state.installedChatModels = [];
    state.modelsDiscovered = false;
    message.className = "form-message is-error";
    message.textContent = `${error.message} Advanced connections are available below.`;
  } finally {
    button.disabled = false;
    renderModelLibrary();
  }
}

function setProviderStatus(role, status, label, model) {
  const badge = $(`[data-form-status="${role}"]`);
  badge.textContent = label;
  badge.dataset.state = status;
  const dot = $(`#${role}-status-dot`);
  dot.dataset.state = status;
  if (model) {
    $(`#${role}-model-label`).textContent = modelDisplayName(model);
    $(`#${role}-model-label`).title = model;
  }
  dot.closest("button").setAttribute("aria-label", `${role === "chat" ? "Chat" : "Embedding"} model: ${$(`#${role}-model-label`).textContent}. Open Models`);
  renderReadiness();
}

async function refreshRuntimeStatus() {
  if (!state.bootstrap || document.hidden) return;
  try {
    state.runtimeStatus = await api("/api/v1/runtime-status");
    for (const role of ["chat", "embedding"]) {
      const status = state.runtimeStatus[role];
      const configured = state.bootstrap.providers[role]?.configured !== false;
      const tone = !configured ? "idle" : !status?.reachable || status.model_present === false ? "error" : "ready";
      setProviderStatus(role, tone, !configured ? "Not configured" : tone === "ready" ? "Reachable" : "Needs attention", state.bootstrap.providers[role]?.model);
      $(`#${role}-status-dot`).closest("button").title = status?.error || (status?.model_present === false ? "Configured model is not installed" : tone === "ready" ? `Reachable in ${status.latency_ms} ms` : "Not configured");
    }
    renderModelLibrary();
  } catch {
    state.runtimeStatus = null;
    renderReadiness();
  }
}

async function configureProvider(role, form, quiet = false) {
  const submit = $("button[type=" + '"submit"' + "]", form);
  const message = $(`[data-form-message="${role}"]`);
  const payload = formPayload(role);
  submit.disabled = true;
  setProviderStatus(role, "checking", "Connecting…");
  message.className = "form-message";
  message.textContent = payload.provider_kind === "openai" ? "Validating the hosted OpenAI connection…" : "Validating the loopback connection…";
  try {
    const result = await post("/api/v1/configure", payload);
    state.bootstrap.providers[role] = result.provider;
    state.runtimeStatus = null;
    syncHostedCapabilities();
    setProviderStatus(role, "ready", "Configured", result.provider.model);
    renderModelLibrary();
    renderEvaluation();
    message.classList.add("is-success");
    message.textContent = result.provider.provider_kind === "local" ? "Local selection saved for future launches." : "Hosted connection selected for this process.";
    if (!quiet) toast(`${role === "chat" ? "Chat" : "Embedding"} connection updated.`);
    void refreshRuntimeStatus();
    return result.provider;
  } catch (error) {
    setProviderStatus(role, "error", "Needs attention");
    message.classList.add("is-error");
    message.textContent = error.message;
    throw error;
  } finally {
    submit.disabled = false;
  }
}

async function probeProvider(role) {
  const form = providerForm(role);
  const button = $(`[data-probe="${role}"]`);
  const message = $(`[data-form-message="${role}"]`);
  button.disabled = true;
  try {
    setProviderStatus(role, "checking", "Probing…");
    const payload = formPayload(role);
    message.textContent = payload.provider_kind === "openai" ? "Calling OpenAI /v1/models…" : "Calling the local /v1/models endpoint…";
    const result = await post("/api/v1/probe", payload);
    const list = $(`#${role}-models`);
    list.replaceChildren();
    result.models.forEach((model) => {
      const option = document.createElement("option");
      option.value = model;
      list.append(option);
    });
    form.elements.model.setAttribute("list", `${role}-models`);
    if (result.models.length === 1) form.elements.model.value = result.models[0];
    const configured = state.bootstrap.providers[role].configured !== false;
    setProviderStatus(role, configured ? "ready" : "idle", configured ? "Configured" : "Discovered", configured ? state.bootstrap.providers[role].model : undefined);
    message.className = "form-message is-success";
    message.textContent = `${result.models.length} model${result.models.length === 1 ? "" : "s"} found in ${result.latency_ms} ms. Select or enter an identifier, then save.`;
  } catch (error) {
    setProviderStatus(role, "error", "Offline");
    message.className = "form-message is-error";
    message.textContent = error.message;
  } finally {
    button.disabled = false;
  }
}

async function checkAgentContract() {
  const form = providerForm("chat");
  const button = $("#contract-check-button");
  const message = $('[data-form-message="chat"]');
  button.disabled = true;
  try {
    await configureProvider("chat", form, true);
    message.className = "form-message";
    message.textContent = "Testing structured output, bounded reasoning, and tool selection…";
    const result = await post("/api/v1/check-model", {});
    message.className = "form-message is-success";
    message.textContent = `Agent contract passed in ${result.latency_ms} ms using ${result.structured_output_mode}.`;
    toast("The chat model passed the agent contract check.");
  } catch (error) {
    message.className = "form-message is-error";
    message.textContent = `${error.message} Try JSON object or Prompt only mode for this model.`;
    toast("The model needs a compatibility adjustment.", true);
  } finally {
    button.disabled = false;
  }
}

function renderSkillPicker() {
  const list = $("#skill-picker-list");
  list.replaceChildren();
  const skills = state.bootstrap.capabilities.skills;
  if (!skills.length) {
    list.append(el("p", "empty-list", "No local skills were discovered."));
    return;
  }
  skills.forEach((skill) => {
    const label = el("label", "skill-option");
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.value = skill.name;
    checkbox.checked = state.selectedSkills.has(skill.name);
    const copy = el("span");
    const description = el("span", "", compactText(skill.description, 180));
    description.title = skill.description;
    copy.append(el("strong", "", skill.name), description);
    label.append(checkbox, copy);
    checkbox.addEventListener("change", () => {
      if (checkbox.checked) state.selectedSkills.add(skill.name);
      else state.selectedSkills.delete(skill.name);
      updateSelectedSkills();
    });
    list.append(label);
  });
}

function updateSelectedSkills() {
  const names = [...state.selectedSkills];
  const usedInMode = ["agent", "supervisor"].includes(state.workflow);
  $("#selected-skill-count").textContent = String(names.length);
  $("#selected-skill-count").hidden = names.length === 0;
  const summary = $("#selected-skills-summary");
  summary.textContent = names.length ? `${names.length} skill${names.length === 1 ? "" : "s"} selected` : "No skills selected";
  summary.title = names.join(" · ");
  summary.classList.toggle("has-skills", usedInMode && names.length > 0);
}

function capabilityTotal() {
  const capabilities = state.bootstrap.capabilities;
  return capabilities.tools.length + capabilities.agents.length + capabilities.skills.length + capabilities.plugins.length;
}

function syncHostedCapabilities() {
  if (!state.bootstrap) return;
  const chat = state.bootstrap.providers.chat;
  const available = chat.configured !== false && (
    (chat.provider_kind === "openai" && chat.credential_configured) ||
    (chat.provider_kind === "local" && state.bootstrap.local_web_search_available)
  );
  const hosted = [state.bootstrap.providers.chat, state.bootstrap.providers.embedding]
    .some((provider) => provider.configured !== false && provider.provider_kind === "openai");
  const boundary = $("#boundary-badge");
  boundary.lastChild.textContent = hosted ? " Hosted model active" : state.allowWeb ? " Local model · web on" : " On this Mac";
  boundary.dataset.hosted = String(hosted);
  const webTool = state.bootstrap.capabilities.tools.find((item) => item.id === "web_search");
  const webAgent = state.bootstrap.capabilities.agents.find((item) => item.id === "web_researcher");
  if (webTool) webTool.enabled = available;
  if (webAgent) webAgent.enabled = available;
  const input = $("#allow-web-input");
  input.disabled = !available || !["direct", "supervisor"].includes(state.workflow);
  if (input.disabled) {
    input.checked = false;
    state.allowWeb = false;
  }
  renderCapabilities(state.capabilityTab);
}

function renderCapabilities(tab) {
  if (!state.bootstrap) return;
  state.capabilityTab = tab;
  $$("[data-capability-tab]").forEach((button) => {
    const active = button.dataset.capabilityTab === tab;
    button.classList.toggle("is-active", active);
    button.setAttribute("aria-selected", String(active));
  });
  const content = $("#capability-content");
  content.replaceChildren();
  const capabilities = state.bootstrap.capabilities;
  if (tab === "agent") {
    const intro = el("div", "capability-intro");
    intro.append(el("h2", "", "Host-owned agent policy"), el("p", "", "The model proposes actions and critiques answers. The workbench enforces every execution and evidence boundary."));
    const definition = el("dl", "policy-definition");
    const rows = [
      ["Planning", capabilities.agent.planning],
      ["Review", capabilities.agent.review],
      ["Tool allowlist", capabilities.agent.tool_allowlist.join(", ")],
      ["Default steps", String(capabilities.agent.default_limits.max_steps)],
      ["Time budget", `${capabilities.agent.default_limits.max_seconds} seconds`],
      ["Evidence budget", `${capabilities.agent.tool_budget.max_evidence_chunks} chunks`],
      ["Search / lookup", `${capabilities.agent.tool_budget.max_searches} / ${capabilities.agent.tool_budget.max_lookups}`],
    ];
    rows.forEach(([term, description]) => definition.append(el("dt", "", term), el("dd", "", description)));
    content.append(intro, definition);
    return;
  }
  const titles = {
    tools: ["Read-only tools", "Host-executed functions the model may request within explicit budgets."],
    agents: ["Available agents", "The supervisor may call these bounded specialists; specialists cannot recursively delegate."],
    skills: ["Runtime skills", "Auditable instruction bundles loaded only when selected by the operator or supervisor."],
    plugins: ["Plugins", capabilities.plugin_status],
  };
  const intro = el("div", "capability-intro");
  intro.append(el("h2", "", titles[tab][0]), el("p", "", titles[tab][1]));
  const list = el("div", "capability-list");
  const items = capabilities[tab];
  if (!items.length) list.append(el("p", "empty-list", tab === "plugins" ? "No plugin adapters are installed yet." : "Nothing discovered."));
  items.forEach((item) => {
    const row = el("article", "capability-row");
    const copy = el("div");
    copy.append(el("h3", "", item.name));
    if (item.description) {
      const description = el("p", "", compactText(item.description));
      description.title = item.description;
      copy.append(description);
    }
    const meta = el("div", "capability-meta");
    if (item.access) meta.append(el("span", "meta-chip", item.access));
    if (item.source) meta.append(el("span", "meta-chip", item.source));
    if (item.sha256) meta.append(el("span", "meta-chip", item.sha256.slice(0, 12)));
    copy.append(meta);
    const status = el("span", `enabled-label${item.enabled ? "" : " is-disabled"}`, item.enabled ? "Enabled" : "Unavailable");
    row.append(copy, status);
    list.append(row);
  });
  content.append(intro, list);
}

function readinessRow(title, detail, ready, warning = false) {
  const row = el("div", `readiness-item ${ready ? "is-ready" : warning ? "is-warning" : ""}`);
  row.append(el("span", "readiness-icon", ready ? "✓" : warning ? "!" : "·"));
  const copy = el("div");
  copy.append(el("strong", "", title), el("p", "", detail));
  row.append(copy);
  return row;
}

function renderReadiness() {
  if (!state.bootstrap) return;
  const providers = state.bootstrap.providers;
  const chatReady = providers.chat.configured !== false;
  const embeddingReady = providers.embedding.configured !== false;
  const storeReady = Boolean(state.bootstrap.store && state.bootstrap.store.backend);
  const capabilityReady = state.bootstrap.capabilities.tools.length > 0;
  const readyCount = [chatReady, embeddingReady, storeReady, capabilityReady].filter(Boolean).length;
  $("#readiness-ring").textContent = `${readyCount}/4`;
  const chatStatus = state.runtimeStatus?.chat;
  const notice = $("#runtime-notice");
  notice.hidden = !chatStatus?.configured || (chatStatus.reachable && chatStatus.model_present !== false);
  if (!notice.hidden) $("#runtime-notice-text").textContent = `${modelDisplayName(providers.chat.model)} is not ready. ${chatStatus.model_present === false ? "The configured model was not found." : chatStatus.error || "Check the runtime connection."}`;
  const embeddingStatus = state.runtimeStatus?.embedding;
  $("#readiness-label").textContent = chatStatus?.configured && (!chatStatus.reachable || chatStatus.model_present === false)
    ? "Chat model unreachable"
    : embeddingStatus?.configured && (!embeddingStatus.reachable || embeddingStatus.model_present === false)
      ? "Embedding model unreachable"
      : readyCount === 4 ? `${chatStatus?.reachable && embeddingStatus?.reachable ? "Ready" : "Configured"} · 4 of 4` : readyCount >= 2 ? `Configured · ${readyCount} of 4` : "Needs setup";
  $("#readiness-label").dataset.state = chatStatus?.reachable && embeddingStatus?.reachable && chatStatus.model_present !== false && embeddingStatus.model_present !== false
    ? "ready" : chatStatus?.configured && (!chatStatus.reachable || chatStatus.model_present === false) || embeddingStatus?.configured && (!embeddingStatus.reachable || embeddingStatus.model_present === false) ? "error" : "idle";
  try {
    const provider = providers.chat;
    $("#runtime-endpoint-label").textContent = provider.configured === false ? "" : `${provider.runtime} · ${new URL(provider.base_url).host}`;
  } catch { $("#runtime-endpoint-label").textContent = ""; }
  const list = $("#readiness-list");
  if (list) {
    list.replaceChildren(
      readinessRow("Chat runtime", chatStatus?.error || (chatStatus?.model_present === false ? "Configured model was not found" : chatReady ? `${providers.chat.runtime} · ${providers.chat.model}` : "Choose a runtime and model in Models."), chatReady && chatStatus?.reachable && chatStatus?.model_present !== false, !chatReady || !!chatStatus?.error || chatStatus?.model_present === false),
      readinessRow("Embedding runtime", state.runtimeStatus?.embedding?.error || (embeddingReady ? `${providers.embedding.runtime} · ${providers.embedding.model}` : "Required for ingest and retrieval workflows."), embeddingReady && state.runtimeStatus?.embedding?.reachable && state.runtimeStatus?.embedding?.model_present !== false, !embeddingReady || !!state.runtimeStatus?.embedding?.error),
      readinessRow("Corpus store", `${state.bootstrap.store.backend} · initialized on first use`, storeReady),
      readinessRow("Agent boundary", `${state.bootstrap.capabilities.tools.length} tools · ${state.bootstrap.capabilities.skills.length} skills`, capabilityReady),
    );
    $("#inspector-title").textContent = "Configuration status";
  }
}

function appendMessage(kind, content, meta, animate = true) {
  $("#chat-empty").hidden = true;
  const message = el("article", `message ${kind}`);
  if (animate) message.classList.add("is-entering");
  const header = el("div", "message-meta");
  header.append(el("strong", "", kind === "user" ? "You" : "AgenticRAG"), el("span", "", meta || ""));
  message.append(header, el("div", "message-content", content));
  $("#conversation").append(message);
  scrollChatToBottom();
  return message;
}

function appendLoading() {
  const message = appendMessage("assistant is-loading", "", "working within configured budgets");
  if (["agent", "supervisor"].includes(state.workflow)) $(".message-meta", message).append(el("span", "verification-badge", "Review pending"));
  else if (state.workflow === "fixed") $(".message-meta", message).append(el("span", "verification-badge", "Answer in progress"));
  const content = $(".message-content", message);
  content.append(el("div", "answer-skeleton"), el("p", "waiting-note", "The answer appears once sources are read."));
  return message;
}

function renderLiveSteps(message, events, limits) {
  if (!events.length) return;
  let details = $(".steps-inline", message);
  if (!details) {
    details = el("details", "steps-inline live-steps");
    details.append(el("summary"), el("div", "steps-inline-list trace-list"));
    message.insertBefore(details, $(".message-content", message));
  }
  $("summary", details).textContent = stepChain(events);
  const rows = $(".steps-inline-list", details);
  rows.replaceChildren();
  appendTraceRows(rows, events, null, true);
  if (limits?.max_steps) {
    let budget = $(".run-budget", message);
    if (!budget) { budget = el("p", "run-budget"); details.after(budget); }
    const actions = events.filter((event) => event.kind === "tool_called").length + (events.some((event) => event.kind === "retrieval_completed") ? 1 : 0);
    budget.textContent = `${actions} / ${limits.max_steps} tool actions · ${((events.at(-1)?.at_ms || 0) / 1000).toFixed(1)} / ${limits.max_seconds || 180}s`;
  }
}

function renderMarkdown(container, markdown) {
  if (!window.marked || !window.DOMPurify) {
    container.textContent = markdown;
    return;
  }
  const parsed = window.marked.parse(markdown, { gfm: true, breaks: true });
  container.innerHTML = window.DOMPurify.sanitize(parsed, {
    USE_PROFILES: { html: true },
    FORBID_TAGS: ["img", "iframe", "form", "style"],
    FORBID_ATTR: ["style"],
  });
  container.querySelectorAll("a").forEach((link) => {
    link.target = "_blank";
    link.rel = "noopener noreferrer";
  });
  container.querySelectorAll("table").forEach((table) => {
    const scroll = el("div", "table-scroll");
    table.replaceWith(scroll);
    scroll.append(table);
  });
  container.querySelectorAll("pre").forEach((block) => {
    const wrapper = el("div", "code-panel");
    const copy = el("button", "code-copy", "Copy code");
    copy.type = "button";
    copy.addEventListener("click", () => void copyText(block.textContent || "", copy));
    block.replaceWith(wrapper);
    wrapper.append(copy, block);
  });
}

async function copyText(value, button) {
  try {
    await navigator.clipboard.writeText(value);
    const previous = button.textContent;
    button.textContent = "Copied";
    window.setTimeout(() => { button.textContent = previous; }, 1800);
  } catch {
    toast("Copy is unavailable in this browser.", true);
  }
}

function renderResult(result, loading, stored = false) {
  loading.className = "message assistant";
  $(".steps-inline", loading)?.remove();
  $(".run-budget", loading)?.remove();
  $(".live-evidence-count", loading)?.remove();
  result._viewId = crypto.randomUUID();
  const workflowName = { direct: "Direct", fixed_rag: "Fixed RAG", bounded_agentic_rag: "Agentic", manager_multi_agent: "Supervisor", web_research: "Web research" }[result.workflow] || result.workflow || "Response";
  const meta = $(".message-meta", loading);
  $(".verification-badge", meta)?.remove();
  const providerModel = typeof result.provider === "string" ? result.provider.match(/^(?:local|openai):(.+?)@/)?.[1] : null;
  const modelPart = providerModel ? ` · ${modelDisplayName(providerModel)}` : "";
  $(".message-meta span", loading).textContent = result.abstained ? `${workflowName}${modelPart} · needs sources` : `${workflowName}${modelPart}${stored ? " · saved" : result.elapsed_ms ? ` · ${(result.elapsed_ms / 1000).toFixed(1)} s` : ""}`;
  const events = result.events || [];
  const review = events.findLast((event) => event.kind === "review_completed" && event.detail?.accepted === true);
  const validated = events.some((event) => event.kind === "answer_validated");
  let badge = "";
  let badgeTone = "";
  if (result.abstained || events.some((event) => event.kind === "abstained")) { badge = "Not enough evidence to answer"; badgeTone = "is-warning"; }
  else if (events.some((event) => event.kind === "budget_exhausted")) { badge = "Stopped at budget"; badgeTone = "is-warning"; }
  else if (review && validated && review.detail?.unsupported_claim_count === 0) { badge = "Review passed · no unsupported claims"; badgeTone = "is-success"; }
  else if (validated && result.citations?.length) { badge = `${result.citations.length} citation${result.citations.length === 1 ? "" : "s"} validated`; badgeTone = "is-success"; }
  if (badge) meta.append(el("span", `verification-badge ${badgeTone}`, badge));
  if (events.length && result.workflow !== "direct") {
    const details = el("details", "steps-inline");
    const citedCount = result.citations?.length || 0;
    const summary = el("summary", "", `${stepChain(events)} · ${citedCount} source${citedCount === 1 ? "" : "s"} cited`);
    const rows = el("div", "steps-inline-list trace-list");
    appendTraceRows(rows, events, result.elapsed_ms);
    details.append(summary, rows);
    loading.insertBefore(details, $(".message-content", loading));
  }
  const content = $(".message-content", loading);
  content.replaceChildren();
  renderMarkdown(content, result.answer);
  if (result.citations?.length) linkCitationMarkers(content, result);
  if (result.citations?.length) {
    const citations = el("div", "citation-strip");
    citations.append(el("span", "citation-label", "Sources"));
    result.citations.forEach((citation, index) => {
      const button = el("button", "citation-button");
      button.type = "button";
      button.dataset.resultId = result._viewId;
      button.dataset.citationIndex = String(index);
      button.setAttribute("aria-pressed", "false");
      button.append(el("span", "citation-number", String(index + 1)), document.createTextNode(citation.logical_path.split("/").pop()));
      button.addEventListener("click", () => openResultPanel(result, "evidence", index));
      citations.append(button);
    });
    loading.append(citations);
  }
  if (result.external_sources && result.external_sources.length) {
    const sources = el("div", "citation-strip");
    result.external_sources.forEach((source, index) => {
      const link = el("a", "citation-button", `${index + 1}  ${source.title || source.url}`);
      link.href = source.url;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      sources.append(link);
    });
    loading.append(sources);
  }
  const actions = el("div", "message-actions");
  const copy = el("button", "", "Copy response");
  copy.type = "button";
  copy.addEventListener("click", () => void copyText(result.answer, copy));
  actions.append(copy);
  const remember = el("button", "", "Save to memory");
  remember.type = "button";
  remember.addEventListener("click", () => void openMemoryDialog({
    content: result.answer.replace(/\s+/g, " ").trim().slice(0, 1000),
    sourceChatId: state.activeChatId || "",
  }));
  actions.append(remember);
  if (result.events?.length) {
    const inspect = el("button", "", "View steps");
    inspect.type = "button";
    inspect.addEventListener("click", () => openResultPanel(result, "steps"));
    actions.append(inspect);
  }
  loading.append(actions);
}

function linkCitationMarkers(container, result) {
  const walker = document.createTreeWalker(container, NodeFilter.SHOW_TEXT);
  const nodes = [];
  while (walker.nextNode()) nodes.push(walker.currentNode);
  for (const node of nodes) {
    if (node.parentElement?.closest("code, pre, a, button")) continue;
    const value = node.textContent || "";
    const matches = [...value.matchAll(/\[(\d+)\]/g)];
    if (!matches.some((match) => Number(match[1]) >= 1 && Number(match[1]) <= result.citations.length)) continue;
    const fragment = document.createDocumentFragment();
    let last = 0;
    for (const match of matches) {
      const index = Number(match[1]) - 1;
      fragment.append(document.createTextNode(value.slice(last, match.index)));
      if (index >= 0 && index < result.citations.length) {
        const citation = result.citations[index];
        const button = el("button", "inline-citation", String(index + 1));
        button.type = "button";
        button.dataset.resultId = result._viewId;
        button.dataset.citationIndex = String(index);
        button.setAttribute("aria-pressed", "false");
        button.setAttribute("aria-label", `Source ${index + 1}: ${citation.logical_path.split("/").pop()}`);
        button.title = `${citation.logical_path} — ${(citation.section_path || []).join(" › ")}`;
        button.addEventListener("click", () => openResultPanel(result, "evidence", index));
        fragment.append(button);
      } else fragment.append(document.createTextNode(match[0]));
      last = match.index + match[0].length;
    }
    fragment.append(document.createTextNode(value.slice(last)));
    node.replaceWith(fragment);
  }
}

function openResultPanel(result, tab = "evidence", selected = 0) {
  $$(`[data-result-id="${result._viewId}"]`).forEach((button) => {
    button.setAttribute("aria-pressed", String(tab === "evidence" && Number(button.dataset.citationIndex) === selected));
  });
  const title = $("#inspector-title");
  title.textContent = "";
  const body = $("#inspector-body");
  body.replaceChildren();
  const tabs = el("div", "inspector-tabs");
  const evidenceButton = el("button", tab === "evidence" ? "is-active" : "", `Evidence ${result.citations?.length || 0}`);
  const stepsButton = el("button", tab === "steps" ? "is-active" : "", `Steps ${result.events?.length || 0}`);
  [evidenceButton, stepsButton].forEach((button) => { button.type = "button"; });
  evidenceButton.addEventListener("click", () => openResultPanel(result, "evidence", selected));
  stepsButton.addEventListener("click", () => openResultPanel(result, "steps", selected));
  tabs.append(evidenceButton, stepsButton);
  body.append(tabs);
  if (tab === "steps") {
    const trace = el("div", "trace-list");
    appendTraceRows(trace, result.events || [], result.elapsed_ms);
    body.append(trace);
    (result.delegations || []).forEach((delegation) => {
      const card = el("div", "evidence-preview");
      card.append(el("strong", "", `${delegation.agent.replaceAll("_", " ")} · ${delegation.status}`), el("p", "", delegation.summary));
      body.append(card);
    });
  } else {
    const evidence = result.evidence || [];
    const retrievedCount = result.retrieved_count ?? Math.max(evidence.length, ...((result.events || []).map((event) => Number(event.detail?.evidence_count) || 0)));
    body.append(el("p", "inspector-counts", `${retrievedCount} retrieved · ${result.citations?.length || 0} cited`));
    (result.citations || []).forEach((citation, index) => {
      const card = el("div", `evidence-preview${index === selected ? " is-selected" : ""}`);
      const chunk = evidence.find((item) => item.chunk?.id === citation.chunk_id || item.chunk_id === citation.chunk_id);
      const section = citation.section_path?.at(-1) || chunk?.chunk?.heading || chunk?.heading || (citation.page_start ? `p. ${citation.page_start}` : "");
      const count = $$(`.inline-citation[data-result-id="${result._viewId}"][data-citation-index="${index}"]`).length;
      const passage = plainPassage(chunk?.chunk?.text || chunk?.text || "");
      const heading = el("button", "evidence-card-heading");
      heading.type = "button";
      heading.setAttribute("aria-expanded", String(index === selected));
      heading.append(el("span", "citation-number", String(index + 1)), el("span", "evidence-card-heading-copy"));
      $(".evidence-card-heading-copy", heading).append(el("strong", "", citation.logical_path.split("/").pop()), el("small", "", [section, count ? `cited ${count}×` : passage.slice(0, 90)].filter(Boolean).join(" · ")));
      heading.addEventListener("click", () => openResultPanel(result, "evidence", index));
      card.append(heading);
      let versionLabel;
      if (index === selected) {
        const quote = el("blockquote", "evidence-passage");
        if (passage) quote.append(el("mark", "", passage));
        else quote.textContent = "Open this source to read the saved passage.";
        card.append(quote);
        versionLabel = el("span", "", `v·${citation.source_version_id.replace(/^version_/, "").slice(0, 8)}`);
        void enrichEvidencePassage(citation, quote, versionLabel);
      }
      const open = el("button", "secondary-button", "Open source");
      open.type = "button";
      open.addEventListener("click", () => { setView("corpus"); void openSource(citation.source_version_id, citation); });
      if (index === selected) {
        const footer = el("div", "evidence-card-footer");
        footer.append(versionLabel);
        const copy = el("button", "secondary-button", "Copy citation");
        copy.type = "button";
        copy.addEventListener("click", () => void copyText(`${citation.logical_path}${citation.section_path?.length ? ` §${citation.section_path.join(" › ")}` : ""} [${citation.source_version_id}:${citation.start_char}-${citation.end_char}]`, copy));
        footer.append(copy, open);
        card.append(footer);
      }
      body.append(card);
    });
    const cited = new Set((result.citations || []).map((item) => item.chunk_id));
    const uncited = evidence.filter((item) => !cited.has(item.chunk?.id || item.chunk_id));
    if (uncited.length) body.append(el("p", "inspector-counts", `${uncited.length} retrieved but not cited`));
    uncited.slice(0, 3).forEach((item) => body.append(el("div", "uncited-row", [item.chunk?.logical_path || item.logical_path || "Passage", item.chunk?.section_path?.at(-1) || item.chunk?.heading].filter(Boolean).join(" · "))));
  }
  const note = el("p", "inspector-trust", "Retrieved text is evidence, never executable instruction. The host validates every model-selected action.");
  body.append(note);
  openInspector();
}

function openLiveEvidence(items) {
  $("#inspector-title").textContent = "Evidence arriving";
  const body = $("#inspector-body");
  body.replaceChildren(el("p", "inspector-counts", `${items.length} passages retrieved so far`));
  items.forEach((item) => body.append(el("div", "uncited-row", [item.logical_path?.split("/").pop(), item.heading].filter(Boolean).join(" · "))));
  openInspector();
}

function plainPassage(markdown) {
  return plainDocument(markdown).replace(/[ \t]+/g, " ").replace(/\n{3,}/g, "\n\n").trim();
}

async function enrichEvidencePassage(citation, quote, versionLabel) {
  try {
    const { scopes } = currentContext();
    const query = new URLSearchParams();
    scopes.forEach((scope) => query.append("scope", scope));
    const source = await api(`/api/v1/sources/${encodeURIComponent(citation.source_version_id)}?${query}`);
    const text = source.text || "";
    if (!quote.isConnected || !Number.isInteger(citation.start_char) || !Number.isInteger(citation.end_char) || citation.start_char < 0 || citation.end_char > text.length || citation.end_char <= citation.start_char) return;
    let start = citation.start_char;
    let end = citation.end_char;
    while (start > 0 && !/\s/.test(text[start - 1]) && citation.start_char - start < 60) start--;
    while (end < text.length && !/\s/.test(text[end]) && end - citation.end_char < 60) end++;
    const excerpt = plainPassage(text.slice(start, end));
    if (excerpt) quote.replaceChildren(el("mark", "", `${start > 0 ? "… " : ""}${excerpt}${end < text.length ? " …" : ""}`));
    const type = source.media_type?.includes("markdown") ? "Markdown" : source.media_type?.includes("pdf") ? "PDF" : source.media_type?.split("/").at(-1)?.toUpperCase();
    versionLabel.textContent = [`v·${source.id.replace(/^version_/, "").slice(0, 8)}`, type, Number.isFinite(source.byte_size) ? formatBytes(source.byte_size) : ""].filter(Boolean).join(" · ");
  } catch { /* Keep the saved excerpt when the source is unavailable. */ }
}

function plainDocument(markdown) {
  return String(markdown).replace(/^#{1,6}\s+/gm, "").replace(/!?(\[([^\]]+)\])\([^)]*\)/g, "$2")
    .replace(/(?:\*\*|__|~~|`)/g, "").replace(/^\s*[-*+]\s+/gm, "");
}

function chainLabel(event) {
  if (event.kind === "tool_called") return { search: "Search", lookup: "Read", calculate: "Calc" }[event.detail?.action] || "Tool";
  return { plan_created: "Plan", skill_loaded: "Skill", retrieval_completed: "Search", generation_completed: "Draft", review_completed: "Review", answer_validated: "Validate", delegation_started: "Specialist", delegation_completed: "Specialist", web_search_completed: "Web", synthesis_completed: "Synthesize", abstained: "Abstain", budget_exhausted: "Budget" }[event.kind] || "";
}

function stepChain(events) {
  const labels = [];
  for (const event of events) {
    const label = chainLabel(event);
    if (!label) continue;
    if (labels.at(-1)?.label === label) labels.at(-1).count++;
    else labels.push({ label, count: 1 });
  }
  return labels.map(({ label, count }) => `${label}${count > 1 ? ` ×${count}` : ""}`).join(" › ") || `${events.length} steps`;
}

function appendTraceRows(container, events, elapsedMs = null, live = false) {
  events.forEach((event, index) => {
    const error = event.kind === "validation_rejected" || event.detail?.success === false;
    const row = el("div", `trace-item${error ? " is-error" : ""}${live && index === events.length - 1 ? " is-running" : ""}`);
    const heading = el("div", "trace-heading");
    heading.append(el("strong", "", humanEvent(event)));
    const previous = events[index - 1]?.at_ms ?? 0;
    if (Number.isFinite(event.at_ms)) {
      const duration = Math.max(0, event.at_ms - previous);
      heading.append(el("time", "", duration < 100 ? "<0.1s" : `${(duration / 1000).toFixed(1)}s`));
    }
    row.append(heading, el("p", "", eventDetailText(event)));
    container.append(row);
  });
}

function humanEvent(event) {
  if (event.kind === "tool_called") return { search: "Searched library", lookup: "Read source", calculate: "Calculated" }[event.detail?.action] || "Used tool";
  const labels = {
    plan_created: "Plan created",
    skill_loaded: "Skill loaded",
    tool_called: "Tool called",
    review_completed: "Evidence review",
    validation_rejected: "Answer validation rejected",
    answer_validated: "Answer validated",
    retrieval_completed: "Retrieval completed",
    generation_completed: "Generation completed",
    abstained: "Safe abstention",
    budget_exhausted: "Budget exhausted",
    delegation_started: "Delegation started",
    delegation_completed: "Delegation completed",
    web_search_completed: "Web search",
    synthesis_completed: "Supervisor synthesis",
    failed: "Run failed",
  };
  return labels[event.kind] || event.kind.replaceAll("_", " ");
}

function eventDetailText(event) {
  const detail = event.detail || {};
  const seconds = (value) => `${(value / 1000).toFixed(1)}s`;
  if (event.kind === "plan_created") return detail.manager ? `${detail.delegation_count || 0} specialists` : `${detail.obligation_count || 0} obligations${detail.obligations?.length ? ` · ${detail.obligations.map((item) => item.question).join("; ")}` : ""}`;
  if (event.kind === "skill_loaded") return detail.name || "Trusted instruction loaded";
  if (event.kind === "retrieval_completed") return [detail.query, `${detail.evidence_delta ?? detail.evidence_count ?? 0} new passages`].filter(Boolean).join(" · ");
  if (event.kind === "tool_called") return detail.success === false ? detail.error || "Tool failed" : [detail.summary?.query || detail.summary?.source_path || detail.summary?.expression, detail.evidence_delta ? `${detail.evidence_delta} new passages` : ""].filter(Boolean).join(" · ") || "Completed";
  if (event.kind === "review_completed") return detail.accepted ? `Accepted · ${detail.unsupported_claim_count ?? 0} unsupported claims${detail.missing_obligation_count == null ? "" : ` · ${detail.missing_obligation_count} missing obligations`}` : "Sent back for revision";
  if (event.kind === "answer_validated") return `${detail.citation_count ?? 0} citation ID${detail.citation_count === 1 ? "" : "s"} ${detail.citation_count === 1 ? "resolves" : "resolve"} to the evidence set`;
  if (event.kind === "validation_rejected") return detail.reason || "Output did not pass validation";
  if (event.kind === "abstained") return String(detail.reason || "Insufficient evidence").replaceAll("_", " ");
  if (event.kind === "budget_exhausted") return [detail.kind, detail.phase].filter(Boolean).join(" · ") || "Run budget reached";
  if (event.kind === "delegation_started" || event.kind === "delegation_completed") return [detail.agent?.replaceAll("_", " "), detail.success == null ? "started" : detail.success ? "completed" : "failed"].filter(Boolean).join(" · ");
  if (event.kind === "synthesis_completed") return `${detail.used_delegations?.length || 0} specialist reports used`;
  if (event.kind === "web_search_completed" && Number.isFinite(detail.elapsed_ms)) {
    return `${seconds(detail.elapsed_ms)} · ${detail.source_count || 0} sources${detail.finding_chars == null ? "" : ` · ${Number(detail.finding_chars).toLocaleString()} characters of findings`}`;
  }
  if (event.kind === "generation_completed" && detail.workflow_model_calls === 1) {
    const parts = [`${seconds(detail.elapsed_ms)} model time`];
    if (detail.prompt_tokens != null) parts.push(`${detail.prompt_tokens} input tokens`);
    if (detail.completion_tokens != null) parts.push(`${detail.completion_tokens} output tokens`);
    if (detail.request_attempts > 1) parts.push(`${detail.request_attempts} attempts`);
    return parts.join(" · ");
  }
  if (event.kind === "generation_completed") return [detail.prompt_tokens != null ? `${detail.prompt_tokens} in` : "", detail.completion_tokens != null ? `${detail.completion_tokens} out` : ""].filter(Boolean).join(" · ") || "Answer drafted";
  return "Completed";
}

function closeInspector() {
  const wasOpen = $(".inspector").classList.contains("is-open");
  $(".inspector").classList.remove("is-open");
  $(".inspector").setAttribute("aria-hidden", "true");
  $("#inspector-backdrop").hidden = true;
  if (wasOpen && state.inspectorInvoker?.isConnected) state.inspectorInvoker.focus({ preventScroll: true });
  state.inspectorInvoker = null;
}

function openInspector() {
  if (!$('.inspector').classList.contains('is-open')) state.inspectorInvoker = document.activeElement;
  $(".inspector").classList.add("is-open");
  $(".inspector").setAttribute("aria-hidden", "false");
  $("#inspector-backdrop").hidden = false;
  $("#inspector-close").focus();
}

async function runQuestion(question) {
  const originalQuestion = question;
  const context = currentContext();
  const workflow = state.workflow;
  const attachment = state.chatAttachment;
  closeInspector();
  const send = $("#send-button");
  send.disabled = true;
  send.hidden = true;
  $("#stop-button").hidden = false;
  $("#stop-button").disabled = true;
  state.stopRequested = false;
  state.followRunOutput = true;
  $$('[data-workflow]').forEach((button) => { button.disabled = true; });
  $("#mode-pill").disabled = true;
  toggleModeMenu(false);
  $("#new-chat-button").disabled = true;
  let loading = null;
  let streamBuffer = "";
  let streamTimer = null;
  let userNode = null;
  let createdChatId = null;
  const liveEvents = [];
  let liveEvidence = [];
  let runLimits = null;
  try {
    let image = null;
    if (attachment) {
      if (isImageFile(attachment)) {
        if (attachment.size > 8 * 1024 * 1024) throw new Error("Images must be 8 MiB or smaller.");
        image = { filename: attachment.name, mime_type: imageMimeType(attachment), data_base64: await fileToBase64(attachment) };
      } else {
        const limit = state.bootstrap.ingestion.limits.max_file_bytes;
        if (attachment.size > limit) throw new Error(`Files must be ${formatBytes(limit)} or smaller.`);
        await post("/api/v1/ingest", {
          filename: attachment.name,
          content_base64: await fileToBase64(attachment),
          ...context,
          ocr: "auto",
        });
        question += `\n\n[Attached source: ${attachment.name}]`;
        await refreshCorpusStatus();
      }
    }
    if (!state.activeChatId) {
      const chat = await post("/api/v1/chats", context);
      state.activeChatId = chat.id;
      createdChatId = chat.id;
      localStorage.setItem("agenticrag.activeChatId", chat.id);
    }
    userNode = appendMessage("user", question + (image ? `\n[Attached image: ${attachment.name}]` : ""), workflow === "direct" ? "You" : `You · ${workflow}`);
    loading = appendLoading();
    state.runId = crypto.randomUUID().replaceAll("-", "");
    $("#active-run-count").hidden = false;
    renderHistoryList();
    const result = await streamQuestion({
      question,
      ...context,
      workflow,
      skills: [...state.selectedSkills],
      max_steps: 8,
      allow_web: ["direct", "supervisor"].includes(workflow) && state.allowWeb,
      ...(image ? { image } : {}),
      chat_id: state.activeChatId,
      run_id: state.runId,
    }, (message) => { if (!liveEvents.length) $(".waiting-note", loading).textContent = message; }, (started) => {
      runLimits = started.limits;
      $("#stop-button").disabled = false;
    }, (token) => {
      const content = $(".message-content", loading);
      streamBuffer += token;
      loading.classList.add("is-streaming");
      content.setAttribute("aria-live", "off");
      if (!streamTimer) streamTimer = window.setTimeout(() => {
        streamTimer = null;
        renderMarkdown(content, streamBuffer);
        if (state.followRunOutput) scrollChatToBottom();
      }, 120);
    }, (event) => {
      liveEvents.push(event);
      renderLiveSteps(loading, liveEvents, runLimits);
      if (state.followRunOutput) scrollChatToBottom();
    }, (items) => {
      liveEvidence = items;
      let button = $(".live-evidence-count", loading);
      if (!button) {
        button = el("button", "live-evidence-count");
        button.type = "button";
        button.addEventListener("click", () => openLiveEvidence(liveEvidence));
        loading.insertBefore(button, $(".message-content", loading));
      }
      button.textContent = `${items.length} passages retrieved · View evidence`;
    });
    if (streamTimer) window.clearTimeout(streamTimer);
    renderResult(result, loading);
    $(".message-content", loading).removeAttribute("aria-live");
    resetAttachment();
    state.activeTurns += 1;
    $("#delete-chat-button").disabled = false;
    if (state.activeTurns === 1) $("#chat-title").textContent = conversationTitle(question);
    updateDesignLabels();
    updateMemoryStatus();
    updateEmptyState();
    try { await refreshChats(); } catch { toast("Answer saved, but the chat list could not refresh.", true); }
  } catch (error) {
    if (state.stopRequested || error.message === "Run stopped" || error.name === "AbortError") {
      loading?.remove();
      userNode?.remove();
      if (createdChatId) {
        try {
          await api(`/api/v1/chats/${encodeURIComponent(createdChatId)}`, { method: "DELETE" });
          clearChat();
          await refreshChats();
        } catch { /* Keep the chat if cleanup was already completed. */ }
      }
      $("#question-input").value = originalQuestion;
      toast("Run stopped. Your question is ready to retry.");
      return;
    }
    if (createdChatId && state.activeTurns === 0) {
      try {
        await api(`/api/v1/chats/${encodeURIComponent(createdChatId)}`, { method: "DELETE" });
        clearChat();
        $("#question-input").value = originalQuestion;
        if (attachment) {
          showAttachment(attachment);
        }
        await refreshChats();
        loading = null;
      } catch { /* Keep the conversation visible if cleanup fails. */ }
    }
    if (loading) {
      loading.className = "message assistant";
      $(".message-meta span", loading).textContent = "run failed safely";
      $(".message-content", loading).textContent = error.message;
      const retry = el("button", "", "Retry question");
      retry.type = "button";
      retry.addEventListener("click", () => {
        $("#question-input").value = originalQuestion;
        resizeComposer();
        $("#question-input").focus();
      });
      loading.append(retry);
    } else $("#question-input").value = question;
    toast(error.message, true);
  } finally {
    if (streamTimer) window.clearTimeout(streamTimer);
    if (state.allowWeb) {
      state.allowWeb = false;
      $("#allow-web-input").checked = false;
      syncHostedCapabilities();
      updateDesignLabels();
    }
    send.disabled = false;
    send.hidden = false;
    $("#stop-button").hidden = true;
    $("#stop-button").disabled = false;
    $("#stop-button").textContent = "Stop";
    state.runId = null;
    $("#active-run-count").hidden = true;
    renderHistoryList();
    state.runController = null;
    state.stopRequested = false;
    $$('[data-workflow]').forEach((button) => { button.disabled = false; });
    $("#mode-pill").disabled = false;
    $("#new-chat-button").disabled = false;
    $("#delete-chat-button").disabled = !state.activeChatId;
    resizeComposer();
    if (!phoneLayout()) $("#question-input").focus();
  }
}

async function loadSources() {
  if (!state.bootstrap) return;
  const list = $("#source-list");
  list.replaceChildren(el("p", "empty-list", "Loading authorized sources…"));
  try {
    const { collection, scopes } = currentContext();
    const query = new URLSearchParams({ collection });
    scopes.forEach((scope) => query.append("scope", scope));
    const result = await api(`/api/v1/sources?${query}`);
    state.sources = result.sources;
    renderSourceRows();
  } catch (error) {
    list.replaceChildren(el("p", "empty-list", error.message));
  }
}

function renderSourceRows() {
  const list = $("#source-list");
  list.replaceChildren();
  if (state.sourceFilter !== "all" && !state.sources.some((source) => source.logical_path.toLowerCase().endsWith(`.${state.sourceFilter}`))) state.sourceFilter = "all";
  $("#source-count").textContent = `${state.sources.length} source${state.sources.length === 1 ? "" : "s"}`;
  const filters = $("#source-filters");
  filters.replaceChildren();
  for (const type of ["all", "md", "pdf", "docx", "txt"]) {
    const count = type === "all" ? state.sources.length : state.sources.filter((source) => source.logical_path.toLowerCase().endsWith(`.${type}`)).length;
    if (!count && type !== "all") continue;
    const button = el("button", state.sourceFilter === type ? "is-active" : "", `${type === "all" ? "All" : type === "md" ? "Markdown" : type.toUpperCase()} ${count}`);
    button.type = "button";
    button.setAttribute("aria-pressed", String(state.sourceFilter === type));
    button.addEventListener("click", () => { state.sourceFilter = type; renderSourceRows(); });
    filters.append(button);
  }
  const visible = state.sources.filter((source) =>
    (state.sourceFilter === "all" || source.logical_path.toLowerCase().endsWith(`.${state.sourceFilter}`))
    && `${source.title || ""} ${source.logical_path}`.toLowerCase().includes(state.sourceQuery));
  if (!visible.length) list.append(el("p", "empty-list", state.sources.length ? "No sources match these filters." : "No authorized sources in this collection yet."));
  visible.forEach((source) => {
      const button = el("button", "source-row");
      button.type = "button";
      button.dataset.sourceId = source.id;
      const type = source.logical_path.split(".").pop().slice(0, 4);
      const copy = el("span");
      copy.append(el("strong", "", source.title || source.logical_path.split("/").pop()), el("small", "", `${source.logical_path.split("/").pop()} · ${type.toUpperCase()} · ${new Date(source.created_at).toLocaleDateString()}`));
      button.append(el("span", "source-type", type), copy, el("span", "source-size", formatBytes(source.byte_size)), el("span", "source-version", `v·${source.id.replace(/^version_/, "").slice(0, 8)}`), el("span", "source-status", "Indexed"));
      button.addEventListener("click", () => openSource(source.id));
      list.append(button);
  });
}

async function openSource(sourceId, citation = null) {
  try {
    const { scopes } = currentContext();
    const query = new URLSearchParams();
    scopes.forEach((scope) => query.append("scope", scope));
    const source = await api(`/api/v1/sources/${encodeURIComponent(sourceId)}?${query}`);
    if (!$("#view-corpus").hidden) {
      const preview = $("#source-preview");
      preview.hidden = false;
      preview.replaceChildren();
      const heading = el("div", "source-preview-heading");
      heading.append(el("strong", "", source.logical_path));
      const close = el("button", "icon-button", "×");
      close.type = "button";
      close.setAttribute("aria-label", "Close source preview");
      close.addEventListener("click", () => { preview.hidden = true; $(".corpus-layout").classList.remove("has-preview"); });
      heading.append(close);
      const content = el("div", "source-preview-content");
      const sourceText = source.text || "";
      if (citation && citation.source_version_id === source.id && Number.isInteger(citation.start_char) && Number.isInteger(citation.end_char) && citation.start_char >= 0 && citation.end_char <= sourceText.length && citation.end_char > citation.start_char) {
        content.classList.add("is-plain");
        content.append(document.createTextNode(plainDocument(sourceText.slice(0, citation.start_char))));
        content.append(el("mark", "cite-mark", plainDocument(sourceText.slice(citation.start_char, citation.end_char))));
        content.append(document.createTextNode(plainDocument(sourceText.slice(citation.end_char))));
      } else if (sourceText) {
        renderMarkdown(content, sourceText);
        const firstHeading = content.querySelector("h1");
        if (firstHeading?.textContent?.trim() === (source.title || "").trim()) firstHeading.remove();
      }
      else content.textContent = "No parsed text available.";
      const filename = source.logical_path.split("/").pop();
      const outline = el("nav", "source-outline");
      outline.setAttribute("aria-label", "Document outline");
      const matches = [...sourceText.matchAll(/^#{1,6}\s+(.+)$/gm)].slice(0, 30);
      if (matches.length) {
        outline.append(el("strong", "", "Outline"));
        matches.forEach((match, index) => {
          const item = el("button", "", `${index + 1}  ${match[1]}`);
          item.type = "button";
          item.addEventListener("click", () => {
            const target = content.querySelectorAll("h1,h2,h3,h4,h5,h6")[index];
            if (target) target.scrollIntoView({ block: "center", behavior: "smooth" });
            else content.scrollTop = content.scrollHeight * (match.index / Math.max(1, sourceText.length));
          });
          outline.append(item);
        });
      }
      const details = el("dl", "source-preview-details");
      [["Collection", source.collection], ["Access", source.scopes?.join(", ")], ["Parser", source.parser_id], ["Size", formatBytes(source.byte_size)], ["Version", source.id]].forEach(([term, value]) => details.append(el("dt", "", term), el("dd", "", value || "—")));
      const actions = el("div", "source-preview-actions");
      const ask = el("button", "secondary-button", "Ask about this source");
      ask.type = "button";
      ask.addEventListener("click", () => { clearChat(); setView("chat"); $("#question-input").value = `About ${filename}: `; resizeComposer(); $("#question-input").focus(); });
      const upload = el("button", "secondary-button", "Upload new version");
      upload.type = "button";
      upload.addEventListener("click", () => $("#file-input").click());
      actions.append(ask, upload);
      preview.append(heading, el("h2", "", source.title || filename), el("p", "source-preview-meta", `${source.media_type} · ${matches.length} sections · v·${source.id.replace(/^version_/, "").slice(0, 8)}${citation ? " · opened from citation" : ""}`));
      if (matches.length) preview.append(outline);
      preview.append(content, details, actions);
      $(".corpus-layout").classList.add("has-preview");
      $$(".source-row").forEach((row) => row.classList.toggle("is-selected", row.dataset.sourceId === sourceId));
      const highlight = $(".cite-mark", content);
      if (highlight) requestAnimationFrame(() => highlight.scrollIntoView({ block: "center" }));
      return;
    }
    $("#inspector-title").textContent = "Source version";
    const body = $("#inspector-body");
    body.replaceChildren();
    const detail = el("article", "source-detail");
    detail.append(el("h3", "", source.logical_path));
    const definitions = el("dl");
    [["Collection", source.collection], ["Parser", source.parser_id], ["Bytes", formatBytes(source.byte_size)], ["Version", source.id], ["Original SHA", source.sha256], ["Parsed SHA", source.parsed_sha256], ["Scopes", source.scopes.join(", ")]].forEach(([term, value]) => definitions.append(el("dt", "", term), el("dd", "", value)));
    detail.append(definitions, el("pre", "source-content", source.text || "No parsed text available."));
    body.append(detail);
    openInspector();
  } catch (error) {
    toast(error.message, true);
  }
}

function formatBytes(value) {
  if (!Number.isFinite(value)) return "—";
  if (value < 1024) return `${value} B`;
  if (value < 1024 ** 2) return `${(value / 1024).toFixed(1)} KiB`;
  return `${(value / 1024 ** 2).toFixed(1)} MiB`;
}

async function fileToBase64(file) {
  const bytes = new Uint8Array(await file.arrayBuffer());
  const chunkSize = 0x8000;
  let binary = "";
  for (let index = 0; index < bytes.length; index += chunkSize) {
    binary += String.fromCharCode(...bytes.subarray(index, index + chunkSize));
  }
  return btoa(binary);
}

async function ingestSelectedFile() {
  const file = state.selectedFile || $("#file-input").files[0];
  if (!file) throw new Error("Choose a source file first");
  const limit = state.bootstrap.ingestion.limits.max_file_bytes;
  if (file.size > limit) throw new Error(`File is ${formatBytes(file.size)}; the limit is ${formatBytes(limit)}`);
  const button = $("#upload-button");
  const message = $("#upload-message");
  button.disabled = true;
  message.className = "form-message";
  message.textContent = "Reading the file locally and sending it to the local workbench…";
  try {
    const context = currentContext();
    const result = await post("/api/v1/ingest", {
      filename: file.name,
      content_base64: await fileToBase64(file),
      ...context,
      ocr: $("#ocr-select").value,
    });
    message.className = "form-message is-success";
    message.textContent = `Published ${result.logical_path} as ${result.id}.`;
    state.selectedFile = null;
    $("#file-input").value = "";
    $("#selected-file-label").textContent = "Up to 50 MiB · processed locally";
    toast("Source ingested and indexed.");
    await loadSources();
    await refreshCorpusStatus();
  } catch (error) {
    message.className = "form-message is-error";
    message.textContent = error.message;
    throw error;
  } finally {
    button.disabled = false;
  }
}

function toast(message, isError = false) {
  const node = el("div", `toast${isError ? " is-error" : ""}`, message);
  $("#toast-region").append(node);
  window.setTimeout(() => node.remove(), 4800);
}

function bindEvents() {
  for (const target of [$("#chat-scroll"), $("#conversation"), $(".model-workspace"), $(".corpus-layout"), $(".capability-layout")]) {
    target.addEventListener("scroll", updateBackToTop, { passive: true });
  }
  $("#back-to-top").addEventListener("click", () => {
    state.followRunOutput = false;
    screenScroller()?.scrollTo({ top: 0, behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
  });
  window.addEventListener("resize", updateBackToTop);
  window.addEventListener("resize", () => setSidebarOpen(false));
  window.visualViewport?.addEventListener("resize", updateBackToTop);
  for (const target of [$("#chat-scroll"), $("#conversation")]) {
    for (const name of ["touchmove", "wheel"]) {
      target.addEventListener(name, () => {
        if (state.runId) state.followRunOutput = false;
      }, { passive: true });
    }
  }
  $("#mobile-context-toggle").addEventListener("click", (event) => {
    event.stopPropagation();
    setMobileContextOpen($("#mobile-context-fields").hidden);
  });
  for (const selector of [$("#project-select"), $("#mobile-project-select")]) {
    selector.addEventListener("change", (event) => void selectProject(event.target.value).catch((error) => toast(error.message, true)));
  }
  for (const button of [$("#new-project-button"), $("#mobile-new-project")]) {
    button.addEventListener("click", () => { setMobileContextOpen(false); $("#project-dialog").showModal(); $("#project-name").focus(); });
  }
  $("#cancel-project").addEventListener("click", () => $("#project-dialog").close());
  $$('[data-open-memory]').forEach((button) => button.addEventListener("click", () => void openMemoryDialog()));
  $("#close-memory").addEventListener("click", () => $("#memory-dialog").close());
  const speechAvailable = Boolean(window.SpeechRecognition || window.webkitSpeechRecognition);
  $("#dictate-button").hidden = !speechAvailable;
  $("#add-dictate-button").hidden = !speechAvailable;
  $("#chat-attachment-control").addEventListener("click", () => {
    toggleModeMenu(false);
    const menu = $("#composer-add-menu");
    menu.hidden = !menu.hidden;
    $("#chat-attachment-control").setAttribute("aria-expanded", String(!menu.hidden));
    if (!menu.hidden) $("#add-file-button").focus();
  });
  $("#add-file-button").addEventListener("click", () => {
    $("#composer-add-menu").hidden = true;
    $("#chat-attachment-control").setAttribute("aria-expanded", "false");
    $("#chat-document-input").click();
  });
  $("#add-image-button").addEventListener("click", () => {
    $("#composer-add-menu").hidden = true;
    $("#chat-attachment-control").setAttribute("aria-expanded", "false");
    $("#chat-image-input").click();
  });
  $("#add-dictate-button").addEventListener("click", () => {
    $("#composer-add-menu").hidden = true;
    $("#chat-attachment-control").setAttribute("aria-expanded", "false");
    $("#dictate-button").click();
  });
  $("#dictate-button").addEventListener("click", () => {
    if (state.voiceListening) {
      state.recognition?.stop();
      return;
    }
    if (localStorage.getItem("agenticrag.voiceConsent") === "1") startVoiceDictation();
    else $("#voice-dialog").showModal();
  });
  $("#cancel-voice").addEventListener("click", () => $("#voice-dialog").close());
  $("#start-voice").addEventListener("click", () => {
    $("#voice-dialog").close();
    localStorage.setItem("agenticrag.voiceConsent", "1");
    startVoiceDictation();
  });
  $("#cancel-memory-edit").addEventListener("click", () => {
    state.memoryEditingId = null;
    $("#memory-content").value = "";
    $("#memory-source-chat").value = "";
    $("#save-memory").textContent = "Save note";
    $("#cancel-memory-edit").hidden = true;
  });
  $("#memory-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      const content = $("#memory-content").value.trim();
      if (state.memoryEditingId) {
        await api(`/api/v1/project-notes/${state.memoryEditingId}`, {
          method: "PUT", body: JSON.stringify({ content }),
        });
      } else {
        await post(`/api/v1/projects/${state.activeProjectId}/notes`, {
          content, source_chat_id: $("#memory-source-chat").value || null,
        });
      }
      state.memoryEditingId = null;
      $("#memory-content").value = "";
      $("#memory-source-chat").value = "";
      $("#save-memory").textContent = "Save note";
      $("#cancel-memory-edit").hidden = true;
      await loadProjectMemory();
      toast("Project memory saved.");
    } catch (error) { toast(error.message, true); }
  });
  $("#project-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      const project = await post("/api/v1/projects", { name: $("#project-name").value.trim() });
      $("#project-dialog").close();
      $("#project-name").value = "";
      await refreshProjects();
      await selectProject(project.id);
      setView("chat");
      toast(`Created ${project.name}.`);
    } catch (error) { toast(error.message, true); }
  });
  for (const search of [$("#chat-search"), $("#mobile-chat-search")]) {
    search.addEventListener("input", (event) => {
      state.chatSearch = event.target.value.trim();
      $("#chat-search").value = event.target.value;
      $("#mobile-chat-search").value = event.target.value;
      void refreshChats().catch((error) => toast(error.message, true));
    });
  }
  $$("[data-view]").forEach((button) => button.addEventListener("click", () => setView(button.dataset.view)));
  $$("[data-open-view]").forEach((button) => button.addEventListener("click", () => setView(button.dataset.openView)));
  $("#composer-route").addEventListener("click", () => setView("models"));
  $("#refresh-evaluation").addEventListener("click", () => void refreshEvaluation());
  $$("[data-workflow]").forEach((button) => button.addEventListener("click", () => {
    state.workflow = button.dataset.workflow;
    updateSelectedSkills();
    $$("[data-workflow]").forEach((item) => item.classList.toggle("is-active", item === button));
    $$("[data-workflow]").forEach((item) => item.setAttribute("aria-checked", String(item === button)));
    $("#send-button span").textContent = state.workflow === "agent" ? "Run agent" : state.workflow === "supervisor" ? "Run team" : state.workflow === "fixed" ? "Ask RAG" : "Ask model";
    $("#send-button").setAttribute("aria-label", state.workflow === "agent" ? "Run agent" : state.workflow === "supervisor" ? "Run supervisor" : "Send question");
    syncHostedCapabilities();
    updateMemoryStatus();
    updateEmptyState();
    updateComposerRoute();
    updateDesignLabels();
    $("#mobile-writing-mode").textContent = `${$("#mode-pill-label").textContent} question`;
    toggleModeMenu(false);
  }));
  $("#new-chat-button").addEventListener("click", () => {
    clearChat();
    setView("chat");
    if (phoneLayout()) $("#question-input").focus();
  });
  $("#stop-button").addEventListener("click", async () => {
    if (!state.runId || state.stopRequested) return;
    state.stopRequested = true;
    $("#stop-button").disabled = true;
    $("#stop-button").textContent = "Stopping…";
    try { await post(`/api/v1/runs/${state.runId}/cancel`, {}); }
    catch { /* Aborting the response still stops this client run. */ }
    state.runController?.abort();
    $("#stop-button").textContent = "Stop";
  });
  $("#delete-chat-button").addEventListener("click", async () => {
    if (state.activeChatId) await deleteChat(state.activeChatId);
  });
  $("#sidebar-new-chat").addEventListener("click", () => { clearChat(); setView("chat"); });
  $("#mobile-chat-select").addEventListener("change", (event) => {
    if (event.target.value) void loadChat(event.target.value);
  });
  $$("[data-provider-form]").forEach((form) => form.addEventListener("submit", async (event) => {
    event.preventDefault();
    try { await configureProvider(form.dataset.providerForm, form); } catch { /* message is inline */ }
  }));
  $$("[data-runtime-select]").forEach((select) => select.addEventListener("change", () => applyRuntimeProfile(select.dataset.runtimeSelect, select.value)));
  $$("[data-probe]").forEach((button) => button.addEventListener("click", () => probeProvider(button.dataset.probe)));
  $("#contract-check-button").addEventListener("click", checkAgentContract);
  $("#active-contract-button").addEventListener("click", checkAgentContract);
  $("#active-embedding-change").addEventListener("click", () => { $("#connections-dialog").showModal(); $("[data-provider-form=embedding] input[name=model]").focus(); });
  $("#discover-models-button").addEventListener("click", discoverLocalModels);
  $$("[data-capability-tab]").forEach((button) => button.addEventListener("click", () => renderCapabilities(button.dataset.capabilityTab)));
  $$("[data-prompt]").forEach((button) => button.addEventListener("click", () => {
    $("#question-input").value = button.dataset.prompt;
    resizeComposer();
    $("#question-input").focus();
  }));
  $("#ask-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    if ($("#send-button").disabled) return;
    const input = $("#question-input");
    const question = input.value.trim();
    if (!question) return;
    input.value = "";
    resizeComposer();
    if (phoneLayout()) input.blur();
    try { await runQuestion(question); } catch (error) { toast(error.message, true); }
  });
  $("#send-button").addEventListener("pointerdown", (event) => {
    if (phoneLayout() && document.activeElement === $("#question-input") && $("#question-input").value.trim()) {
      event.preventDefault();
      $("#ask-form").requestSubmit();
    }
  });
  $("#question-input").addEventListener("input", resizeComposer);
  $("#question-input").addEventListener("focus", () => {
    if (phoneLayout()) {
      document.body.classList.add("is-composing");
      $("#mobile-chat-history").open = false;
      setMobileContextOpen(false);
      scrollChatToBottom();
    }
    updateMobileViewport();
  });
  $("#question-input").addEventListener("blur", () => {
    document.body.classList.remove("is-composing");
    updateMobileViewport();
  });
  $("#dismiss-keyboard").addEventListener("click", () => $("#question-input").blur());
  $("#question-input").addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey && !phoneLayout()) {
      event.preventDefault();
      $("#ask-form").requestSubmit();
    }
  });
  $("#skill-picker-button").addEventListener("click", () => {
    const picker = $("#skill-picker");
    picker.hidden = !picker.hidden;
    $("#skill-picker-button").setAttribute("aria-expanded", String(!picker.hidden));
  });
  $("#allow-web-input").addEventListener("change", (event) => {
    state.allowWeb = event.target.checked;
    syncHostedCapabilities();
    updateDesignLabels();
  });
  $("#chat-document-input").addEventListener("change", (event) => selectChatAttachment(event.target.files[0], "document"));
  $("#chat-image-input").addEventListener("change", (event) => selectChatAttachment(event.target.files[0], "image"));
  $("#remove-attachment").addEventListener("click", resetAttachment);
  document.addEventListener("click", (event) => {
    if (!event.target.closest("#chat-attachment-control") && !event.target.closest("#composer-add-menu")) {
      $("#composer-add-menu").hidden = true;
      $("#chat-attachment-control").setAttribute("aria-expanded", "false");
    }
    if (!event.target.closest("#skill-picker") && !event.target.closest("#skill-picker-button")) {
      $("#skill-picker").hidden = true;
      $("#skill-picker-button").setAttribute("aria-expanded", "false");
    }
    if (!event.target.closest("#mobile-context")) setMobileContextOpen(false);
    if (!event.target.closest("#mode-pill") && !event.target.closest("#workflow-options")) toggleModeMenu(false);
  });
  $("#theme-toggle").addEventListener("click", () => setTheme(document.documentElement.dataset.theme === "dark" ? "light" : "dark"));
  $("#collection-input").addEventListener("change", persistContext);
  $("#scope-input").addEventListener("change", persistContext);
  $("#collection-input").addEventListener("input", contextInputChanged);
  $("#scope-input").addEventListener("input", contextInputChanged);
  for (const [mobileId, desktopId] of [["mobile-collection-input", "collection-input"], ["mobile-scope-input", "scope-input"]]) {
    const mobile = $(`#${mobileId}`);
    const desktop = $(`#${desktopId}`);
    mobile.addEventListener("input", () => {
      desktop.value = mobile.value;
      contextInputChanged();
    });
    mobile.addEventListener("change", persistContext);
    desktop.addEventListener("input", () => { mobile.value = desktop.value; });
  }
  $("#refresh-button").addEventListener("click", initialize);
  $("#reload-sources").addEventListener("click", loadSources);
  $("#inspector-close").addEventListener("click", closeInspector);
  $("#inspector-backdrop").addEventListener("click", closeInspector);
  $("#source-search").addEventListener("input", (event) => { state.sourceQuery = event.target.value.trim().toLowerCase(); renderSourceRows(); });
  $("#add-source-button").addEventListener("click", () => $("#file-input").click());
  $("#file-input").addEventListener("change", (event) => {
    selectFile(event.target.files[0]);
    if (event.target.files[0]) void ingestSelectedFile().catch((error) => toast(error.message, true));
  });
  const dropZone = $("#drop-zone");
  dropZone.addEventListener("click", (event) => { if (event.target !== $("#file-input")) $("#file-input").click(); });
  ["dragenter", "dragover"].forEach((name) => dropZone.addEventListener(name, (event) => { event.preventDefault(); dropZone.classList.add("is-dragging"); }));
  ["dragleave", "drop"].forEach((name) => dropZone.addEventListener(name, (event) => { event.preventDefault(); dropZone.classList.remove("is-dragging"); }));
  dropZone.addEventListener("drop", (event) => {
    selectFile(event.dataTransfer.files[0]);
    if (event.dataTransfer.files[0]) void ingestSelectedFile().catch((error) => toast(error.message, true));
  });
  $("#upload-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    try { await ingestSelectedFile(); } catch (error) { toast(error.message, true); }
  });
  document.addEventListener("keydown", (event) => {
    if ((event.ctrlKey || event.metaKey) && ["1", "2", "3", "4"].includes(event.key)) {
      event.preventDefault();
      setView(["chat", "corpus", "models", "capabilities"][Number(event.key) - 1]);
    }
    if (event.key === "Escape") {
      toggleModeMenu(false);
      $("#composer-add-menu").hidden = true;
      $("#chat-attachment-control").setAttribute("aria-expanded", "false");
      setSidebarOpen(false);
      $("#skill-picker").hidden = true;
      setMobileContextOpen(false);
      closeInspector();
    }
  });
}

function selectFile(file) {
  if (!file) return;
  state.selectedFile = file;
  $("#selected-file-label").textContent = `${file.name} · ${formatBytes(file.size)}`;
}

async function initialize() {
  try {
    state.bootstrap = await api("/api/v1/bootstrap");
    $("#version-label").textContent = `AgenticRAG ${state.bootstrap.version}`;
    $("#collection-input").value = localStorage.getItem("agenticrag.collection") || $("#collection-input").value;
    $("#scope-input").value = localStorage.getItem("agenticrag.scopes") || $("#scope-input").value;
    $("#mobile-collection-input").value = $("#collection-input").value;
    $("#mobile-scope-input").value = $("#scope-input").value;
    await refreshProjects();
    $("#capability-count").textContent = String(capabilityTotal());
    $("#tool-count").textContent = String(state.bootstrap.capabilities.tools.length);
    $("#agent-count").textContent = String(state.bootstrap.capabilities.agents.length);
    $("#skill-count").textContent = String(state.bootstrap.capabilities.skills.length);
    $("#plugin-count").textContent = String(state.bootstrap.capabilities.plugins.length);
    hydrateModels();
    renderSkillPicker();
    syncHostedCapabilities();
    renderCapabilities(state.capabilityTab);
    renderReadiness();
    updateContextLabels();
    updateMemoryStatus();
    updateEmptyState();
    await refreshCorpusStatus();
    await refreshChats();
    const savedChatId = localStorage.getItem("agenticrag.activeChatId");
    if (savedChatId && state.chats.some((item) => item.id === savedChatId)) await loadChat(savedChatId);
    void discoverLocalModels();
    void refreshRuntimeStatus();
  } catch (error) {
    $("#readiness-label").textContent = "Workbench unavailable";
    toast(error.message, true);
  }
}

prepareDesignShell();
setTheme(localStorage.getItem("agenticrag.theme") || (matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark"));
bindEvents();
document.addEventListener("visibilitychange", () => { if (!document.hidden) void refreshRuntimeStatus(); });
window.setInterval(() => { if (!document.hidden) void refreshRuntimeStatus(); }, 60_000);
let viewportFrame = 0;
const scheduleMobileViewport = () => {
  window.cancelAnimationFrame(viewportFrame);
  viewportFrame = window.requestAnimationFrame(updateMobileViewport);
};
window.visualViewport?.addEventListener("resize", scheduleMobileViewport);
window.visualViewport?.addEventListener("scroll", scheduleMobileViewport);
window.addEventListener("resize", scheduleMobileViewport);
window.addEventListener("orientationchange", scheduleMobileViewport);
updateMobileViewport();
resizeComposer();
initialize();
