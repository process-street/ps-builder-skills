# Chrome Extension — PS Builder Recorder

A Chrome extension that records what a user does in the browser and exports a `recording.md` file. Hand that file to Claude Code (with the Process Street MCP connected) and Claude generates a matching Process Street workflow.

## Install (dev mode)

1. Open `chrome://extensions` in Chrome
2. Toggle **Developer mode** (top-right)
3. Click **Load unpacked** and select the `extension/` folder in this directory
4. Pin the extension to the toolbar so the popup is one click away

When you edit code, hit the ↻ reload icon on the extension card in `chrome://extensions` to apply changes.

## Use

1. Open the page where your process starts
2. Click the extension icon → **Start recording**
3. Perform the process (click around, fill forms, navigate)
4. Click the extension icon → **Stop**, then **Export recording**
5. Chrome downloads a folder `ps-recording-<id>/` to your Downloads directory containing:
   - `recording.md` — the prompt + structured event log for Claude
   - `screenshots/step-NNN.png` — one screenshot per captured event
6. Move the folder into a directory where you run Claude Code (with the PS MCP enabled), then ask Claude to "create a Process Street workflow from this recording"

## What gets captured

- Clicks (element tag, accessible name, text, CSS selector, role, href)
- Form input changes (name, type, value — password fields are redacted)
- Form submits
- Navigations (URL + transition type)
- A screenshot of the visible tab at each event

## What's not captured (yet)

- Hover / mouse movement
- Multi-tab flows (only the active tab is screenshotted)
- Iframe content
- Keystrokes that don't fire a `change` event (use blur or Enter to flush)
- Conditional branches (each session is linear)

## Debugging

- **Service worker:** `chrome://extensions` → click "service worker" under the extension card → DevTools console for `background.js`
- **Popup:** right-click extension icon → "Inspect popup"
- **Content script:** open DevTools on the page being recorded, look at the page's console

## Files

```
extension/
  manifest.json     # MV3 manifest, permissions
  background.js     # Service worker: state, screenshots, export
  content.js        # Injected on every page; captures DOM events
  popup.html        # Start / Stop / Export UI
  popup.js          # Wires UI to the service worker
  popup.css         # Styling
```
