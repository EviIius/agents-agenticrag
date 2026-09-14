"use strict";

const state = {
  bootstrap: null,
  workflow: "agent",
  selectedSkills: new Set(),
  allowWeb: false,
  capabilityTab: "tools",
  selectedFile: null,
};

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

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
  updateContextLabels();
}

function updateContextLabels() {
  const collection = $("#collection-input").value.trim() || "no collection";
  const scopes = $("#scope-input").value.trim() || "no scope";
  $("#chat-context-label").textContent = `${collection} · ${scopes}`;
}

function setView(name) {
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
  if (name === "capabilities") renderCapabilities(state.capabilityTab);
  $("#workspace").focus({ preventScroll: true });
}

function setTheme(theme) {
  document.documentElement.dataset.theme = theme;
  localStorage.setItem("agenticrag.theme", theme);
  const toggle = $("#theme-toggle");
  toggle.setAttribute("aria-label", `Switch to ${theme === "dark" ? "light" : "dark"} theme`);
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

function saveProviderPreference(role, payload) {
  const safe = { ...payload };
  safe.credential_configured = Boolean(safe.api_key);
  delete safe.api_key;
  localStorage.setItem(`agenticrag.provider.${role}`, JSON.stringify(safe));
}

function readProviderPreference(role) {
  try {
    return JSON.parse(localStorage.getItem(`agenticrag.provider.${role}`) || "null");
  } catch {
    return null;
  }
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
    const preferred = readProviderPreference(role);
    const initial = preferred || (configured.configured === false ? null : configured);
    if (initial) fillProviderForm(role, initial);
    else applyRuntimeProfile(role, role === "chat" ? "lm-studio" : "ollama");
    if (configured.configured !== false) setProviderStatus(role, "ready", "Configured", configured.model);
  }

  const presets = $("#runtime-presets");
  presets.replaceChildren();
  state.bootstrap.runtimes.forEach((profile, index) => {
    const button = el("button", `preset-button${index === 0 ? " is-active" : ""}`);
    button.type = "button";
    button.dataset.preset = profile.id;
    button.append(el("strong", "", profile.name), el("span", "", profile.description));
    button.addEventListener("click", () => {
      $$(".preset-button").forEach((item) => item.classList.toggle("is-active", item === button));
      applyRuntimeProfile("chat", profile.id);
      applyRuntimeProfile("embedding", profile.id);
      toast(`${profile.name} defaults applied. Enter the model IDs, then connect.`);
    });
    presets.append(button);
  });
}

async function restoreProviderPreferences() {
  for (const role of ["chat", "embedding"]) {
    const preferred = readProviderPreference(role);
    if (!preferred) continue;
    if (preferred.credential_configured) {
      setProviderStatus(role, "idle", "Credential required");
      continue;
    }
    try {
      const result = await post("/api/v1/configure", { ...preferred, role, api_key: "" });
      state.bootstrap.providers[role] = result.provider;
      setProviderStatus(role, "ready", "Restored", result.provider.model);
    } catch {
      setProviderStatus(role, "error", "Preference invalid");
    }
  }
}

function setProviderStatus(role, status, label, model) {
  const badge = $(`[data-form-status="${role}"]`);
  badge.textContent = label;
  badge.dataset.state = status;
  const dot = $(`#${role}-status-dot`);
  dot.dataset.state = status;
  if (model) $(`#${role}-model-label`).textContent = model;
  renderReadiness();
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
    saveProviderPreference(role, payload);
    state.bootstrap.providers[role] = result.provider;
    syncHostedCapabilities();
    setProviderStatus(role, "ready", "Configured", result.provider.model);
    message.classList.add("is-success");
    message.textContent = "Connection selected for this workbench process.";
    if (!quiet) toast(`${role === "chat" ? "Chat" : "Embedding"} connection updated.`);
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
  $("#selected-skill-count").textContent = String(names.length);
  const summary = $("#selected-skills-summary");
  summary.textContent = names.length ? `Skills · ${names.join(" · ")}` : "No skills selected";
  summary.classList.toggle("has-skills", names.length > 0);
}

function capabilityTotal() {
  const capabilities = state.bootstrap.capabilities;
  return capabilities.tools.length + capabilities.agents.length + capabilities.skills.length + capabilities.plugins.length;
}

