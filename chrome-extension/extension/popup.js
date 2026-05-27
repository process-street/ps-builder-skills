const $ = (id) => document.getElementById(id);

async function refresh() {
  const state = await chrome.runtime.sendMessage({ type: 'GET_STATE' });
  const recording = !!(state && state.recording);
  const count = (state && state.event_count) || 0;

  const statusEl = $('status');
  statusEl.textContent = recording ? '● Recording' : (count > 0 ? 'Stopped' : 'Idle');
  statusEl.className = 'status' + (recording ? ' recording' : '');

  $('event-count').textContent = count ? `${count} events captured` : '';
  $('start').disabled = recording;
  $('stop').disabled = !recording;
  $('export').disabled = recording || count === 0;
}

$('start').addEventListener('click', async () => {
  await chrome.runtime.sendMessage({ type: 'START_RECORDING' });
  refresh();
});

$('stop').addEventListener('click', async () => {
  await chrome.runtime.sendMessage({ type: 'STOP_RECORDING' });
  refresh();
});

$('export').addEventListener('click', async () => {
  await chrome.runtime.sendMessage({ type: 'EXPORT_RECORDING' });
});

$('reset').addEventListener('click', async () => {
  if (!confirm('Discard current recording?')) return;
  await chrome.runtime.sendMessage({ type: 'RESET_RECORDING' });
  refresh();
});

refresh();
setInterval(refresh, 1000);
