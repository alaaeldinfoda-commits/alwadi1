<script>
async function fetchActiveAlerts() {
  try {
    const res = await fetch('/alerts/active', { credentials:'same-origin' });
    if (!res.ok) return;
    const alerts = await res.json();
    const strip = document.getElementById('alerts-strip');
    if (!strip) return;
    strip.innerHTML = '';
    alerts.forEach(a=>{
      const el = document.createElement('div');
      el.className = 'alert alert-'+(a.level || 'info')+' py-1 my-0';
      el.style.fontSize = '0.9rem';
      el.innerText = a.title;
      strip.appendChild(el);
    });
  } catch(e){ console.warn('alerts fetch', e); }
}

function showToastMessage(title, msg, level='info', timeout=5000) {
  const container = document.getElementById('globalToasts');
  if(!container) return;
  const toast = document.createElement('div');
  toast.className = 'toast align-items-center text-bg-'+(level==='danger'?'danger':(level==='success'?'success':'primary'))+' border-0';
  toast.role='alert';
  toast.innerHTML = `<div class="d-flex">
    <div class="toast-body"><strong>${title}</strong><div>${msg}</div></div>
    <button type="button" class="btn-close btn-close-white me-2" data-bs-dismiss="toast"></button>
  </div>`;
  container.appendChild(toast);
  const bs = new bootstrap.Toast(toast, { delay: timeout });
  bs.show();
  toast.addEventListener('hidden.bs.toast', ()=> toast.remove());
  return bs;
}

/* Loading overlay helpers */
function showLoading(){ const o=document.getElementById('loadingOverlay'); if(o) o.style.display='flex'; }
function hideLoading(){ const o=document.getElementById('loadingOverlay'); if(o) o.style.display='none'; }

/* auto fetch on load */
document.addEventListener('DOMContentLoaded', ()=>{
  fetchActiveAlerts();
  // polls for alerts every 30s
  setInterval(fetchActiveAlerts, 30000);
});
</script>
