---
name: video-to-ps-page
description: >
  Create a Process Street page from a video source: either a Loom URL or a local video file (MP4).
  Transcribes the video, structures the content into HTML, and publishes a fully formatted PS page
  via the Process Street MCP tools. Use this skill whenever the user shares a Loom link or a local
  MP4 path, or says anything like "create a page", "build a PS page", "make a page from this",
  or "turn this into a page".
---

# Video to PS Page Skill

You are turning a video (Loom URL or local MP4) into a polished, published Process Street page.
The goal is a page that reads like a real SOP or knowledge article — clear headings and structured
steps. For Loom videos, include deep-link timestamps so readers can jump to the relevant moment.

## Prerequisites

- **Process Street MCP** connected and authenticated
- **For Loom URLs:** `loom_cli.py` available at `~/.claude/tools/loom_cli.py`
- **For local MP4 files:** `openai-whisper` and `ffmpeg` installed
  - Install whisper: `pip3 install openai-whisper --break-system-packages`
  - Install ffmpeg: `brew install ffmpeg`

---

## Step 1 — Get the source

If the user hasn't provided a Loom URL or local file path, ask:
> "What would you like to turn into a page? Drop a Loom URL or a local MP4 file path."

---

## Step 2 — Transcribe the video

**For a Loom URL:**

Use `Bash` to run:
```
python3 ~/.claude/tools/loom_cli.py <url> --json
```

This returns JSON with:
- `title` — video title
- `transcript` — array of `{ start: float (seconds), text: string, speaker: string|null }`
- `video_id` — used to build deep-link URLs: `https://www.loom.com/share/<video_id>?t=<seconds>`

Use the transcript segments to structure the page content and timestamps.

---

**For a local MP4 file:**

Transcribe using `Bash`:
```
python3 -c "
import whisper, json
model = whisper.load_model('base')
result = model.transcribe('<absolute-path-to-file>', verbose=False)
print(json.dumps(result))
" > /tmp/transcript.json
```

Then read `/tmp/transcript.json`. It contains a `segments` array with
`{ start: float, end: float, text: string }` per segment.

> **Note:** Timestamp deep-links are not applicable for local MP4s since there is no hosted URL.
> Omit timestamp links from the widgets.

After creating the page, remind the user:
> "The Video widget must be added manually in PS — the API only supports Loom, YouTube, Vimeo,
> and Wistia URLs. Local file uploads are a web UI-only feature."

---

## Step 3 — Ask for the destination folder

Before creating anything, retrieve the full folder list by paginating through ALL pages:

1. Call `mcp__claude_ai_Process_Street__listFolders` (no cursor on first call)
2. If the response includes a `links` entry with `name: "next"`, call `listFolders` again with the `_` cursor value from that link
3. Keep paginating until there is no `"next"` link in the response
4. Combine all folders across all pages into a single list

> **Note:** `listFolders` excludes system folders (Home, Private). If the user wants a folder
> inside Home (e.g. a personal Hackathon folder), ask them to provide the folder ID directly —
> it won't appear in the list.

Show the combined list to the user and ask:
> "Which folder should I create this page in?"

Wait for the user to confirm before proceeding.

---

## Step 4 — Structure the content into HTML widgets

Read through the transcript and organize it into logical sections. Each section becomes one Text widget.

**HTML formatting rules — follow these exactly:**
- Section headings: `<h2><strong>Section Title</strong></h2>`
- Body text: `<p>text here</p>`
- Numbered steps: `<ol><li>Step one</li><li>Step two</li></ol>`
- Bullet lists: `<ul><li>Item</li></ul>`
- Bold emphasis: `<strong>important term</strong>`
- Links: `<a href="URL">link text</a>`

**For Loom videos — add timestamp deep-links:**

At the top of each section widget, add a timestamp link just below the heading:
```html
<h2><strong>Section Title</strong></h2>
<p><a href="https://www.loom.com/share/VIDEO_ID?t=42">▶ Watch this section (0:42)</a></p>
<p>Section content here...</p>
```
Format the display time as `M:SS` (e.g. 125 seconds → `2:05`).

**Widget breakdown:**
- Aim for 3–7 widgets per page — one per logical section, not one per paragraph
- Each widget should be self-contained and scannable
- Keep widgets focused; don't dump the entire transcript into one block

---

## Step 5 — Create the page

Follow this sequence exactly:

**5a. Create the page shell**

Call `mcp__claude_ai_Process_Street__createPage` with:
- `name` — a clear, title-cased page name based on the content
- `folderId` — the ID of the folder the user selected in Step 3

Save the returned `id` as `pageId`.

**5b. Create a draft revision**

Call `mcp__claude_ai_Process_Street__createPageRevision` with:
- `pageId` — from Step 5a

Save the returned revision `id` as `revisionId`.

**5c. Embed the video (Loom only)**

If the source was a Loom URL, call `mcp__claude_ai_Process_Street__createPageRevisionWidget` with:
- `pageId`, `revisionId`
- `createpagewidgetrequest`: `{ "type": "Video", "url": "<loom URL>", "position": { "type": "Top" } }`

Skip this step for local MP4s — the API does not support file uploads for Video widgets.
Only Loom, YouTube, Vimeo, and Wistia URLs are accepted.

**5d. Add content widgets**

For each structured section from Step 4, call `mcp__claude_ai_Process_Street__createPageRevisionWidget` with:
- `pageId`, `revisionId`
- `createpagewidgetrequest`: `{ "type": "Text", "content": "<html>...</html>", "position": { "type": "Bottom" } }`

Add widgets in order from top to bottom.

**5e. Publish the revision**

Call `mcp__claude_ai_Process_Street__publishPageRevision` with:
- `pageId`, `revisionId`

---

## Step 6 — Return the result

Construct the page URL:
```
https://app.process.st/pages/<pageId>/view
```

Give the user a one-line summary:
> "Done! I created **[Page Name]** in the **[Folder]** folder with [N] sections. [Link]"

For local MP4s, append the reminder to add the Video widget manually in the PS web UI.

---

## Notes

- **HTML only** — PS renders HTML, not markdown. Never use `#`, `**`, or `-` inside widget content.
- **Folder is required** — always confirm with the user before creating the page.
- **Publish is required** — a page without a published revision is a draft and won't be visible. Always complete Step 5e.
- **Widget order matters** — video embed goes first (`Top`), then text widgets in order (`Bottom` appends sequentially).
- **Video widget API limitation** — only Loom, YouTube, Vimeo, and Wistia URLs are accepted. Local file uploads are a web UI-only feature and cannot be automated via the API.
