/* Prospective cancellation probe: observes actual text, then clicks a visible enabled control. */
export function observeStudioEvents() {
  window.nativeWorkflowEvents = [];
  const Base = window.EventSource;
  window.EventSource = class extends Base {
    constructor(url, options) {
      super(url, options);
      if (String(url).includes('/api/workflows/stream')) {
        for (const kind of ['run.snapshot', 'run.updated', 'node.text', 'node.progress']) {
          this.addEventListener(kind, event => {
            const item={kind,at:performance.timeOrigin+performance.now(),data:JSON.parse(event.data)};
            window.nativeWorkflowEvents.push(item);
            const target=window.nativeCancelTarget;
            if(kind==='node.text' && target && item.data.run_id===target.run_id && item.data.node_id===target.node_id && (item.data.text || item.data.delta)) {
              const button=[...document.querySelectorAll('button')].find(b=>b.textContent.trim()==='Cancel workflow'&&!b.disabled&&!b.closest('[inert]'));
              const box=button?.getBoundingClientRect();
              const hit=box?document.elementFromPoint(box.x+box.width/2,box.y+box.height/2):null;
              const clickable=!!button&&box.width>0&&box.height>0&&getComputedStyle(button).visibility==='visible'&&getComputedStyle(button).pointerEvents!=='none'&&(hit===button||button.contains(hit));
              window.nativeCancelResult={at:performance.timeOrigin+performance.now(),run_id:item.data.run_id,node_id:item.data.node_id,clicked:clickable};
              if(clickable){window.nativeCancelTarget=null;button.click();}
            }
          });
        }
      }
    }
  };
}