function syncHostedCapabilities() {
  if (!state.bootstrap) return;
  const chat = state.bootstrap.providers.chat;
  const available = chat.configured !== false && chat.provider_kind === "openai" && chat.credential_configured;
  const hosted = [state.bootstrap.providers.chat, state.bootstrap.providers.embedding]
    .some((provider) => provider.configured !== false && provider.provider_kind === "openai");
  const boundary = $("#boundary-badge");
  boundary.lastChild.textContent = hosted ? " Hosted provider enabled" : " Local boundary";
  boundary.dataset.hosted = String(hosted);
  const webTool = state.bootstrap.capabilities.tools.find((item) => item.id === "web_search");
  const webAgent = state.bootstrap.capabilities.agents.find((item) => item.id === "web_researcher");
  if (webTool) webTool.enabled = available;
  if (webAgent) webAgent.enabled = available;
  const input = $("#allow-web-input");
  input.disabled = !available || state.workflow !== "supervisor";
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
  const score = [chatReady, embeddingReady, storeReady, capabilityReady].filter(Boolean).length * 25;
  $("#readiness-ring").textContent = String(score);
  $("#readiness-label").textContent = score === 100 ? "Ready to run" : score >= 50 ? "Setup in progress" : "Needs setup";
  const list = $("#readiness-list");
  list.replaceChildren(
    readinessRow("Chat runtime", chatReady ? `${providers.chat.runtime} · ${providers.chat.model}` : "Choose a runtime and model in Models.", chatReady, !chatReady),
    readinessRow("Embedding runtime", embeddingReady ? `${providers.embedding.runtime} · ${providers.embedding.model}` : "Required for ingest and retrieval workflows.", embeddingReady, !embeddingReady),
    readinessRow("Corpus store", `${state.bootstrap.store.backend} · initialized on first use`, storeReady),
    readinessRow("Agent boundary", `${state.bootstrap.capabilities.tools.length} tools · ${state.bootstrap.capabilities.skills.length} skills`, capabilityReady),
  );
  $("#inspector-title").textContent = "Session readiness";
}

function appendMessage(kind, content, meta) {
  $("#chat-empty").hidden = true;
  const message = el("article", `message ${kind}`);
  const header = el("div", "message-meta");
  header.append(el("strong", "", kind === "user" ? "You" : "AgenticRAG"), el("span", "", meta || ""));
  message.append(header, el("div", "message-content", content));
  $("#conversation").append(message);
  $("#conversation").scrollTop = $("#conversation").scrollHeight;
  return message;
}

function appendLoading() {
  const message = appendMessage("assistant is-loading", "", "working within configured budgets");
  const content = $(".message-content", message);
  const dots = el("span", "thinking-dots");
  dots.append(el("i"), el("i"), el("i"));
  const progress = state.workflow === "agent"
    ? " Planning, retrieving, and reviewing…"
    : state.workflow === "supervisor"
      ? " Planning delegations, running specialists, and synthesizing…"
      : " Running workflow…";
  content.append(dots, document.createTextNode(progress));
  return message;
}

function renderResult(result, loading) {
  loading.className = "message assistant";
  $(".message-meta span", loading).textContent = result.abstained ? "abstained safely" : `${result.workflow.replaceAll("_", " ")} · ${result.elapsed_ms} ms`;
  const content = $(".message-content", loading);
  content.replaceChildren(document.createTextNode(result.answer));
  if (result.citations.length) {
    const citations = el("div", "citation-strip");
    result.citations.forEach((citation, index) => {
      const button = el("button", "citation-button", `${index + 1} · ${citation.logical_path}`);
      button.type = "button";
      button.addEventListener("click", () => openSource(citation.source_version_id));
      citations.append(button);
    });
    loading.append(citations);
  }
  if (result.external_sources && result.external_sources.length) {
    const sources = el("div", "citation-strip");
    result.external_sources.forEach((source) => {
      const link = el("a", "citation-button", source.title || source.url);
      link.href = source.url;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      sources.append(link);
    });
    loading.append(sources);
  }
  const summary = el("div", "run-summary");
  summary.append(
    el("span", "", `${result.evidence.length} evidence chunks`),
    el("span", "", `${(result.delegations || []).length} delegations`),
    el("span", "", `${result.events.length} events`),
  );
  const inspect = el("button", "", "Inspect trace →");
  inspect.type = "button";
  inspect.addEventListener("click", () => renderRunInspector(result));
  summary.append(inspect);
  loading.append(summary);
  renderRunInspector(result);
}

