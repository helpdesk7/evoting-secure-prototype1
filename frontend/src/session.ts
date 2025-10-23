export function startIdleTimer(onLogout: () => void, ms=15*60*1000) {
  let t:any; const reset=()=>{ clearTimeout(t); t=setTimeout(onLogout, ms); };
  ['click','keydown','mousemove','scroll'].forEach(e=>window.addEventListener(e, reset));
  reset(); return () => { clearTimeout(t); };
}
