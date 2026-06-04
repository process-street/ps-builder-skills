# Documents → Workflow (and back)

**`document-to-workflow`** — turn written process artifacts into built, published
Process Street workflows:

- 📕 **PDF** — SOPs, regulatory procedures, signed policies
- 📘 **DOCX** — procedure docs, checklists
- 📊 **XLSX / CSV** — field specs, lookup tables, per-region rule matrices (every tab examined)
- 📄 **TXT / MD** — informal process notes

What makes it more than a converter:

- **Lookup-table detection** — spreadsheet tabs that are really reference data become
  **Data Sets** with linked dropdowns, not hardcoded options
- **Rule matrices → conditional logic** — per-state/per-type requirement tabs become logic
  rules, one per row
- **RACI tables → assignments and approvals** — R becomes the assignee, A becomes the approver
- **Compliance-aware** — "must/shall" language stays load-bearing; signature blocks become
  approval tasks; retention language is preserved on the task
- **Cited** — every task, field, and rule carries its source (file + page/section/cell)
- **Staleness flags** — old revision dates, retired tools, and numbering gaps get flagged,
  never silently "fixed"
- **Reverse mode** — export an existing workflow back out as a clean, numbered SOP document

## Contents

| File | Purpose |
|---|---|
| [`SKILL.md`](SKILL.md) | The skill — full pipeline, both directions |
| [`references/ps-build-conventions.md`](references/ps-build-conventions.md) | PS API build order + gotchas |

## Quick start

```
# Install (Claude Code)
cp -r documents ~/.claude/skills/document-to-workflow

# Connect the Process Street MCP server (or have a PS API key ready), then:
#   "Build a workflow from this SOP: ~/Downloads/inspection-procedure.pdf"
#   "Convert rules.xlsx — the States tab drives the conditional logic"
#   "Export workflow <id> as an SOP document"
```

Pairs with the other skills in this repo: **gap-analysis** for strategic context first;
**meeting-transcripts-and-recordings** when the same process was also described on a call —
reconciling the two is where the interesting findings live.
