---
name: chrome-recording-to-workflow
description: Convert a recording.md exported by the PS Builder Chrome Extension into a Process Street workflow via the Process Street MCP.
---

# Chrome Recording → Process Street Workflow

This skill tells Claude how to consume a `recording.md` file (produced by the PS Builder Chrome Extension) and create a matching Process Street workflow using the **Process Street MCP**.

## When to use

Trigger this skill when:

- The user provides a `recording.md` from a `ps-recording-*` folder
- The user asks to "turn this recording into a workflow", "build a PS workflow from this browser session", or similar
- The folder contains a `recording.md` plus a `screenshots/` subfolder

If the Process Street MCP is not connected, stop and tell the user to enable it first. **Do not fall back to writing PS API calls by hand or generating a JSON brief.** This skill exists specifically to use the MCP.

## Inputs

```
ps-recording-<id>/
  recording.md            # required — prompt + structured event log
  screenshots/
    step-001.png          # one per captured event (optional, not all events have one)
    step-002.png
    ...
```

`recording.md` has these sections (always present, in order):

1. Header (session id, start/end timestamps, event count)
2. `## Instructions for Claude` — high-level intent (this skill supersedes them with the more concrete guidance below)
3. `## Events` — one `### Event N — <type>` block per captured event, with element + form_field metadata and an optional screenshot reference
4. `## Raw events (JSON, screenshots stripped)` — the same events as a JSON array, for reliable programmatic access

**Prefer parsing the JSON appendix over the rendered event sections** — it's the source of truth and easier to reason about.

## Process Street MCP tools to use

| Step | Tool | Purpose |
| --- | --- | --- |
| 1 | `mcp__claude_ai_Process_Street__listFolders` | Find or confirm the target folder |
| 2 | `mcp__claude_ai_Process_Street__createWorkflow` | Create the workflow shell. Returns a draft revision — use its id for subsequent calls. |
| 3 | `mcp__claude_ai_Process_Street__createWorkflowRevisionTask` | One call per logical task |
| 4 | `mcp__claude_ai_Process_Street__createWorkflowRevisionTaskWidget` | Add Text widgets (instructions) and FormField widgets (inputs) to each task |
| 5 | `mcp__claude_ai_Process_Street__publishWorkflowRevision` | Finalize the draft |

`createWorkflow` already opens a draft revision under the hood. Do **not** call `createWorkflowRevision` immediately after — that's only for editing a workflow that already has a finished revision.

## Algorithm

### 1. Parse and clean the events

Read `recording.md`, extract the JSON array under `## Raw events`. Drop noise before grouping:

