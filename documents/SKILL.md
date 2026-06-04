---
name: document-to-workflow
description: >
  Turn process documents — PDF SOPs, DOCX procedures, XLSX/CSV spreadsheets, TXT files —
  into fully built, published Process Street workflows. Detects lookup tables and converts
  them to Data Sets, maps field-spec sheets to form fields, converts RACI/role tables to
  assignments, turns review/sign-off language into approval tasks, and handles multi-tab
  spreadsheets with per-region or per-type rules as conditional logic. Also runs in
  reverse: export an existing workflow to a clean SOP document.
  Use whenever the user shares an SOP, procedure doc, checklist, or process spreadsheet and
  says anything like "build a workflow from this document", "turn this SOP into a process",
  "convert this spreadsheet", or "document to workflow".
---

# Document → Workflow

You are converting a written process artifact into a working Process Street workflow.
Documents are *more structured* than calls but *lie differently*: they describe the process
as someone wrote it down (often years ago), not necessarily as it runs today. Extract
faithfully, flag staleness signals, and never invent steps the document doesn't contain.

The output is a runnable workflow plus a build report that cites the page/section/cell
every element came from.

---

## Supported inputs

| Format | Typical content | Notes |
|---|---|---|
| **PDF** | SOPs, regulatory procedures, signed policies | Read directly; OCR caveats below |
| **DOCX** | Procedure docs, checklists, templates | Headings/numbering carry the structure |
| **XLSX** | Field specs, lookup tables, per-region rule matrices, checklist trackers | **Every tab is examined separately** |
| **CSV** | Lookup/reference data, exported checklists | Usually becomes a Data Set |
| **TXT / MD** | Informal process notes | Treat like a loose SOP |

Multiple documents about the same process are welcome — see *Multi-document reconciliation*.

## Prerequisites

- **Process Street access** — the Process Street MCP server, or a PS API key
  (`https://public-api.process.st/api/v1.1`, header `X-API-Key`).
- Spreadsheet parsing: prefer reading sheets programmatically (e.g. `python3` + `openpyxl`
  or `pandas`) over eyeballing — cell-level fidelity matters for lookup tables.

---

## Pipeline

### Step 0 — Intake

1. **Inventory the documents** — list every file, and for spreadsheets every tab, before
   reading any of them deeply. State what each appears to be.
2. **Target** — confirm the Process Street organization + folder. Never build into a
   production folder without explicit confirmation.
3. **Build mode** — `live` (default) or `dry-run` (spec + report only).
4. **One process or several?** A document set often covers multiple processes (e.g., an
   SOP manual). Confirm scope with the user before merging anything.

### Step 1 — Classify each artifact

Every document/tab gets one of these roles. The role determines how it's used:

| Role | Recognize it by | Becomes |
|---|---|---|
| **Procedure narrative** | Numbered steps, imperative verbs, "Purpose / Scope / Procedure" headings | The task sequence |
| **Lookup table** | 2–5 columns, one key-like column with unique values, rows are data not steps (e.g. region → owner, type → SLA) | **Data Set** + linked dropdown |
| **Field spec** | Columns like Field Name / Type / Required / Validation | Form fields, mapped 1:1 |
| **Rule matrix** | Rows or tabs per region/state/type, each with different requirements | Dropdown + conditional logic rules per value |
| **RACI / roles table** | Roles vs. activities grid (R/A/C/I) | Task assignments (R) + approvals (A) |
| **Revision/approval history** | Version, date, approver columns | Signal: the doc takes sign-off seriously → expect approval gates in the procedure |
| **Reference/appendix** | Definitions, glossaries, regulation citations | Text widgets on relevant tasks; regulation refs become required evidence fields |

The most valuable single move in this skill: **spotting that a spreadsheet tab is a lookup
table and building it as a Data Set** instead of hardcoding its values into dropdowns or
task names. Lookup tables change; Data Sets are editable without touching the workflow.

### Step 2 — Extract the procedure

From procedure narratives:

- **Numbered/lettered steps** → tasks, in document order. Keep the document's section
  reference for traceability, but put it at the **end** of the name in parentheses
  (`Verify supplier certificate (SOP §3.2)`) — never as a numeric prefix; the PS UI
  numbers tasks by position and prefixes go stale on reorder.
- **Heading levels** → phases. An H2 with five numbered steps under it is a phase of five
  tasks, not one task.
- **"must / shall / required"** → required form fields or stop-tasks. Regulatory language is
  load-bearing — never soften it.
- **"reviewed and approved by..."** / signature lines / approval columns → approval tasks.
  Multiple named signers → voting or mandatory-voters config (ask which).
- **"if / when / unless / except"** → conditional logic rules. Tables of conditions →
  one rule per row.
- **"attach / retain / record"** → File/MultiFile fields. Retention language goes in a task
  text widget — it matters for compliance users.
