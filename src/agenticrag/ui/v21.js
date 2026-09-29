/* Appearance, connection presentation, and offline behavior. No build step. */
(() => {
  const appearance = window.ragAppearance;
  const settings = appearance.settings;
  const byId = (id) => document.getElementById(id);
  const dialog = byId("settings-dialog");
  const content = byId("settings-content");
  const sections = ["General", "Appearance", "Models", "Tools & agents", "Privacy", "About"];
  let currentSection = "appearance";
  let opener = null;

  function persistAppearance() {
    try { localStorage.setItem("agenticrag.appearance", JSON.stringify(settings)); } catch { /* private mode */ }
    appearance.apply();
    renderSettings();
  }
  function swatch(theme) {
    const paint = (value) => `<span class="theme-swatch" data-theme="${value}" data-accent="${settings.accent}"><span class="sw-side"></span><span class="sw-body"><span class="sw-line is-strong"></span><span class="sw-line"></span><span class="sw-cite"></span><span class="sw-button"></span></span></span>`;
    return theme === "system" ? `<span class="theme-swatch is-split">${paint(settings.light)}${paint(settings.dark)}</span>` : paint(theme);
  }
  function segment(key, values) {
    return `<div class="seg" role="group" aria-label="${key}">${values.map(([value, label]) => `<button class="seg-option" type="button" data-appearance-key="${key}" data-value="${value}" aria-pressed="${settings[key] === value}">${label}</button>`).join("")}</div>`;
  }
  function choice(key, value, label) {
    return `<button type="button" class="theme-card" data-appearance-key="${key}" data-value="${value}" aria-pressed="${settings[key] === value}">${swatch(value)}<span>${label}</span></button>`;
  }
  function renderSettings() {
    byId("settings-title").textContent = sections.find((name) => name.toLowerCase().replace(" & agents", "") === currentSection) || currentSection[0].toUpperCase() + currentSection.slice(1);
    document.querySelectorAll("[data-settings-section]").forEach((button) => {
      if (button.dataset.settingsSection === currentSection) button.setAttribute("aria-current", "page");
      else button.removeAttribute("aria-current");
    });
    if (currentSection === "appearance") {
      const dark = matchMedia("(prefers-color-scheme: dark)").matches;
      content.innerHTML = `
        <section class="settings-section"><h3>Theme</h3>
          <div class="theme-grid">${choice("theme", "system", "System")}${choice("theme", "dark", "Graphite Dark")}${choice("theme", "light", "Graphite Light")}${choice("theme", "midnight", "Midnight")}${choice("theme", "paper", "Paper")}</div>
          ${settings.theme === "system" ? `<div class="system-pickers"><label>Light appearance ${segment("light", [["light", "Graphite Light"], ["paper", "Paper"]])}</label><label>Dark appearance ${segment("dark", [["dark", "Graphite Dark"], ["midnight", "Midnight"]])}</label><p>This device is ${dark ? "dark" : "light"} right now, so you're seeing ${dark ? settings.dark === "dark" ? "Graphite Dark" : "Midnight" : settings.light === "light" ? "Graphite Light" : "Paper"}.</p></div>` : ""}
        </section>
        <section class="settings-section"><h3>Accent</h3><div class="accent-options">${["cobalt", "amber", "graphite"].map((value) => `<button class="accent-option" type="button" data-appearance-key="accent" data-value="${value}" aria-pressed="${settings.accent === value}"><span class="accent-dot" data-accent="${value}" data-theme="${document.documentElement.dataset.theme}"></span>${value[0].toUpperCase() + value.slice(1)}</button>`).join("")}</div></section>
        <section class="settings-section"><h3>Fonts</h3><div class="font-choice-row"><span>Interface</span>${segment("fontUi", [["geist", "Geist"], ["atkinson", "Atkinson Hyperlegible"], ["system", "System"]])}</div><div class="font-choice-row"><span>Answers</span>${segment("fontRead", [["newsreader", "Newsreader"], ["literata", "Literata"], ["geist", "Geist"], ["atkinson", "Atkinson"]])}${segment("textSize", [["s", "S"], ["m", "M"], ["l", "L"]])}</div><div class="font-preview"><span class="settings-label">Preview</span><span class="read">A useful answer should make its evidence easy to find. <span class="citation-pill">1</span></span></div></section>
        <section class="settings-section"><h3>Accessibility &amp; launch</h3>
          <div class="setting-row"><span class="setting-text"><strong>Increase contrast</strong><span class="setting-hint">Follow your device unless you choose otherwise.</span></span><button class="switch" role="switch" type="button" data-toggle="contrast" aria-label="Increase contrast" aria-checked="${document.documentElement.dataset.contrast === "more"}"></button></div>
          <div class="setting-row"><span class="setting-text"><strong>Reduce motion</strong><span class="setting-hint">Follow your device, or reduce motion here.</span></span><button class="switch" role="switch" type="button" data-toggle="motion" aria-label="Reduce motion" aria-checked="${settings.motion === "reduce"}"></button></div>
          <label>Launch intro ${segment("intro", [["always", "Every launch"], ["slow", "Only when slow"], ["off", "Off"]])}</label>
        </section>`;
    } else if (currentSection === "privacy") {
      const enabled = localStorage.getItem("agenticrag.offlineChats") !== "0";
      content.innerHTML = `<section class="settings-section"><h3>On this device</h3><div class="setting-row"><span class="setting-text"><strong>Keep chats readable offline on this device</strong><span class="setting-hint">A copy of recent chats is saved in this browser.</span></span><button class="switch" role="switch" type="button" id="offline-cache-toggle" aria-label="Keep chats readable offline on this device" aria-checked="${enabled}"></button></div><button class="secondary-button" type="button" id="clear-offline-copy">Clear offline copy</button></section>`;
    } else {
      const target = { models: "models", tools: "capabilities" }[currentSection];
      if (currentSection === "models") {
        const warm = localStorage.getItem("agenticrag.warmOnLaunch") !== "0";
        content.innerHTML = `<section class="settings-section"><h3>Models</h3><div class="setting-row"><span class="setting-text"><strong>Warm up the model when the app opens</strong><span class="setting-hint">Loads the selected local chat model before your first answer.</span></span><button class="switch" role="switch" type="button" id="warm-model-toggle" aria-label="Warm up the model when the app opens" aria-checked="${warm}"></button></div><button class="primary-button" id="open-settings-view" type="button">Open Models</button></section>`;
        return;
      }
      content.innerHTML = `<section class="settings-section"><h3>${currentSection === "general" ? "General" : currentSection === "about" ? "About AgenticRAG" : currentSection === "tools" ? "Tools & agents" : "Models"}</h3><p>${target ? "Open the workspace to manage these settings." : currentSection === "about" ? "Your private workbench on your Mac mini." : "Your projects and conversations are managed in the workspace."}</p>${target ? `<button class="primary-button" id="open-settings-view" type="button">Open ${currentSection === "tools" ? "Tools & agents" : "Models"}</button>` : ""}</section>`;
    }
  }
  content.addEventListener("click", async (event) => {
    const selected = event.target.closest("[data-appearance-key]");
    if (selected) { settings[selected.dataset.appearanceKey] = selected.dataset.value; persistAppearance(); return; }
    const toggle = event.target.closest("[data-toggle]");
    if (toggle) { const key = toggle.dataset.toggle; settings[key] = settings[key] === (key === "contrast" ? "more" : "reduce") ? (key === "contrast" ? "normal" : "auto") : (key === "contrast" ? "more" : "reduce"); persistAppearance(); return; }
    if (event.target.id === "offline-cache-toggle") {
      const enabled = event.target.getAttribute("aria-checked") !== "true";
      localStorage.setItem("agenticrag.offlineChats", enabled ? "1" : "0");
      event.target.setAttribute("aria-checked", String(enabled));
      navigator.serviceWorker?.controller?.postMessage({ type: "offline-chats", enabled });
      return;
    }
    if (event.target.id === "clear-offline-copy") {
      navigator.serviceWorker?.controller?.postMessage({ type: "clear-offline-copy" });
      toast({ kind: "success", title: "Offline copy cleared" });
      return;
    }
    if (event.target.id === "warm-model-toggle") {
      const enabled = event.target.getAttribute("aria-checked") !== "true";
      localStorage.setItem("agenticrag.warmOnLaunch", enabled ? "1" : "0");
      event.target.setAttribute("aria-checked", String(enabled));
      return;
    }
    if (event.target.id === "open-settings-view") { dialog.close(); setView(currentSection === "tools" ? "capabilities" : "models"); }
  });
  function openSettings(section = "appearance", invoker = document.activeElement) {
    if (document.querySelector("dialog[open]")) return;
    opener = invoker;
    currentSection = section;
    renderSettings();
    dialog.showModal();
    dialog.classList.remove("is-section-list");
    if (matchMedia("(max-width: 640px)").matches) { dialog.classList.add("is-section-list"); byId("settings-title").textContent = "Settings"; }
  }
  byId("theme-toggle").addEventListener("click", (event) => openSettings("appearance", event.currentTarget));
  byId("settings-close").addEventListener("click", () => dialog.close());
  byId("settings-back").addEventListener("click", () => { dialog.classList.add("is-section-list"); byId("settings-title").textContent = "Settings"; });
  dialog.addEventListener("close", () => opener?.focus());
  dialog.querySelectorAll("[data-settings-section]").forEach((button) => button.addEventListener("click", () => {
    currentSection = button.dataset.settingsSection; renderSettings(); dialog.classList.remove("is-section-list");
  }));
  byId("settings-mobile-sections").innerHTML = sections.map((name) => `<button type="button" data-mobile-section="${name.toLowerCase().replace(" & agents", "")}">${name}<span>›</span></button>`).join("");
  byId("settings-mobile-sections").addEventListener("click", (event) => {
    const button = event.target.closest("[data-mobile-section]");
    if (!button) return;
    currentSection = button.dataset.mobileSection; renderSettings(); dialog.classList.remove("is-section-list");
  });
  document.addEventListener("keydown", (event) => {
    if ((event.metaKey || event.ctrlKey) && event.key === ",") { event.preventDefault(); openSettings(); }
  });
  ["(prefers-color-scheme: dark)", "(prefers-contrast: more)"].forEach((query) => matchMedia(query).addEventListener("change", () => { appearance.apply(); if (dialog.open) renderSettings(); }));

  window.confirmDialog = ({ title, body, confirmLabel = "Confirm", danger = false }) => new Promise((resolve) => {
    const modal = byId("confirm-dialog");
    if (modal.open) return resolve(false);
    const invoker = document.activeElement;
    byId("confirm-title").textContent = title;
    byId("confirm-body").textContent = body;
    byId("confirm-accept").textContent = confirmLabel;
    byId("confirm-accept").classList.toggle("btn-danger", danger);
    let answer = false;
    const accept = () => { answer = true; modal.close(); };
    const cancel = () => modal.close();
    const complete = () => {
      byId("confirm-accept").removeEventListener("click", accept);
      byId("confirm-cancel").removeEventListener("click", cancel);
      invoker?.focus(); resolve(answer);
    };
    byId("confirm-accept").addEventListener("click", accept);
    byId("confirm-cancel").addEventListener("click", cancel);
    modal.addEventListener("close", complete, { once: true });
    modal.showModal(); byId("confirm-cancel").focus();
  });

  /* Prepared for the agent's future waiting_for_user events. No model text controls permissions. */
  let pendingQuestion = null;
  function showToolApproval(request, onDecision) {
    if (document.querySelector("dialog[open]")) return null;
    const card = document.createElement("div"); card.className = "agent-question approval-inline";
    const label = document.createElement("strong"); label.textContent = "The agent is waiting for approval";
    const summary = document.createElement("p"); summary.textContent = `${request.tool || "Tool"} · ${request.argumentsSummary || "Review the requested action"}`;
    const reopen = document.createElement("button"); reopen.type = "button"; reopen.className = "secondary-button"; reopen.textContent = "Review request";
    card.append(label, summary, reopen);
    byId("conversation").append(card);
    const modal = document.createElement("dialog"); modal.className = "rag-dialog as-sheet";
    const heading = document.createElement("h2"); heading.className = "dialog-title"; heading.textContent = "Allow this tool action?";
    const meta = document.createElement("p"); meta.className = "approval-meta"; meta.textContent = `${request.workflow || "Agentic"} run · step ${request.step || "?"} of ${request.maxSteps || "?"}`;
    const call = document.createElement("div"); call.className = "approval-call";
    const tool = document.createElement("strong"); tool.className = "tool"; tool.textContent = request.tool || "Tool";
    const args = document.createElement("span"); args.textContent = request.argumentsSummary || "";
    call.append(tool, args);
    const purpose = document.createElement("p"); purpose.className = "dialog-body"; purpose.textContent = request.purpose ? `Reason given: “${String(request.purpose).slice(0, 180)}”` : "";
    const egress = document.createElement("p"); egress.className = "approval-note"; egress.textContent = request.hostEgressSummary || "Review what this action sends before allowing it.";
    const actions = document.createElement("div"); actions.className = "dialog-actions";
    const decide = (value) => { modal.close(); card.remove(); onDecision(value); };
    const deny = document.createElement("button"); deny.type = "button"; deny.className = "secondary-button"; deny.textContent = "Deny"; deny.addEventListener("click", () => decide("deny"));
    const once = document.createElement("button"); once.type = "button"; once.className = "primary-button"; once.textContent = "Allow once"; once.addEventListener("click", () => decide("once"));
    actions.append(deny);
    if (request.allowAlways && request.site) {
      const always = document.createElement("button"); always.type = "button"; always.className = "secondary-button"; always.textContent = `Always for ${request.site}`; always.addEventListener("click", () => decide("always")); actions.append(always);
    }
    actions.append(once);
    modal.append(heading, meta, call, purpose, egress, actions);
    document.body.append(modal);
    modal.addEventListener("close", () => { if (!card.isConnected) modal.remove(); });
    reopen.addEventListener("click", () => { if (!modal.open) modal.showModal(); deny.focus(); });
    modal.showModal(); deny.focus();
    return card;
  }
  function showAgentQuestion(question, onAnswer) {
    if (pendingQuestion) return null;
    const card = document.createElement("section"); card.className = "agent-question"; card.tabIndex = 0;
    const header = document.createElement("strong"); header.textContent = "The agent has a question";
    const paused = document.createElement("span"); paused.className = "chip-paused"; paused.textContent = "Paused";
    const prompt = document.createElement("p"); prompt.className = "q"; prompt.textContent = question.text || "";
    card.append(header, paused, prompt);
    const answer = (value) => { pendingQuestion = null; byId("question-input").placeholder = "Ask a follow-up…"; card.remove(); onAnswer(value); };
    (question.choices || []).slice(0, 4).forEach((value, index) => {
      const button = document.createElement("button"); button.type = "button"; button.className = "choice"; button.textContent = `${index + 1}. ${value}`; button.addEventListener("click", () => answer(value)); card.append(button);
    });
    const footer = document.createElement("small"); footer.textContent = `${question.stepsUsed || 0} of ${question.maxSteps || 8} steps used. The run waits for your answer.`; card.append(footer);
    card.addEventListener("keydown", (event) => { const n = Number(event.key); if (n >= 1 && n <= (question.choices || []).length && n <= 4) { event.preventDefault(); answer(question.choices[n - 1]); } });
    byId("conversation").append(card); card.focus();
    byId("question-input").placeholder = "Answer the agent…";
    pendingQuestion = answer;
    return card;
  }
  byId("ask-form").addEventListener("submit", (event) => {
    if (!pendingQuestion) return;
    event.preventDefault(); event.stopImmediatePropagation();
    const value = byId("question-input").value.trim();
    if (value) { byId("question-input").value = ""; pendingQuestion(value); }
  }, true);
  window.ragPopups = { showToolApproval, showAgentQuestion };

  const tooltip = document.createElement("div");
  tooltip.id = "rag-tooltip";
  tooltip.className = "tooltip";
  tooltip.hidden = true;
  document.body.append(tooltip);
  let tooltipTimer = null;
  const hideTooltip = () => { clearTimeout(tooltipTimer); tooltip.hidden = true; };
  document.addEventListener("pointerover", (event) => {
    if (event.pointerType === "touch") return;
    const target = event.target.closest?.("[data-tooltip]");
    if (!target) return;
    hideTooltip();
    tooltipTimer = setTimeout(() => {
      tooltip.textContent = target.dataset.tooltip;
      const box = target.getBoundingClientRect();
      tooltip.style.setProperty("left", `${Math.min(window.innerWidth - 220, Math.max(8, box.left))}px`);
      tooltip.style.setProperty("top", `${box.bottom + 8}px`);
      tooltip.hidden = false;
    }, 400);
  });
  document.addEventListener("pointerout", (event) => { if (event.target.closest?.("[data-tooltip]")) hideTooltip(); });
  document.addEventListener("focusin", (event) => {
    const target = event.target.closest?.("[data-tooltip]");
    if (!target) return;
    hideTooltip(); tooltipTimer = setTimeout(() => { tooltip.textContent = target.dataset.tooltip; const box = target.getBoundingClientRect(); tooltip.style.setProperty("left", `${Math.max(8, box.left)}px`); tooltip.style.setProperty("top", `${box.bottom + 8}px`); tooltip.hidden = false; }, 400);
  });
  document.addEventListener("focusout", hideTooltip);

  let connection = "checking";
  let failureCount = 0;
  let offlineSince = 0;
  let retryTimer = null;
  let retrySeconds = 8;
  let lastAttempt = null;
  let lastRuntime = null;
  let warmStartedAt = 0;
  let offlineChatId = localStorage.getItem("agenticrag.activeChatId") || "new";
  const runtimeName = (id) => ({ "lm-studio": "LM Studio", ollama: "Ollama", "llama-cpp": "llama.cpp", vllm: "vLLM", openai: "OpenAI" }[id] || "Model runtime");
  const fetchJson = async (path, timeout = 4000) => {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeout);
    try {
      const response = await fetch(path, { signal: controller.signal, cache: "no-store" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return response.json();
    } finally { clearTimeout(timer); }
  };
  function launchRow(id, stateName, detail, name) {
    const row = byId(id); row.dataset.state = stateName;
    row.querySelector(".detail").textContent = detail;
    if (name) row.querySelector(".name").textContent = name;
  }
  const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
  function hideLaunch() {
    const node = byId("launch");
    node.classList.add("is-leaving");
    setTimeout(() => { document.documentElement.removeAttribute("data-launch"); node.classList.remove("is-leaving"); }, 320);
  }
  function showOffline(kind) {
    if (!offlineSince) offlineSince = Date.now();
    connection = kind;
    if (kind === "device_offline") hideLaunch();
    const phone = matchMedia("(max-width: 640px)").matches;
    byId("offline-title").textContent = kind === "device_offline" ? (phone ? "This phone is offline" : "This device is offline") : "Your Mac mini isn't answering";
    byId("offline-description").textContent = kind === "device_offline" ? "Connect this device to the internet or your tailnet to continue." : "Check your Mac mini and Tailscale connection. Chats saved on this device remain readable.";
    byId("offline-screen").hidden = false;
    byId("offline-screen").classList.toggle("is-device-offline", kind === "device_offline");
    const detail = byId("offline-details");
    detail.replaceChildren();
    for (const [label, value] of [["Address", location.host], ["Last attempt", lastAttempt ? lastAttempt.toLocaleTimeString() : "not yet"], ["This device", navigator.onLine ? "online" : "offline"], ["Retry", `${retrySeconds} s`]]) {
      const dt = document.createElement("dt"); dt.textContent = label;
      const dd = document.createElement("dd"); dd.textContent = value;
      detail.append(dt, dd);
    }
    byId("offline-check-list").replaceChildren(...(kind === "device_offline" ? ["Turn on Wi-Fi or cellular data.", "Reconnect to your tailnet."] : ["Check that your Mac mini is awake and powered on.", "Check Tailscale on both devices.", "Check that AgenticRAG is running."]).map((value) => { const li = document.createElement("li"); li.textContent = value; return li; }));
    void loadOfflineChats();
    try { byId("offline-draft").value = JSON.parse(localStorage.getItem("agenticrag.drafts") || "{}")[offlineChatId] || ""; } catch { /* private mode */ }
    scheduleRetry();
  }
  async function hideOffline() {
    if (!offlineSince) return;
    const duration = Math.max(1, Math.round((Date.now() - offlineSince) / 60000));
    offlineSince = 0; failureCount = 0;
    clearTimeout(retryTimer);
    byId("offline-screen").hidden = true;
    const draft = byId("offline-draft").value;
    toast({ kind: "success", title: "Back online", detail: `Mac mini reconnected after ${duration} min` });
    await initialize();
    if (offlineChatId !== "new" && state.chats.some((item) => item.id === offlineChatId)) await loadChat(offlineChatId);
    if (draft && !byId("question-input").value) { byId("question-input").value = draft; resizeComposer(); }
  }
  function scheduleRetry() {
    clearTimeout(retryTimer);
    const seconds = retrySeconds;
    byId("offline-retry-label").textContent = `Trying again in ${seconds} s`;
    retryTimer = setTimeout(() => { retrySeconds = seconds === 8 ? 16 : 30; void checkConnection(true); }, seconds * 1000);
  }
  async function loadOfflineChats() {
    const list = byId("offline-chat-list"); list.replaceChildren();
    try {
      const collection = localStorage.getItem("agenticrag.collection") || "research";
      const result = await fetchJson(`/api/v1/chats?collection=${encodeURIComponent(collection)}`, 1500);
      result.chats.forEach((chat) => {
        const button = document.createElement("button"); button.type = "button"; button.textContent = chat.title;
        button.addEventListener("click", async () => {
          try {
            offlineChatId = chat.id;
            byId("offline-draft").value = JSON.parse(localStorage.getItem("agenticrag.drafts") || "{}")[offlineChatId] || "";
            const detail = await fetchJson(`/api/v1/chats/${chat.id}`, 1500);
            byId("offline-chat-detail").replaceChildren();
            const h = document.createElement("h3"); h.textContent = chat.title; byId("offline-chat-detail").append(h);
            (detail.messages || detail.turns || []).forEach((turn) => { const p = document.createElement("p"); p.textContent = turn.content || turn.answer || turn.question || ""; byId("offline-chat-detail").append(p); });
          } catch { toast({ kind: "error", title: "This chat isn't saved on this device" }); }
        });
        list.append(button);
      });
      if (!result.chats.length) list.textContent = "No chats saved on this device yet.";
    } catch { list.textContent = "No chats saved on this device yet."; }
  }
  byId("offline-sources-toggle").addEventListener("click", async () => {
    const list = byId("offline-source-list");
    if (!list.hidden) { list.hidden = true; return; }
    list.hidden = false;
    list.textContent = "Loading saved source list…";
    try {
      const collection = localStorage.getItem("agenticrag.collection") || "research";
      const scopes = (localStorage.getItem("agenticrag.scopes") || "private").split(",");
      const query = new URLSearchParams({ collection });
      scopes.forEach((scope) => query.append("scope", scope.trim()));
      const result = await fetchJson(`/api/v1/sources?${query}`, 1500);
      list.replaceChildren();
      for (const source of result.sources || []) {
        const row = document.createElement("p");
        row.textContent = source.title || source.name || source.logical_path || "Untitled source";
        list.append(row);
      }
      if (!list.childElementCount) list.textContent = "No source list saved on this device.";
    } catch { list.textContent = "No source list saved on this device."; }
  });
  function applyRuntime(status) {
    lastRuntime = status;
    const chat = status?.chat;
    if (!chat?.configured) return;
    const previous = connection;
    const down = !chat.reachable || chat.model_present === false;
    const name = runtimeName(chat.runtime);
    const chip = document.querySelector(".runtime-chip");
    chip.classList.toggle("is-down", down);
    if (down) chip.setAttribute("aria-label", chat.model_present === false ? "Chat model missing. Show details" : `${name} not responding. Show details`);
    else chip.setAttribute("aria-label", "Chat model settings");
    if (down) {
      connection = chat.model_present === false ? "model_missing" : "runtime_down";
      byId("composer-status").hidden = false;
      byId("composer-status-text").textContent = chat.model_present === false ? "The selected model is missing. Choose another model to send this question." : `Answers are paused until ${name} responds on your Mac mini.`;
      byId("question-input").placeholder = "Write your next question. Send it once the model is back.";
      if (!state.runId) byId("send-button").disabled = true;
      byId("send-button").setAttribute("aria-label", chat.model_present === false ? "Send unavailable: model missing" : `Send unavailable: ${name} not responding`);
    } else {
      if (connection === "runtime_down" || connection === "model_missing") connection = "ok";
      byId("composer-status").hidden = true;
      if (!state.runId) byId("send-button").disabled = false;
      byId("send-button").setAttribute("aria-label", "Send question");
      const label = byId("chat-model-label");
      if (chat.loaded === true) warmStartedAt = 0;
      if (warmStartedAt && Date.now() - warmStartedAt > 120_000) warmStartedAt = 0;
      if (chat.loaded === false && warmStartedAt) label.textContent = "Loading…";
      else if (state.bootstrap?.providers?.chat?.model) label.textContent = modelDisplayName(state.bootstrap.providers.chat.model);
    }
    if (previous === "ok" && down) toast({ kind: "error", title: chat.model_present === false ? "Selected model missing" : `${name} isn't responding`, action: { label: "Retry", run: () => void checkConnection(true) } });
    if ((previous === "runtime_down" || previous === "model_missing") && !down) toast({ kind: "success", title: `${name} is ready` });
    const embedding = status.embedding;
    const embeddingDown = embedding?.configured && (!embedding.reachable || embedding.model_present === false);
    document.querySelectorAll('#workflow-options [data-workflow="fixed"], #workflow-options [data-workflow="agent"], #workflow-options [data-workflow="supervisor"]').forEach((button) => {
      button.disabled = Boolean(embeddingDown);
      button.title = embeddingDown ? "Grounded answers need the embedding model" : "";
    });
    renderRuntimePopover();
  }
  const runtimePopover = document.createElement("div");
  runtimePopover.className = "runtime-details popover";
  runtimePopover.id = "runtime-details";
  runtimePopover.hidden = true;
  document.querySelector(".runtime-strip").append(runtimePopover);
  const modelPicker = document.createElement("div");
  modelPicker.className = "model-picker popover";
  modelPicker.id = "model-picker";
  modelPicker.hidden = true;
  modelPicker.setAttribute("role", "listbox");
  modelPicker.setAttribute("aria-label", "Choose a chat model");
  document.querySelector(".runtime-strip").append(modelPicker);
  function renderModelPicker() {
    modelPicker.replaceChildren();
    const heading = document.createElement("strong"); heading.textContent = "Chat model"; modelPicker.append(heading);
    const active = state.bootstrap?.providers?.chat?.model;
    const available = [...new Set([active, ...state.installedChatModels].filter(Boolean))];
    if (!available.length) { const empty = document.createElement("p"); empty.textContent = "No installed models found. Open Models to refresh."; modelPicker.append(empty); }
    available.forEach((model) => {
      const option = document.createElement("button"); option.type = "button"; option.className = "model-picker-option";
      option.setAttribute("role", "option"); option.setAttribute("aria-selected", String(model === active));
      const group = state.evaluation?.available && state.evaluation.groups?.find((row) => row.model === model && row.workflow === "fixed_rag" && row.mean_latency_ms != null);
      const badge = document.createElement("span"); badge.className = "model-option-status";
      badge.dataset.state = model !== active ? "available" : lastRuntime?.chat?.loaded === false ? "loading" : lastRuntime?.chat?.reachable ? "ready" : "unavailable";
      badge.setAttribute("aria-label", badge.dataset.state === "available" ? "installed" : badge.dataset.state);
      const display = document.createElement("strong"); display.textContent = modelDisplayName(model);
      const detail = document.createElement("small"); detail.textContent = [model === active && lastRuntime?.chat?.loaded === false ? "not loaded" : "", group ? `~${(group.mean_latency_ms / 1000).toFixed(1)} s typical` : ""].filter(Boolean).join(" · ") || model;
      option.append(badge, display, detail);
      option.addEventListener("click", async () => {
        if (model === active) { modelPicker.hidden = true; return; }
        option.disabled = true;
        try {
          const current = state.bootstrap.providers.chat;
          if (current.configured === false || current.runtime !== "ollama") applyRuntimeProfile("chat", "ollama");
          else fillProviderForm("chat", current);
          providerForm("chat").elements.api_key.value = "";
          providerForm("chat").elements.model.value = model;
          await configureProvider("chat", providerForm("chat"), true);
          modelPicker.hidden = true;
          toast({ kind: "success", title: `${modelDisplayName(model)} selected for chat` });
        } catch (error) { toast(error.message, true); }
        finally { option.disabled = false; }
      });
      modelPicker.append(option);
    });
    const more = document.createElement("button"); more.type = "button"; more.className = "model-picker-more"; more.textContent = "Open Models";
    more.addEventListener("click", () => { modelPicker.hidden = true; setView("models"); });
    modelPicker.append(more);
    if (state.evaluation?.available) {
      const footer = document.createElement("p"); footer.className = "model-picker-foot"; footer.textContent = "Times from measured Fixed RAG runs on this Mac."; modelPicker.append(footer);
    }
  }
  modelPicker.addEventListener("keydown", (event) => {
    const options = [...modelPicker.querySelectorAll('[role="option"]')];
    const index = options.indexOf(document.activeElement);
    const next = event.key === "ArrowDown" ? (index + 1) % options.length : event.key === "ArrowUp" ? (index - 1 + options.length) % options.length : event.key === "Home" ? 0 : event.key === "End" ? options.length - 1 : -1;
    if (next >= 0 && options.length) { event.preventDefault(); options[next].focus(); }
  });
  function renderRuntimePopover() {
    if (!lastRuntime) return;
    const chat = lastRuntime.chat || {};
    const name = runtimeName(chat.runtime);
    const model = state.bootstrap?.providers?.chat?.model || "Chat model";
    const title = chat.model_present === false ? `${modelDisplayName(model)} isn't in ${name}` : `${name} isn't responding`;
    const body = chat.model_present === false ? `${name} is running on your Mac mini, but this model isn't in its model list.` : `Your Mac mini is online, but ${name} didn't answer. It may have quit or still be starting.`;
    const stateLabel = (role) => !role?.configured ? "not configured" : role.error_kind === "refused" ? "connection refused" : role.error_kind === "timeout" ? "no response" : role.error_kind === "model_missing" ? "not in model list" : role.reachable ? `ok · ${role.latency_ms ?? "—"} ms` : "not responding";
    runtimePopover.replaceChildren();
    const heading = document.createElement("strong"); heading.textContent = title;
    const description = document.createElement("p"); description.textContent = body;
    const table = document.createElement("div"); table.className = "runtime-table";
    for (const [label, role] of [["Chat", lastRuntime.chat], ["Embeddings", lastRuntime.embedding]]) {
      const row = document.createElement("div"); row.className = "row";
      const roleName = document.createElement("span"); roleName.textContent = label;
      const status = document.createElement("span"); status.className = `state${!role?.configured || role.reachable && role.model_present !== false ? "" : " is-bad"}`; status.textContent = stateLabel(role);
      row.append(roleName, status); table.append(row);
    }
    const foot = document.createElement("p"); foot.className = "runtime-foot";
    foot.textContent = [name, chat.endpoint, lastRuntime.checked_at ? `checked ${new Date(lastRuntime.checked_at).toLocaleTimeString()}` : ""].filter(Boolean).join(" · ");
    const works = document.createElement("p"); works.textContent = "Still works: reading chats and sources, project memory.";
    const actions = document.createElement("div"); actions.className = "dialog-actions";
    const retry = document.createElement("button"); retry.className = "primary-button"; retry.type = "button"; retry.textContent = "Retry now"; retry.addEventListener("click", () => void checkConnection(true));
    const models = document.createElement("button"); models.className = "secondary-button"; models.type = "button"; models.textContent = "Choose a model"; models.addEventListener("click", () => { runtimePopover.hidden = true; setView("models"); });
    actions.append(models, retry);
    runtimePopover.append(heading, description, table, foot, works, actions);
  }
  document.querySelector(".runtime-chip").addEventListener("click", (event) => {
    event.preventDefault(); event.stopImmediatePropagation();
    if (lastRuntime?.chat?.configured && (!lastRuntime.chat.reachable || lastRuntime.chat.model_present === false)) {
      modelPicker.hidden = true;
      runtimePopover.hidden = !runtimePopover.hidden;
    } else {
      runtimePopover.hidden = true;
      renderModelPicker(); modelPicker.hidden = !modelPicker.hidden;
    }
  }, true);
  document.addEventListener("click", (event) => { if (!event.target.closest(".runtime-strip")) { runtimePopover.hidden = true; modelPicker.hidden = true; } });
  document.addEventListener("keydown", (event) => { if (event.key === "Escape") { runtimePopover.hidden = true; modelPicker.hidden = true; } });
  async function checkConnection(force = false) {
    if (!navigator.onLine) { showOffline("device_offline"); return false; }
    lastAttempt = new Date();
    try {
      await fetchJson("/api/v1/health", 4000);
      const wasOffline = offlineSince > 0;
      failureCount = 0;
      if (wasOffline) hideOffline();
      const runtime = await fetchJson(`/api/v1/runtime-status${force ? "?fresh=1" : ""}`, 5000).catch(() => null);
      if (runtime) applyRuntime(runtime);
      if (!wasOffline && connection === "checking") connection = "ok";
      return true;
    } catch {
      failureCount++;
      if (force || failureCount >= 2) showOffline("server_unreachable");
      return false;
    }
  }
  byId("offline-try").addEventListener("click", () => { retrySeconds = 8; void checkConnection(true); });
  byId("offline-draft").addEventListener("input", (event) => {
    try {
      const drafts = JSON.parse(localStorage.getItem("agenticrag.drafts") || "{}");
      drafts[offlineChatId] = event.target.value;
      localStorage.setItem("agenticrag.drafts", JSON.stringify(drafts));
    } catch { /* private mode */ }
  });
  byId("composer-retry").addEventListener("click", () => void checkConnection(true));
  window.addEventListener("online", () => void checkConnection(true));
  window.addEventListener("offline", () => showOffline("device_offline"));
  document.addEventListener("visibilitychange", () => { if (!document.hidden) void checkConnection(true); });
  setInterval(() => { if (!document.hidden) void checkConnection(); }, 60000);
  setInterval(() => { if (!document.hidden && warmStartedAt && lastRuntime?.chat?.loaded === false) void checkConnection(true); }, 4000);
  window.ragConnection = { apply: applyRuntime, check: checkConnection };

  async function launch() {
    const started = performance.now();
    if (settings.intro === "slow") setTimeout(() => { if (byId("launch").dataset.done !== "true") document.documentElement.dataset.launch = "on"; }, 400);
    if (settings.intro === "off") { void checkConnection(true); return; }
    const health = (async () => {
      if (!navigator.onLine) throw new Error("offline");
      const t = performance.now();
      const value = await fetchJson("/api/v1/health", 4000);
      launchRow("launch-mac", "ok", `${Math.round(performance.now() - t)} ms`);
      return value;
    })();
    const runtime = fetchJson("/api/v1/runtime-status", 5000).then((value) => {
      const chat = value.chat;
      const model = state.bootstrap?.providers?.chat?.model;
      launchRow("launch-model", !chat?.configured ? "ok" : chat?.reachable && chat?.model_present !== false ? "ok" : "fail", !chat?.configured ? "not configured" : chat?.model_present === false ? "model missing" : chat?.reachable ? chat.loaded === false ? "not loaded" : "ready" : "not responding", model ? modelDisplayName(model) : runtimeName(chat?.runtime));
      applyRuntime(value); return value;
    });
    const library = fetchJson("/api/v1/projects", 4000).then(async (value) => {
      const collection = localStorage.getItem("agenticrag.collection") || "research";
      const scopes = (localStorage.getItem("agenticrag.scopes") || "private").split(",");
      const project = value.projects?.find((item) => item.collection === collection && item.scopes?.join(",") === scopes.join(","));
      const name = project?.name || collection;
      const query = new URLSearchParams({ collection }); scopes.forEach((item) => query.append("scope", item.trim()));
      const sources = await fetchJson(`/api/v1/sources?${query}`, 4000);
      launchRow("launch-library", "ok", sources.sources.length ? `${sources.sources.length} ready` : "no sources yet", name);
      return sources;
    });
    const [mac, model, docs] = await Promise.allSettled([health, runtime, library]);
    byId("launch").dataset.done = "true";
    if (mac.status === "rejected") {
      if (!navigator.onLine) { showOffline("device_offline"); return; }
      launchRow("launch-mac", "fail", navigator.onLine ? "no response" : "this device offline");
      byId("launch-status").textContent = navigator.onLine ? "Can't reach your Mac mini" : "This device is offline";
      byId("launch-actions").hidden = false;
      byId("launch-continue").textContent = "Continue offline";
      byId("launch-continue").onclick = () => { hideLaunch(); showOffline(navigator.onLine ? "server_unreachable" : "device_offline"); };
      byId("launch-retry").onclick = () => { byId("launch-actions").hidden = true; void launch(); };
      showOffline(navigator.onLine ? "server_unreachable" : "device_offline");
      return;
    }
    if (model.status === "rejected" || model.value?.chat?.configured && (!model.value.chat.reachable || model.value.chat.model_present === false)) {
      byId("launch-status").textContent = `${runtimeName(model.value?.chat?.runtime)} isn't ready on your Mac mini`;
      byId("launch-actions").hidden = false;
      byId("launch-continue").textContent = "Open anyway";
      byId("launch-continue").onclick = hideLaunch;
      byId("launch-retry").onclick = () => { byId("launch-actions").hidden = true; void launch(); };
      if (settings.intro === "slow") document.documentElement.dataset.launch = "on";
      return;
    }
    if (docs.status === "rejected") launchRow("launch-library", "fail", "unavailable");
    connection = "ok";
    if (model.value?.chat?.loaded === false) {
      byId("launch-status").textContent = "Loading the chat model on your Mac mini…";
      if (localStorage.getItem("agenticrag.warmOnLaunch") !== "0") {
        warmStartedAt = Date.now();
        byId("chat-model-label").textContent = "Loading…";
        void post("/api/v1/runtime/warm", { role: "chat" }).then((result) => {
          if (!result.started) { warmStartedAt = 0; void checkConnection(true); }
        }).catch(() => { warmStartedAt = 0; void checkConnection(true); });
      }
      const loadingAt = performance.now();
      const tick = setInterval(() => launchRow("launch-model", "run", `loading · ${Math.floor((performance.now() - loadingAt) / 1000)} s`), 1000);
      await wait(Math.max(900, 3000 - (performance.now() - started)));
      clearInterval(tick);
    } else {
      byId("launch-status").textContent = "Ready";
      await wait(Math.max(200, 900 - (performance.now() - started)));
    }
    hideLaunch();
  }
  byId("launch").addEventListener("click", (event) => { if (event.target.closest("button")) return; if (connection === "ok") hideLaunch(); });
  document.addEventListener("keydown", () => { if (document.documentElement.dataset.launch === "on" && connection === "ok") hideLaunch(); });
  void launch();

  if ("serviceWorker" in navigator && (location.protocol === "https:" || location.hostname === "localhost" || location.hostname === "127.0.0.1")) {
    navigator.serviceWorker.register("/sw.js").then((registration) => {
      const offerUpdate = () => toast({ kind: "info", title: "Update ready", action: { label: "Reload", run: () => {
        const waiting = registration.waiting;
        if (!waiting) { location.reload(); return; }
        navigator.serviceWorker.addEventListener("controllerchange", () => location.reload(), { once: true });
        waiting.postMessage({ type: "activate-update" });
      } } });
      if (registration.waiting) offerUpdate();
      registration.addEventListener("updatefound", () => {
        registration.installing?.addEventListener("statechange", () => {
          if (registration.waiting && navigator.serviceWorker.controller) offerUpdate();
        });
      });
      navigator.serviceWorker.ready.then(() => navigator.serviceWorker.controller?.postMessage({ type: "offline-chats", enabled: localStorage.getItem("agenticrag.offlineChats") !== "0" }));
    }).catch(() => {});
  }
})();