- Drop `navigation` events whose URL only differs by a fragment (`#...`) or query-string-only change from the previous URL
- Drop consecutive duplicate `click` events on the same selector within 1 second (debounce double-clicks)
- Drop `input` events on hidden / `type="hidden"` fields
- Drop password fields (they're already redacted but still drop them from the task spec — they leak no value to a workflow consumer)

### 2. Group events into tasks

A task represents one logical step in the process. Default heuristic:

- A `navigation` event starts a new task
- All `click`, `input`, `submit` events until the next `navigation` belong to that task
- If a page has more than ~8 inputs / clicks, consider splitting into multiple tasks at form-section boundaries (a `submit` event is a strong split signal)
- If there is no initial `navigation` (recording started after the page loaded), treat the first observed URL as the initial task

### 3. Name and describe each task

For each grouped task:

- **Name** — derive from the dominant action. Examples:
  - Navigation to `app.process.st/workflows/new` + click "Create" → "Create workflow"
  - Multiple inputs on a `task_name` + `description` form → "Fill in task details"
  - Click on "Add Task" → "Add a task"
  - **Never prefix with numbers** (`1. `, `Task 1:`). PS auto-numbers in the UI.
- **Description (Text widget)** — short prose: what page the user was on, what they clicked, key form values. Reference the screenshot if a relevant one was captured: `See screenshots/step-014.png`. Don't dump raw selectors — those are not useful to a human running the workflow.

### 4. Detect and emit form fields

For each grouped task, look at its `input` events (and `click` events on `select`, `input[type=file]`, etc.). Map each unique form field to a PS form-field widget:

| HTML field | PS `fieldType` |
| --- | --- |
| `<input type="text">`, no type | `Text` |
| `<input type="email">` | `Email` |
| `<input type="url">` | `Url` |
| `<input type="number">` | `Number` |
| `<input type="date">`, `datetime-local` | `Date` |
| `<input type="file">` (single) | `File` |
| `<input type="file" multiple>` | `MultiFile` |
| `<input type="checkbox">` (one) | `MultiChoice` with one item |
| `<input type="checkbox">` (group, same `name`) | `MultiChoice` with N items |
| `<input type="radio">` (group, same `name`) | `Select` |
| `<select>` | `Select` |
| `<select multiple>` | `MultiSelect` |
| `<textarea>` | `Textarea` |
| `password` | **skip entirely** |

For each field, set:
- `label` — use the `form_field.label` from the recording (it's the accessible name). Fall back to `form_field.placeholder` or `form_field.name`.
- `defaultValue` — **don't** copy the recorded value as default; it was the demonstrator's input, not a sensible default. Only set a default if the value looks like a true static default (e.g., a country code preselected on every visit).

### 5. Create the workflow

```
folders = listFolders()                                                 // pick the right one with the user
wf = createWorkflow(
  name: <inferred name>,
  folderId: <chosen>,
  shareLevel: "None",
  runLinkShareLevel: "Organization",
  allowComments: true,
  sharedRunsByDefault: false,
)
// wf returns { id, draftRevisionId } (or equivalent — see actual response shape)

for each task in tasks:
  t = createWorkflowRevisionTask(
    workflowId: wf.id,
    revisionId: wf.draftRevisionId,
    name: task.name,
    taskType: "Standard",
  )
  createWorkflowRevisionTaskWidget(
    workflowId: wf.id, revisionId: wf.draftRevisionId, taskId: t.id,
    createworkflowwidgetrequest: { type: "Text", content: task.description }
  )
  for each ff in task.form_fields:
    createWorkflowRevisionTaskWidget(
      workflowId: wf.id, revisionId: wf.draftRevisionId, taskId: t.id,
      createworkflowwidgetrequest: { type: "FormField", fieldType: ff.psType, label: ff.label, ...ff.configAndConstraints }
    )

publishWorkflowRevision(workflowId: wf.id, revisionId: wf.draftRevisionId)
```

After publishing, report the workflow URL to the user (constructed from the returned workflow id, or just the id if the URL isn't in the response).

### 6. Confirm before publish

Before calling `publishWorkflowRevision`, summarize for the user what was built (task count, form-field count, workflow name + folder) and ask for go-ahead. The draft is safe to leave unpublished; it's recoverable.

## Naming the workflow

Pick the name in this order of preference:

1. The user's explicit instruction ("call it 'New customer onboarding'")
2. The page title of the page where the *first meaningful interaction* (click/input) happens — strip trailing site names like " — Process Street"
3. A noun phrase from the first interactive element's accessible name (e.g. "Create workflow" if the first click is on a "Create workflow" button)
4. Fallback: `Recorded workflow <YYYY-MM-DD>`

## Edge cases

- **No `navigation` events at all** — single-page recording. Group everything into one task; ask the user for a name.
- **Same form field appears in multiple tasks** — emit it on the task where the user *first interacted* with it. Don't duplicate across tasks.
- **A `click` on a button labeled "Submit" / "Save" / "Create"** at the end of a group is a workflow-meaningful action. Keep it in the description even though it's not a form field.
- **Recording is suspiciously short (< 3 events)** — surface this to the user before creating anything; they may have started recording too late.
- **`form_field.value` is the placeholder text** (some sites send change events with placeholders) — heuristic: if `value === placeholder`, treat as empty.

## What to NOT do

- Don't try to upload screenshots as PS Image widgets via the MCP. The Image widget schema doesn't accept a URL/file directly here; it expects an attachment flow that's out of scope for this skill. Reference screenshots by relative path inside Text widget content instead.
- Don't replay the recording (don't try to use Playwright / browser-use / etc. to re-execute it). The skill's only job is structural translation: events → PS workflow.
- Don't preserve the recorded values as form-field defaults. They were demo inputs, not defaults.
- Don't number task names. PS UI auto-numbers.
- Don't invent fields the recording doesn't show. If the user wants additional fields, they can ask.

## Example invocation

```
User: I just dropped a recording into ./ps-recording-a1b2c3d4/. Can you turn it into a PS workflow?
Claude:
  1. Reads ./ps-recording-a1b2c3d4/recording.md
  2. Parses the JSON appendix → 23 events
  3. Drops 4 noise events → 19
  4. Groups into 5 tasks based on 5 navigations
  5. Maps 7 form fields (3 Text, 2 Select, 1 Email, 1 Date)
  6. Calls listFolders, picks one with the user
  7. Calls createWorkflow → draft id
  8. Loops createWorkflowRevisionTask + createWorkflowRevisionTaskWidget for each task
  9. Summarizes: "5 tasks, 7 form fields, in folder 'Demo'. Publish?"
  10. On confirm, publishWorkflowRevision → returns workflow URL
```

See `examples/recording-sample.md` for a small reference recording.