- **Cross-references** ("see SOP-104") → CrossLink widgets if the target exists in PS,
  otherwise a note in the build report.
- **Frequencies** ("quarterly", "every batch") → scheduled workflow vs. per-run trigger;
  confirm with the user.

For each extracted element record **document evidence**: filename + page/section/cell
(e.g. `inspection-sop.pdf p.4 §3.2`, `rules.xlsx tab "States" B7`). No citation, no build.

### Step 3 — Staleness & conflict checks

Documents drift from reality. Flag, don't silently fix:

| Signal | Action |
|---|---|
| Revision date > ~2 years old | ⚠️ in report: "verify steps still current" |
| References to retired tools/systems | Build the step, flag the tool reference |
| Steps that contradict each other across documents | Build the more recent document's version; flag the conflict |
| A numbered step that's clearly missing (3, 4, 6...) | Flag the gap; do not invent step 5 |
| Role names that appear nowhere else in the org | Group-assign + open question |

### Step 4 — Design the workflow spec (approval gate)

Same spec shape as the call-to-workflow skill (see `references/ps-build-conventions.md`),
with document citations in the `evidence` slots:

```yaml
workflow:
  name: "<Team> — <Process Name>"
  classification: OPS | DOCS | HYBRID
  tasks:
    - name: "Receive and log the request (SOP §3.1)"
      assignee_role: "Coordinator"          # from RACI: R
      evidence: "intake-sop.pdf p.3 §3.1"
      fields:
        - { type: "Text", name: "Request ID", required: true }   # field-spec tab row 2
  logic_rules:
    - when: { field: "State", op: "Is", value: "CA" }
      then: [ { action: "Show", task: "CA Addendum Review" } ]
      evidence: "rules.xlsx tab 'States' row 5"
  data_sets:
    - name: "Region → Owner"
      source: "assignments.xlsx tab 'Coverage' (22 rows)"
  approvals:
    - task: "Final sign-off (SOP §4.0)"
      mode: "mandatory_voters"              # two named signers on the signature block
      evidence: "intake-sop.pdf p.7 signature block"
```

Present a readable summary and **wait for explicit approval before building live**.

### Step 5 — Build

Follow `references/ps-build-conventions.md` exactly — same build order, same gotchas as
every skill in this repo. Document-specific notes:

- **Data Sets first** when dropdowns link to them, then the workflow that references them.
- Data Set records from spreadsheets: dates must be ISO-8601 (`YYYY-MM-DD`) — one
  `MM/DD/YYYY` cell fails the whole batch. Normalize before upload.
- Preserve the document's section numbers in task names — auditors and process owners
  navigate by them.

### Step 6 — Build report

- **Workflow URL + ID**, published revision ID
- **Built** ✅ — every element with its document citation
- **Flags** ⚠️ — staleness, retired tools, conflicts, gaps in numbering
- **Data Sets created** — row counts vs. source rows (must match)
- **Not built** ⏭ — anything in the document that didn't map to a PS primitive, and why
- **Open questions** — fuzzy roles, frequency ambiguities, cross-references to missing SOPs

---

## Reverse direction: Workflow → Document

When asked to export ("turn this workflow into an SOP / document"):

1. Fetch the full workflow structure (tasks, widgets, rules, assignments, approvals).
2. Render as a clean SOP: Purpose → Scope → Roles → Procedure (numbered, one section per
   task) → Decision rules (one row per logic rule, in plain English) → Approvals →
   Field reference (appendix table).
3. Output markdown by default; offer DOCX/PDF conversion (e.g. `pandoc`) if tooling exists.
4. Include a generated-from line (workflow ID + revision + date) so the doc can be traced
   back and regenerated.

---

## Multi-document reconciliation

1. Classify all artifacts first (Step 1) — narrative vs. data vs. spec.
2. The **narrative** drives task structure; **spreadsheets** drive fields, data sets, and
   logic values. They complement more often than they conflict.
3. On conflict (SOP says weekly, tracker shows daily): newer artifact wins, flag both.
4. If a call transcript about the same process exists, run **call-to-workflow** on it
   separately and reconcile the two specs — what people *say* and what's *written down*
   differing is itself a finding worth reporting.

---

## What this skill does NOT do

- Read call transcripts/recordings — **meeting-transcripts-and-recordings** lane.
- Read BPMN/diagrams/images — **bpmn-and-images** lane (a flowchart embedded in a PDF can
  be handed to that skill as an image).
- Strategic account research — **gap-analysis**; its JSON brief's
  `source_documents[].step_breakdown` is a pre-mapped spec this skill can build from
  directly.
- Invent process steps. If the document doesn't say it, it goes in *Open questions*, not
  in the workflow.

---

## Files in this skill

| File | Purpose |
|---|---|
| `SKILL.md` | This file |
| `references/ps-build-conventions.md` | PS API build order + gotchas (shared repo convention) |
