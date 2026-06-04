---
name: call-to-workflow
description: >
  Turn any call artifact — a meeting transcript, an audio recording, or a video recording
  (Loom URL, Zoom/Teams/Gong export, MP4) — into a fully built, published Process Street
  workflow. Transcribes recordings locally, analyzes the conversation to determine what the
  actual procedure is (vs. wishlist, hypotheticals, or vendor suggestions), extracts key
  video frames and embeds them as images in the relevant workflow tasks, designs a workflow
  spec for approval, then builds and verifies it via the Process Street API/MCP.
  Use whenever the user shares a call transcript, recording, or video and says anything like
  "build a workflow from this call", "turn this recording into a workflow",
  "make a process from this video", or "call to workflow".
---

# Call → Workflow

You are converting a conversation about a process into a working Process Street workflow.
Someone described (or demonstrated) how their team works — on a discovery call, a kickoff,
a walkthrough, a screen-share. Your job is to figure out **what the actual procedure is**,
design it as a workflow, get the design approved, build it, and prove it was built correctly.

The output is never "a summary of the call." It is a runnable workflow plus a build report
that shows, with timestamped evidence, why every task exists.

---

## Supported inputs

| Input | Examples | How it's processed |
|---|---|---|
| Pasted transcript | Raw text, Gong/Zoom/Teams transcript export | Used directly |
| Transcript file | `.txt`, `.md`, `.vtt`, `.srt`, `.json` | Parsed; VTT/SRT timestamps preserved |
| Audio recording | `.mp3`, `.m4a`, `.wav` | Transcribed locally via Whisper (`scripts/transcribe.py`) |
| Video recording | `.mp4`, `.mov`, `.webm` — Zoom, Teams, Gong, screen recordings | Transcribed locally via Whisper **+ key frames extracted** (`scripts/extract_frames.py`) |
| Loom URL | `loom.com/share/...` | Transcript via Loom API/CLI if available; otherwise ask the user to download the MP4 |

Multiple inputs for the same process are welcome (e.g., two calls with different
stakeholders) — see *Multi-source reconciliation* below.

## Prerequisites

- **Process Street access** — either the Process Street MCP server connected, or a PS API
  key for the REST API (`https://public-api.process.st/api/v1.1`, header `X-API-Key`).
- **For recordings only:** `openai-whisper` and `ffmpeg` installed locally:
  ```
  pip3 install openai-whisper --break-system-packages
  # older pip (< 22.x) rejects that flag — use instead:  pip3 install --user openai-whisper
  brew install ffmpeg        # or apt-get install ffmpeg
  ```
  All transcription and frame extraction runs **locally** — no audio/video leaves the machine.

---

## Pipeline

### Step 0 — Intake

Confirm before doing anything else:

1. **Source** — which file/URL/text is the input? If video, confirm it shows a screen-share
   or demonstration (that's what makes frame extraction worthwhile).
2. **Target** — which Process Street organization and folder should the workflow land in?
   List folders (`listFolders`) and let the user pick. Never build in a customer's
   production folder without explicit confirmation.
3. **Build mode** — `live` (default: actually create the workflow) or `dry-run`
   (emit the spec and build report only).
4. **Naming** — default to `<Company/Team> — <Process Name>`; confirm with the user.

### Step 1 — Get a timestamped transcript

- **Text/transcript input:** use as-is. If it has no timestamps, that's fine — you simply
  won't have frame anchors.
- **Audio/video:** run the bundled transcriber:
  ```
  python3 scripts/transcribe.py <path-to-media> --model base --out /tmp/call_transcript.json
  ```
  Output is JSON: `{ "segments": [ { "start": float, "end": float, "text": str } ] }`.
  Use `--model small` or `medium` if the audio is noisy or heavily accented (slower, better).
- **Loom URL:** if a Loom CLI/API helper is available, pull `{title, transcript[], video_id}`
  from it. Otherwise ask the user to download the MP4 and treat as video.

### Step 2 — Call analysis (read the whole conversation first)

Do NOT start extracting tasks yet. First build a mental model of the call:

1. **Segment map.** Calls follow a predictable arc — label the regions:
   - 0–10%: intros, agenda (skim)
   - 10–40%: discovery — the prospect/customer describes how they work today (**read closely**)
   - 40–70%: demo/walkthrough — reactions, refinements, screen-share (**frame-extraction zone**)
   - 70–100%: pricing, next steps, commitments (skim for scope confirmations)
   Adjust if the call doesn't fit (a pure walkthrough call is 90% demonstration).
2. **Speaker roles.** Identify who is *describing the process* (the process owner — their
   words are evidence) vs. who is *selling/suggesting* (their words are proposals, not
   evidence) vs. who is *reacting* (confirmations and corrections — high-value evidence).
3. **Process census.** A single call often describes more than one process. List every
   distinct process mentioned, then confirm with the user which one(s) to build. Never
   silently merge two processes into one workflow.
4. **Classification.** Tag the target process as:
   - **OPS** — operational execution: checklists, field work, intake/triage, recurring runs
   - **DOCS** — document lifecycle: drafting, review cycles, approvals, regulated sign-off
   - **HYBRID** — both
   This drives which Process Street features you emphasize (OPS → assignments, due dates,
   data-set routing; DOCS → approvals, voting, conditional review paths).

### Step 3 — Determine the ACTUAL procedure

This is the core skill. People on calls describe four different things that all sound like
process — only one of them should be built as the main flow:

| What you're hearing | Markers | What to do |
|---|---|---|
| **Current practice** (the real procedure) | Present tense, habitual: "we do X", "every Monday", "then it goes to...", repeated consistently, confirmed by a second speaker | **Build it.** This is the workflow. |
| **Aspiration / wishlist** | "ideally", "we'd love to", "in a perfect world", "eventually we want" | Don't build into the main flow. Record in the build report under *Future enhancements*. |
| **Hypothetical / edge speculation** | "I guess if that happened...", "theoretically", single mention, no confirmation | Skip, or capture as a flagged optional branch if it sounds operationally real. |
| **Vendor/facilitator suggestion** | The seller/consultant proposes it; the process owner doesn't confirm | Not evidence. Only build if the owner explicitly agrees ("yes, exactly", "that would work"). |

Additional evidence rules:

- **Repetition beats mention.** A step described once in passing is weaker evidence than a
  step referenced three times. Weight accordingly.
- **Reactions are gold.** When the owner corrects a restatement ("well, actually first we...")
  that correction is the highest-quality evidence on the call.
- **Two speakers contradict each other** → build the **simpler** version, flag the conflict
  in the build report, and list the alternative as an open question.
- **Confidence score every step**: `high` (stated clearly + confirmed), `medium` (stated once,
  unambiguous), `low` (inferred or ambiguous). Policy: high → build; medium → build with a ⚠️
  flag in the report; low → don't build, list in *Deferred* with the reason.

### Step 4 — Extract the process elements

For each confirmed procedure, walk the transcript and map verbal patterns to Process Street
primitives. The full pattern catalog is in `references/extraction-playbook.md`; the summary:

| Listen for | Maps to |
|---|---|
| "When X happens, we..." / "Someone submits..." | Workflow trigger / kickoff form fields |
| "First... then... after that... finally..." | Task sequence (group into phases) |
| Imperative verbs from the process owner | Individual tasks |
| "If X then Y" / "it depends on..." | Conditional logic rules |
| Job titles, team names, "the manager" | Role-based task assignments |
| Nouns that get captured/looked up (IDs, dates, amounts, photos) | Form fields (see field-type guide in the playbook) |
| "has to sign off" / "needs approval" / "two people review" | Approval task (single, voting, or mandatory voters) |
| "then it goes to..." / "we hand it over to..." | Assignee change + notification |
| "sometimes we have to..." / "if it gets rejected..." | Exception branch (flagged) |
| "every morning" / "once a quarter" | Scheduled workflow |
| "we look it up in a spreadsheet" / "depends on the region/type/tier" | **Data Set** + linked dropdown (lookup-driven routing) |

Record a **timestamped evidence quote** for every task, field, rule, and approval you plan
to create. No evidence quote → it doesn't get built.

### Step 5 — Key-moment frame extraction (video inputs)

When the input is video, captured frames make the workflow dramatically better — each task
can carry a screenshot of the actual system/screen the step happens in.

1. **Identify key moments** from the transcript: segments where the speaker is *showing*
   something — markers like "let me share my screen", "as you can see here", "this is where
   we...", "so I click...", plus the timestamp of each extracted step from Step 4 that falls
   inside a demonstration region.
2. **Extract frames** at those timestamps:
   ```
   python3 scripts/extract_frames.py <video> --timestamps 312,478,1024 --out /tmp/frames
   ```
   Or let it find visually distinct moments automatically (scene-change detection):
   ```
   python3 scripts/extract_frames.py <video> --scene-detect 0.30 --out /tmp/frames
   ```
3. **Review every frame** (view the image files) before using it. Keep a frame only if it
   clearly shows the step's system/screen/artifact. Discard webcam-only frames, blurred
   transitions, and anything showing sensitive data (real customer records, credentials,
   email inboxes). **When in doubt, show the user the frame and ask before embedding.**
4. **Map kept frames to tasks** — each frame attaches to the task whose evidence quote it
   coincides with.
5. **Embed during the build** (Step 7): create an `Image` widget on the task, then upload
   the frame to it:
   - MCP: `createWorkflowRevisionTaskWidget` with `type: "Image"`, then upload via the
     widget upload endpoint
   - REST: `POST /workflows/{workflowId}/revisions/{revisionId}/tasks/{taskId}/widgets`
     with `{"type": "Image"}`, then
     `POST .../widgets/{widgetId}/upload` with multipart `file` (or JSON
     `fileBase64: {content, filename}`)

### Step 6 — Design the workflow spec (approval gate)

Produce a complete spec **before any API call** and show it to the user for approval.
Spec shape:

```yaml
workflow:
  name: "<Team> — <Process Name>"
  description: "Built from <call type> on <date> with <participant roles>"
  folder_id: "<confirmed target>"
  classification: OPS | DOCS | HYBRID
  tasks:
    - name: "Intake — Receive Request"     # no numeric prefixes — the UI numbers tasks
      assignee_role: "Coordinator"
      evidence: "[14:32] 'every request comes in through the shared inbox first'"
      confidence: high
      frame: frames/frame_0312.jpg        # video inputs only
      fields:
        - { type: "Text",   name: "Request ID",  required: true }
        - { type: "Select", name: "Region",      required: true, options: [...] }
        - { type: "MultiFile", name: "Supporting Photos" }
      widgets:
        - { type: "Text", body: "Verify the requester before continuing." }
    - name: "Review — Manager Approval"
      task_type: "Approval"               # single approver; voting/mandatory need thresholds
      assignee_role: "Manager"
      evidence: "[22:10] 'nothing moves until my manager signs off'"
      confidence: high
  logic_rules:
    - when: { field: "Region", op: "IsNot", value: "In Network" }
      then: [ { action: "Show", task: "Escalate — Out of Network" } ]   # target task is hiddenByDefault
      evidence: "[31:55] 'if it's out of network it goes to a totally different team'"
  data_sets:
    - name: "Region → Reviewer"
      reason: "[35:40] 'we keep that mapping in a spreadsheet' — lookup-driven routing"
  deferred:
    - item: "Automated CRM writeback"
      reason: "aspirational — 'we'd love it to update Salesforce someday' [48:12]"
```

Present the spec as a readable summary (task list, fields, rules, approvals, frames,
deferred items + why). **Wait for explicit approval before building in live mode.**

### Step 7 — Build it

Execute the approved spec against Process Street. MCP tools first; REST fallback.
**Order matters** — follow `references/ps-build-conventions.md` exactly. Summary:

1. `createWorkflow` (shell) → then `createWorkflowRevision` to get the **draft** revision
   (the shell auto-publishes an empty v0.0 — you can't build into it).
2. Create tasks **in order** using the `position` object (`Bottom` by default,
   `After {taskId}` to chain). Use `taskType` (`Standard`/`Approval`/`AI`/`Code`), not
   `type`. No numeric name prefixes. Logic-rule targets get `hiddenByDefault: true`.
3. Add widgets per task (form fields, text, **Image widgets + frame uploads**). Select
   options go in `config.items` as `[{"name": "..."}]`. Widget updates are
   full-replacement PUTs — never send partial bodies.
4. Create logic rules — `action: Show|Hide`, condition as OR-of-AND groups with short
   operator enums (`Is`, `IsNot`, `HasAnyValue`, `HasNoValue`, `IsGreaterThan`, `IsLessThan`), and `targets` with **both**
   `taskIds` and `widgetIds` keys (empty arrays allowed). Dedupe rules yourself.
5. Approvals are tasks with `taskType: "Approval"`; voting / mandatory-voter setups need
   explicit thresholds.
6. Create data sets + records, then wire linked dropdowns.
7. If the last write was a code task, pause 2–5s before publishing (known race).
8. `publishWorkflowRevision`, then **re-fetch and verify** task count, widget count, and
   rule count match the spec.

### Step 8 — Build report

Always emit a markdown build report:

- **Workflow URL + ID**, published revision ID
- **Built** ✅ — every task/field/rule with its timestamped evidence quote
- **Judgment calls** ⚠️ — medium-confidence items built with stated assumptions
- **Deferred** ⏭ — wishlist/hypothetical/low-confidence items and *why* each was skipped
- **Frames embedded** 🖼 — which tasks got screenshots, from which timestamps
- **Open questions** — conflicts between speakers, fuzzy roles, anything to confirm on the
  next call

The deferred list is a feature, not an apology — it's the agenda for the follow-up
conversation.

---

## Multi-source reconciliation

When given 2+ calls about the same process (e.g., different stakeholders):

1. Extract each call independently first.
2. Steps confirmed in both → `high` confidence.
3. Steps in one but not the other → keep, but note which stakeholder is the source.
4. Direct contradictions → build the simpler version, flag both versions in the report.
5. Different *lenses* on the same company (e.g., compliance team vs. operations team) often
  describe **different processes** — check the process census before merging anything.

---

## What this skill does NOT do

- Read SOP documents/spreadsheets — use the **documents** skill (they compose: run both,
  then reconcile).
- Read BPMN diagrams or static process images — use the **bpmn-and-images** skill.
- Strategic account research — use **gap-analysis** first when prepping a tailored demo;
  its JSON brief's `pain_feature_map` (gong-evidenced entries) is a prioritized signal
  list for this skill.
- Build directly in a customer's production org without explicit, named confirmation of
  org + folder.

---

## Files in this skill

| File | Purpose |
|---|---|
| `SKILL.md` | This file — the pipeline |
| `references/extraction-playbook.md` | Full verbal-pattern catalog, field-type guide, failure modes |
| `references/ps-build-conventions.md` | Process Street API build order + known gotchas |
| `scripts/transcribe.py` | Local Whisper transcription (audio + video) with timestamps |
| `scripts/extract_frames.py` | Frame extraction at timestamps or via scene detection |
| `examples/sample-transcript.md` | A sanitized sample call + the spec it should produce |
