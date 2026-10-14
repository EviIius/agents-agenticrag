/* Read-only observer of the actual Studio stream; suitable for page.addInitScript. */
export function observeStudioEvents() {
  window.nativeWorkflowEvents = [];
  const Base = window.EventSource;
  window.EventSource = class extends Base {
    constructor(url, options) {
      super(url, options);
      if (String(url).includes('/api/workflows/stream')) {
        for (const kind of ['run.snapshot', 'run.updated', 'node.text', 'node.progress']) {
          this.addEventListener(kind, event => window.nativeWorkflowEvents.push({
            kind, at: performance.timeOrigin + performance.now(), data: JSON.parse(event.data),
          }));
        }
      }
    }
  };
}