function humanEvent(event) {
  const labels = {
    plan_created: "Plan created",
    skill_loaded: "Skill loaded",
    tool_called: "Tool called",
    review_completed: "Evidence review",
    answer_validated: "Answer validated",
    retrieval_completed: "Retrieval completed",
    generation_completed: "Generation completed",
    abstained: "Safe abstention",
    budget_exhausted: "Budget exhausted",
    delegation_started: "Delegation started",
    delegation_completed: "Delegation completed",
    web_search_completed: "Hosted web search",
    synthesis_completed: "Supervisor synthesis",
    failed: "Run failed",
  };
  return labels[event.kind] || event.kind.replaceAll("_", " ");
}

function renderRunInspector(result) {
  $("#inspector-title").textContent = "Run trace";
  const body = $("#inspector-body");
  body.replaceChildren();
  const trace = el("div", "trace-list");
  result.events.forEach((event) => {
    const item = el("div", "trace-item");
    item.append(el("strong", "", humanEvent(event)), el("p", "", Object.entries(event.detail).map(([key, value]) => `${key}: ${value}`).join(" · ") || "Completed"));
    trace.append(item);
  });
  body.append(trace);
  if (result.delegations && result.delegations.length) {
    body.append(el("p", "eyebrow", "Specialist reports"));
    result.delegations.forEach((delegation) => {
      const preview = el("div", "evidence-preview");
      preview.append(
        el("strong", "", `${delegation.agent.replaceAll("_", " ")} · ${delegation.status}`),
        el("p", "", delegation.summary),
      );
      body.append(preview);
    });
  }
  if (result.evidence.length) {
    body.append(el("p", "eyebrow", "Retained evidence"));
    result.evidence.slice(0, 8).forEach((item) => {
      const preview = el("div", "evidence-preview");
      preview.append(el("strong", "", item.chunk.logical_path), el("p", "", item.chunk.text));
      body.append(preview);
    });
  }
  $(".inspector").classList.add("is-open");
}

async function runQuestion(question) {
  const context = currentContext();
  appendMessage("user", question, `${context.collection} · ${context.scopes.join(", ")}`);
  const loading = appendLoading();
  const send = $("#send-button");
  send.disabled = true;
  try {
    const result = await post("/api/v1/ask", {
      question,
      ...context,
      workflow: state.workflow,
      skills: [...state.selectedSkills],
      max_steps: 8,
      allow_web: state.workflow === "supervisor" && state.allowWeb,
    });
    renderResult(result, loading);
  } catch (error) {
    loading.className = "message assistant";
    $(".message-meta span", loading).textContent = "run failed safely";
    $(".message-content", loading).textContent = error.message;
    toast(error.message, true);
  } finally {
    send.disabled = false;
    $("#question-input").focus();
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
    list.replaceChildren();
    $("#source-count").textContent = `${result.sources.length} source${result.sources.length === 1 ? "" : "s"}`;
    if (!result.sources.length) list.append(el("p", "empty-list", "No authorized sources in this collection yet."));
    result.sources.forEach((source) => {
      const button = el("button", "source-row");
      button.type = "button";
      const type = source.logical_path.split(".").pop().slice(0, 4);
      const copy = el("span");
      copy.append(el("strong", "", source.logical_path), el("small", "", `${source.parser_id} · ${source.id.slice(0, 17)}`));
      button.append(el("span", "source-type", type), copy, el("span", "source-size", formatBytes(source.byte_size)));
      button.addEventListener("click", () => openSource(source.id));
      list.append(button);
    });
  } catch (error) {
    list.replaceChildren(el("p", "empty-list", error.message));
  }
}

