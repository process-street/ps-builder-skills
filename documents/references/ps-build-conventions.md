# Process Street Build Conventions

The exact build order and known API behaviors for constructing workflows via the
Process Street Public API v1.1 / MCP server. Verified against the live OpenAPI spec
(`https://public-api.process.st/api/v1.1/docs/`) **and by a live end-to-end build test
(create → tasks → widgets → image upload → logic rule → publish → verify → delete) on
2026-06-04**. Both the **call-to-workflow** and **documents** skills follow this file.

---

## Connection

| | |
|---|---|
| REST base | `https://public-api.process.st/api/v1.1` |
| Auth | `X-API-Key: <key>` header (NOT Basic auth) |
| Docs | `https://public-api.process.st/api/v1.1/docs/` (OpenAPI at `docs/openapi.json`) |
| MCP | Process Street MCP server exposes the same operations as tools |

Prefer MCP tools when connected; REST is the fallback. Never log or echo the API key.

---

## Build order (do not deviate)

1. **`createWorkflow`** — creates the shell. ⚠️ The shell auto-publishes an **empty
   Finished revision (v0.0)** — there is no draft yet.
2. **`createWorkflowRevision`** — creates the draft revision you'll build into. Only one
   draft can exist at a time. All subsequent calls use this draft's `revisionId`.
3. **Tasks, in order** — `createWorkflowRevisionTask` per task.
   - Order with the `position` object: `{"type": "Bottom"}` (default),
     `{"type": "Top"}`, or `{"type": "After", "taskId": "<id>"}`. Build in final order.
   - The discriminator is **`taskType`**, not `type`: `Standard`, `Approval`, `AI`, `Code`.
   - **Don't prefix task names with numbers** ("1. ", "Step 2:") — the UI already shows
     position numbers and they go stale when order changes.
   - Tasks meant to be revealed by logic rules: create with `hiddenByDefault: true`.
4. **Widgets per task** — `createWorkflowRevisionTaskWidget`.
   - Widget `type` is one of: `FormField` (with a `fieldType` sub-discriminator), `Text`,
     `Image`, `File`, `Video`, `Embed`, `CrossLink`.
   - Position with the `position` object (`Top` / `Bottom` / `After {widgetId}`).
   - **Select/MultiSelect/MultiChoice options** go in `config.items` as
     `[{"name": "Option A"}, ...]` — the server assigns each item's `id`. Bare strings
     are rejected.
   - **Updates are full-replacement PUTs.** Read the current widget, merge your change,
     send the whole body back. Partial bodies erase fields.
5. **Image/File content** — create the widget first, then upload to it:
   `POST /workflows/{workflowId}/revisions/{revisionId}/tasks/{taskId}/widgets/{widgetId}/upload`
   - multipart/form-data with `file`, **or** JSON `{"fileBase64": {"content": "<b64>", "filename": "frame.jpg"}}`
   - Verified live: a 20 KB JPEG frame attached cleanly and renders on the task.
   - Respect file-size limits; JPEG screenshots at 1280px wide are plenty.
6. **Logic rules** — `createWorkflowRevisionLogicRule`.
   - Shape: `action` (`Show` | `Hide`), `condition`, `targets`.
   - Condition nests as OR-of-AND-groups:
     `{"or": [{"and": [{"widgetId": "<field>", "operator": "Is", "value": "Out of Network"}]}]}`
   - Operators (live-verified enum): `Is`, `IsNot`, `HasAnyValue`, `HasNoValue`, `IsGreaterThan`, `IsLessThan`. Empty-check is `HasNoValue` (no `value` needed) — `IsEmpty`/`Contains` are rejected.
   - Select values are referenced by the option **name** string.
   - `targets` requires **both** keys, even when one is empty:
     `{"taskIds": [...], "widgetIds": []}` — omitting `widgetIds` is a 400
     (`Field [targets.widgetIds] is required`).
   - **Dedupe before publish** — the API happily accepts duplicate rules and they cause
     confusing runtime behavior. Same condition + same targets = delete the duplicate.
7. **Task config** — `updateWorkflowRevisionTaskConfig` for due-date rules, required flags,
   stop-task behavior. Due dates are **relative rules**, never hardcoded dates.
8. **Approvals** — create the task with `taskType: "Approval"`. Voting and mandatory-voter
   modes require explicit thresholds — don't rely on defaults.
9. **Data Sets** — `createDataSet`, then add records, then wire the linked dropdown on the
   workflow. Date-type values must be ISO-8601 (`YYYY-MM-DD`); a single malformed date can
   fail an entire batch with HTTP 400.
10. **Code tasks** (if any) — the runtime exposes `inputData` and `outputData` as **globals**:
    read `inputData.x`, assign `outputData.x = value`. No `context` wrapper, no
    `return {outputData}`. For async work use the assignment pattern, not a return.
11. **Publish** — `publishWorkflowRevision`. If the last write was a code-task widget,
    wait 2–5 seconds first (known trailing-write race).
12. **Verify** — re-fetch the revision's tasks/widgets/rules; confirm the revision status
    flipped to Finished and that task count / widget count / rule count match the spec.
    Report any mismatch instead of declaring success.

---

## Known gotchas (each verified live or burned a real build)

| Gotcha | Fix |
|---|---|
| New workflow has no draft — v0.0 auto-publishes empty | `createWorkflowRevision` before any task/widget call |
| Task order is set at create | Use `position` (`Top`/`Bottom`/`After {taskId}`); build in final order |
| Numeric task-name prefixes go stale | Don't number task names; the UI shows positions |
| Widget PUT replaces entire body | Read → merge → PUT full shape |
| `targets.widgetIds` required even when empty | Always send `{"taskIds": [...], "widgetIds": []}` |
| Logic operator enum (live-verified) | `Is`, `IsNot`, `HasAnyValue`, `HasNoValue`, `IsGreaterThan`, `IsLessThan` — empty-check is `HasNoValue` |
| Duplicate logic rules accepted silently | Dedupe before publish |
| Select options as bare strings rejected | `config.items: [{"name": "..."}]` — server assigns ids |
| Code task IO | `inputData`/`outputData` globals; never `inputs`/`outputs`/`return` |
| Trailing code-task race at publish | Pause 2–5s before `publishWorkflowRevision` |
| Date fields reject `MM/DD/YYYY` | ISO-8601 only; one bad date 400s the batch |
| `searchWorkflowRuns` page cap | 200 per page — paginate |
| PUT semantics everywhere | Full replace, not merge — applies to tasks and widgets alike |
| Old pip rejects `--break-system-packages` | If whisper install fails, retry: `pip3 install --user openai-whisper` |

---

## Idempotency

If a build is interrupted and re-run:

- Match on workflow **name + folder** — reuse the existing workflow, don't duplicate.
- List existing tasks/widgets/rules first; create only what's missing.
- Use deterministic, descriptive task names (`Intake — Receive Request`) so diffs are
  trivial — but no numeric prefixes (see Build order).

---

## Safety

- Confirm org + folder with the user before the first write.
- Default to a sandbox/demo folder; a customer's production folder requires explicit,
  named confirmation.
- `dry-run` mode must never call a write endpoint.
- Never place API keys, tokens, or customer-identifying data in widget bodies, task names,
  or commit messages.
