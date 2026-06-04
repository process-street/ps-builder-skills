# Meeting transcripts and recordings → Workflow

**`call-to-workflow`** — turn any call artifact into a built, published Process Street
workflow:

- 📄 **Transcripts** — pasted text, `.txt`/`.md`/`.vtt`/`.srt`/`.json` exports (Gong, Zoom, Teams)
- 🎙 **Audio recordings** — transcribed locally with Whisper
- 🎥 **Video recordings** — Loom, Zoom/Teams exports, MP4 screen recordings — transcribed
  locally, **with key frames extracted at demonstration moments and embedded as images on
  the matching workflow tasks**

What makes it more than a summarizer:

- **Determines the actual procedure** — separates current practice from wishlist,
  hypotheticals, and facilitator suggestions before building anything
- **Evidence-based** — every task, field, logic rule, and approval carries a timestamped
  quote from the call; no evidence, no build
- **Confidence-scored** — high-confidence steps get built, medium ones get flagged,
  low ones land in a deferred list that becomes the follow-up agenda
- **Approval-gated** — produces a full workflow spec for sign-off before any API write
- **Verified** — re-fetches the built workflow and diffs it against the spec

## Contents

| File | Purpose |
|---|---|
| [`SKILL.md`](SKILL.md) | The skill — full pipeline |
| [`references/extraction-playbook.md`](references/extraction-playbook.md) | Verbal-pattern catalog, field-type guide, failure modes |
| [`references/ps-build-conventions.md`](references/ps-build-conventions.md) | PS API build order + gotchas |
| [`scripts/transcribe.py`](scripts/transcribe.py) | Local Whisper transcription (audio + video) |
| [`scripts/extract_frames.py`](scripts/extract_frames.py) | Key-moment frame extraction (timestamps or scene detection) |
| [`examples/sample-transcript.md`](examples/sample-transcript.md) | Sanitized sample call + expected spec |

## Quick start

```
# 1. Install the skill (Claude Code)
cp -r meeting-transcripts-and-recordings ~/.claude/skills/call-to-workflow

# 2. For recordings: install local tooling
pip3 install openai-whisper --break-system-packages
brew install ffmpeg

# 3. Connect the Process Street MCP server (or have a PS API key ready), then:
#    "Build a workflow from this call recording: ~/Downloads/walkthrough.mp4"
```

Pairs with the other skills in this repo: run **gap-analysis** first for strategic context;
use **documents** for SOPs/spreadsheets; reconcile when a prospect gives you both a call
and a document about the same process.