async function openSource(sourceId) {
  try {
    const { scopes } = currentContext();
    const query = new URLSearchParams();
    scopes.forEach((scope) => query.append("scope", scope));
    const source = await api(`/api/v1/sources/${encodeURIComponent(sourceId)}?${query}`);
    $("#inspector-title").textContent = "Source version";
    const body = $("#inspector-body");
    body.replaceChildren();
    const detail = el("article", "source-detail");
    detail.append(el("h3", "", source.logical_path));
    const definitions = el("dl");
    [["Collection", source.collection], ["Parser", source.parser_id], ["Bytes", formatBytes(source.byte_size)], ["Version", source.id], ["Original SHA", source.sha256], ["Parsed SHA", source.parsed_sha256], ["Scopes", source.scopes.join(", ")]].forEach(([term, value]) => definitions.append(el("dt", "", term), el("dd", "", value)));
    detail.append(definitions, el("pre", "source-content", source.text || "No parsed text available."));
    body.append(detail);
    $(".inspector").classList.add("is-open");
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
  $$("[data-view]").forEach((button) => button.addEventListener("click", () => setView(button.dataset.view)));
  $$("[data-open-view]").forEach((button) => button.addEventListener("click", () => setView(button.dataset.openView)));
  $$("[data-workflow]").forEach((button) => button.addEventListener("click", () => {
    state.workflow = button.dataset.workflow;
    $$("[data-workflow]").forEach((item) => item.classList.toggle("is-active", item === button));
    $("#send-button span").textContent = state.workflow === "agent" ? "Run agent" : state.workflow === "supervisor" ? "Run team" : state.workflow === "fixed" ? "Ask RAG" : "Ask model";
    syncHostedCapabilities();
  }));
  $$("[data-provider-form]").forEach((form) => form.addEventListener("submit", async (event) => {
    event.preventDefault();
    try { await configureProvider(form.dataset.providerForm, form); } catch { /* message is inline */ }
  }));
  $$("[data-runtime-select]").forEach((select) => select.addEventListener("change", () => applyRuntimeProfile(select.dataset.runtimeSelect, select.value)));
  $$("[data-probe]").forEach((button) => button.addEventListener("click", () => probeProvider(button.dataset.probe)));
  $("#contract-check-button").addEventListener("click", checkAgentContract);
  $$("[data-capability-tab]").forEach((button) => button.addEventListener("click", () => renderCapabilities(button.dataset.capabilityTab)));
  $$("[data-prompt]").forEach((button) => button.addEventListener("click", () => {
    $("#question-input").value = button.dataset.prompt;
    $("#question-input").focus();
  }));
  $("#ask-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const input = $("#question-input");
    const question = input.value.trim();
    if (!question) return;
    input.value = "";
    try { await runQuestion(question); } catch (error) { toast(error.message, true); }
  });
  $("#question-input").addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
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
  });
  document.addEventListener("click", (event) => {
    if (!event.target.closest("#skill-picker") && !event.target.closest("#skill-picker-button")) {
      $("#skill-picker").hidden = true;
      $("#skill-picker-button").setAttribute("aria-expanded", "false");
    }
  });
  $("#theme-toggle").addEventListener("click", () => setTheme(document.documentElement.dataset.theme === "dark" ? "light" : "dark"));
  $("#collection-input").addEventListener("change", persistContext);
  $("#scope-input").addEventListener("change", persistContext);
  $("#refresh-button").addEventListener("click", initialize);
  $("#reload-sources").addEventListener("click", loadSources);
  $("#inspector-close").addEventListener("click", () => $(".inspector").classList.remove("is-open"));
  $("#file-input").addEventListener("change", (event) => selectFile(event.target.files[0]));
  const dropZone = $("#drop-zone");
  ["dragenter", "dragover"].forEach((name) => dropZone.addEventListener(name, (event) => { event.preventDefault(); dropZone.classList.add("is-dragging"); }));
  ["dragleave", "drop"].forEach((name) => dropZone.addEventListener(name, (event) => { event.preventDefault(); dropZone.classList.remove("is-dragging"); }));
  dropZone.addEventListener("drop", (event) => selectFile(event.dataTransfer.files[0]));
  $("#upload-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    try { await ingestSelectedFile(); } catch (error) { toast(error.message, true); }
  });
  document.addEventListener("keydown", (event) => {
    if ((event.ctrlKey || event.metaKey) && ["1", "2", "3", "4"].includes(event.key)) {
      event.preventDefault();
      setView(["chat", "models", "corpus", "capabilities"][Number(event.key) - 1]);
    }
    if (event.key === "Escape") {
      $("#skill-picker").hidden = true;
      $(".inspector").classList.remove("is-open");
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
    $("#capability-count").textContent = String(capabilityTotal());
    $("#tool-count").textContent = String(state.bootstrap.capabilities.tools.length);
    $("#agent-count").textContent = String(state.bootstrap.capabilities.agents.length);
    $("#skill-count").textContent = String(state.bootstrap.capabilities.skills.length);
    $("#plugin-count").textContent = String(state.bootstrap.capabilities.plugins.length);
    hydrateModels();
    await restoreProviderPreferences();
    renderSkillPicker();
    syncHostedCapabilities();
    renderCapabilities(state.capabilityTab);
    renderReadiness();
    updateContextLabels();
  } catch (error) {
    $("#readiness-label").textContent = "Workbench unavailable";
    toast(error.message, true);
  }
}

setTheme(localStorage.getItem("agenticrag.theme") || (matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark"));
bindEvents();
initialize();
