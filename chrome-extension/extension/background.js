const STORAGE_KEY = 'ps_builder_state';

function emptyState() {
  return { recording: false, session_id: null, started_at: null, ended_at: null, events: [] };
}

async function getState() {
  const data = await chrome.storage.local.get(STORAGE_KEY);
  return data[STORAGE_KEY] || emptyState();
}

async function setState(patch) {
  const cur = await getState();
  const next = { ...cur, ...patch };
  await chrome.storage.local.set({ [STORAGE_KEY]: next });
  return next;
}

async function captureScreenshot(tabId) {
  try {
    const tab = await chrome.tabs.get(tabId);
    if (!tab || !tab.active) return null;
    return await chrome.tabs.captureVisibleTab(tab.windowId, { format: 'png' });
  } catch (err) {
    console.warn('[ps-builder] screenshot failed:', err && err.message);
    return null;
  }
}

async function appendEvent(event, tabId) {
  const state = await getState();
  if (!state.recording) return;
  let screenshot = null;
  if (tabId != null) screenshot = await captureScreenshot(tabId);
  state.events.push({ ...event, screenshot });
  await chrome.storage.local.set({ [STORAGE_KEY]: state });
}

async function broadcast(message) {
  const tabs = await chrome.tabs.query({});
  for (const tab of tabs) {
    if (!tab.id) continue;
    chrome.tabs.sendMessage(tab.id, message).catch(() => {});
  }
}

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  (async () => {
    try {
      if (msg.type === 'START_RECORDING') {
        await setState({
          recording: true,
          session_id: crypto.randomUUID(),
          started_at: new Date().toISOString(),
          ended_at: null,
          events: [],
        });
        await broadcast({ type: 'RECORDING_STARTED' });
        sendResponse({ ok: true });
      } else if (msg.type === 'STOP_RECORDING') {
        await setState({ recording: false, ended_at: new Date().toISOString() });
        await broadcast({ type: 'RECORDING_STOPPED' });
        sendResponse({ ok: true });
      } else if (msg.type === 'GET_STATE') {
        const state = await getState();
        sendResponse({
          recording: state.recording,
          event_count: state.events.length,
          session_id: state.session_id,
        });
      } else if (msg.type === 'EVENT_CAPTURED') {
        await appendEvent(msg.event, sender.tab && sender.tab.id);
        sendResponse({ ok: true });
      } else if (msg.type === 'EXPORT_RECORDING') {
        await buildExport();
        sendResponse({ ok: true });
      } else if (msg.type === 'RESET_RECORDING') {
        await chrome.storage.local.set({ [STORAGE_KEY]: emptyState() });
        await broadcast({ type: 'RECORDING_STOPPED' });
        sendResponse({ ok: true });
      } else {
        sendResponse({ ok: false, error: 'unknown_message' });
      }
    } catch (err) {
      console.error('[ps-builder] handler error:', err);
      sendResponse({ ok: false, error: String(err && err.message || err) });
    }
  })();
  return true; // async response
});

chrome.webNavigation.onCommitted.addListener(async (details) => {
  if (details.frameId !== 0) return;
  const state = await getState();
  if (!state.recording) return;
  await appendEvent({
    type: 'navigation',
    timestamp: new Date().toISOString(),
    url: details.url,
    transition_type: details.transitionType,
  }, details.tabId);
});

async function buildExport() {
  const state = await getState();
  const folder = `ps-recording-${(state.session_id || 'unknown').slice(0, 8)}`;
  const md = renderMarkdown(state);

  const mdUrl = 'data:text/markdown;charset=utf-8,' + encodeURIComponent(md);
  await chrome.downloads.download({
    url: mdUrl,
    filename: `${folder}/recording.md`,
    saveAs: false,
  });

  let imgIdx = 0;
  for (const ev of state.events) {
    if (!ev.screenshot) continue;
    imgIdx++;
    await chrome.downloads.download({
      url: ev.screenshot,
      filename: `${folder}/screenshots/step-${String(imgIdx).padStart(3, '0')}.png`,
      saveAs: false,
    });
  }
}

function renderMarkdown(state) {
  const lines = [];
  lines.push(`# Browser Recording — ${state.session_id || 'unknown'}`);
  lines.push('');
  lines.push(`Recorded with the PS Builder Chrome Extension.`);
  lines.push('');
  lines.push(`- Started: ${state.started_at || '?'}`);
  lines.push(`- Ended: ${state.ended_at || '?'}`);
  lines.push(`- Events: ${state.events.length}`);
  lines.push('');
  lines.push('## Instructions for Claude');
  lines.push('');
  lines.push('This is a recording of a user performing a process in their browser. Convert it into a Process Street workflow:');
  lines.push('');
  lines.push('1. Use the Process Street MCP tools to create a new workflow.');
  lines.push('2. Infer the workflow name from the events (typically the first meaningful page title or the URL pattern).');
  lines.push('3. Group events into logical tasks. Heuristic: each navigation = a new task; form interactions on the same page belong to one task.');
  lines.push('4. For each task, write a clear name + description. Reference the screenshot (`screenshots/step-NNN.png`) in the description if useful.');
  lines.push('5. When events include `form_field` data, add corresponding PS form fields (short text, long text, email, dropdown, etc.) to the matching task.');
  lines.push('6. Ignore noise: duplicate clicks, non-meaningful navigations, programmatic re-renders.');
  lines.push('');
  lines.push('## Events');
  lines.push('');
  let imgIdx = 0;
  state.events.forEach((ev, i) => {
    lines.push(`### Event ${i + 1} — ${ev.type}`);
    lines.push(`- Time: ${ev.timestamp}`);
    if (ev.url) lines.push(`- URL: ${ev.url}`);
    if (ev.page_title) lines.push(`- Page: ${ev.page_title}`);
    if (ev.element) {
      lines.push(`- Element: \`${ev.element.tag || '?'}\``);
      if (ev.element.accessible_name) lines.push(`  - Name: "${ev.element.accessible_name}"`);
      if (ev.element.text && ev.element.text !== ev.element.accessible_name) {
        lines.push(`  - Text: "${ev.element.text}"`);
      }
      if (ev.element.selector) lines.push(`  - Selector: \`${ev.element.selector}\``);
      if (ev.element.href) lines.push(`  - Href: ${ev.element.href}`);
    }
    if (ev.form_field) {
      const ff = ev.form_field;
      lines.push(`- Form field:`);
      if (ff.name) lines.push(`  - Name: ${ff.name}`);
      if (ff.type) lines.push(`  - Type: ${ff.type}`);
      if (ff.label) lines.push(`  - Label: ${ff.label}`);
      if (ff.value !== undefined && ff.value !== '') lines.push(`  - Value: ${JSON.stringify(ff.value)}`);
    }
    if (ev.screenshot) {
      imgIdx++;
      lines.push(`- Screenshot: ![${ev.type}](screenshots/step-${String(imgIdx).padStart(3, '0')}.png)`);
    }
    lines.push('');
  });
  lines.push('## Raw events (JSON, screenshots stripped)');
  lines.push('');
  lines.push('```json');
  const cleanEvents = state.events.map((e) => ({ ...e, screenshot: e.screenshot ? '[saved as png]' : null }));
  lines.push(JSON.stringify(cleanEvents, null, 2));
  lines.push('```');
  return lines.join('\n');
}
