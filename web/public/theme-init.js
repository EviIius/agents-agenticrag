(() => {
  let preference = 'system';
  try { preference = localStorage.getItem('workbench-theme') || 'system'; } catch { /* Storage may be unavailable. */ }
  const dark = preference === 'dark' || (preference !== 'light' && matchMedia('(prefers-color-scheme: dark)').matches);
  document.documentElement.dataset.theme = dark ? 'dark' : 'light';
})();
