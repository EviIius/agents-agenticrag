/* Apply saved appearance before styles paint. */
(() => {
  const defaults = {v:1,theme:"system",light:"light",dark:"dark",accent:"cobalt",fontUi:"geist",fontRead:"newsreader",textSize:"m",contrast:"auto",motion:"auto",intro:"always"};
  const allowed = {theme:["system","dark","light","midnight","paper"],light:["light","paper"],dark:["dark","midnight"],accent:["cobalt","amber","graphite"],fontUi:["geist","atkinson","system"],fontRead:["newsreader","literata","geist","atkinson"],textSize:["s","m","l"],contrast:["auto","more","normal"],motion:["auto","reduce"],intro:["always","slow","off"]};
  let saved = {};
  try {
    saved = JSON.parse(localStorage.getItem("agenticrag.appearance") || "{}") || {};
    if (!Object.keys(saved).length) {
      const old = localStorage.getItem("agenticrag.theme");
      if (old === "dark" || old === "light") saved.theme = old;
      localStorage.removeItem("agenticrag.theme");
    }
  } catch { saved = {}; }
  const settings = {...defaults};
  for (const key in allowed) if (allowed[key].includes(saved[key])) settings[key] = saved[key];
  const root = document.documentElement;
  const apply = () => {
    const dark = matchMedia("(prefers-color-scheme: dark)").matches;
    const theme = settings.theme === "system" ? settings[dark ? "dark" : "light"] : settings.theme;
    Object.assign(root.dataset, {theme,accent:settings.accent,fontUi:settings.fontUi,fontRead:settings.fontRead,textSize:settings.textSize,contrast:settings.contrast === "more" || settings.contrast === "auto" && matchMedia("(prefers-contrast: more)").matches ? "more" : "normal",motion:settings.motion === "reduce" ? "reduce" : "auto"});
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.content = {dark:"#0C0C0D",midnight:"#000000",light:"#FAFAF8",paper:"#F5F0E6"}[theme];
  };
  apply();
  if (settings.intro === "always") root.dataset.launch = "on";
  window.ragAppearance = {settings,apply};
})();
