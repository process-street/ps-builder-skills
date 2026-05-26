# /process-builder

Master skill for the Process Builders hackathon team. Provides context, objectives, and architecture so each individual skill builds with awareness of the whole system.

---

## Project Overview

Process Builders is a team within the PS AI hackathon (3-week sprint, May 2026) building an open-source repository of Claude Code skills that accelerate building Process Street workflows from prospect/customer source materials.

**The problem:** Solutions engineering currently receives documents from prospects (spreadsheets, PDFs, call transcripts, BPMN diagrams, images) and manually builds tailored demo environments in Process Street. This takes hours per prospect and requires deep product knowledge.

**The solution:** A composable set of skills that automate the pipeline from raw prospect input to a ready-to-demo Process Street environment — with strategic intelligence guiding what gets built and why.

---

## Architecture

The skills form a pipeline. They can run independently, but the intended flow is:

```
Prospect Research (existing: prep-notes, proposal skills)
        │
        ▼
┌──────────────────────┐
│   GAP ANALYSIS       │  ← Abdul's skill
│   (internal use)     │
│                      │
│   Determines:        │
│   - What to demo     │
│   - Why it matters   │
│   - Business framing │
│   - Technical reqs   │
└──────────┬───────────┘
           │
           ▼
     Gap Analysis Output (JSON brief)
           │
     ┌─────┼──────────┬──────────────┐
     ▼     ▼          ▼              ▼
┌─────────┐ ┌────────┐ ┌───────────┐ ┌──────────┐
│ DOC →   │ │ CALL → │ │ BPMN/IMG  │ │ PROMPT → │
│ WORKFLOW│ │ WKFLOW │ │ → WKFLOW  │ │ WKFLOW   │
│         │ │        │ │ & reverse │ │ (future) │
│ Ashley  │ │Lincoln │ │ Gabriel   │ │          │
└────┬────┘ └───┬────┘ └─────┬─────┘ └────┬─────┘
     │          │            │             │
     ▼          ▼            ▼             ▼
     Process Street MCP — creates workflows, tasks,
     form fields, data sets, conditional logic
```

### How skills connect

1. **Gap Analysis** runs first. It ingests all available prospect context (HubSpot, Gong, Gmail, web research, uploaded documents) and outputs a structured JSON brief that tells downstream skills exactly what to build and how to frame it.

2. **Document/Spreadsheet → Workflow** (Ashley) takes prospect-provided PDFs, SOPs, spreadsheets, checklists and converts them into Process Street workflows via the MCP. It reads the gap analysis output to know which documents to prioritize and what PS features to emphasize (conditional logic, photo capture, approval steps, etc.).

3. **Call Transcript → Workflow** (Lincoln) takes Gong transcripts or raw call recordings and extracts the processes described verbally, then builds them as PS workflows. Uses gap analysis output to filter for the highest-impact processes mentioned.

4. **BPMN/Image → Workflow** (Gabriel) takes visual process maps (BPMN diagrams, Visio exports, whiteboard photos, flowchart screenshots) and converts them into PS workflows, and can also reverse-engineer existing PS workflows into visual diagrams for prospect presentations.

### Shared conventions

- **Input format:** Each skill accepts its native input type + an optional `gap_analysis.json` file that provides strategic context.
- **Output:** Each skill creates workflows directly in Process Street via the MCP, AND produces a local summary of what was built (HTML or markdown).
- **Naming:** All workflows created follow the pattern: `[Company] - [Process Name] - DEMO`
- **Quality bar:** Every workflow must be mobile-testable, have at least one conditional logic branch, and include realistic sample data.

---

## Team

| Member | Skill | Input Types |
|---|---|---|
| Abdul | Gap Analysis (internal) | HubSpot, Gong, Gmail, web research, prospect docs |
| Ashley | Document → Workflow | PDFs, spreadsheets, Word docs, checklists |
| Lincoln | Call Transcript → Workflow | Gong transcripts, call recordings, meeting notes |
| Gabriel | BPMN/Image → Workflow | BPMN XML, Visio, flowchart images, whiteboard photos |

**Team lead:** Gabriel Labrada
**Meetings:** Tuesdays and Thursdays (recurring)
**Slack:** #ai-hackathon-process-builder
**Duration:** 3 weeks
**Judge:** Cameron (on return)
**Criteria:** Impact, Execution, Innovation

---

## Process Street MCP — what it can do today

The PS MCP server allows Claude to:
- Create, read, update workflows and workflow runs
- Create and configure form fields (text, dropdown, date, file upload, members, etc.)
- Set up conditional logic ("show step X if field Y = Z")
- Create data sets and records
- Manage task assignments and due dates
- Trigger workflow runs

**What it cannot do (as of May 2026):**
- Upload images or files into form fields
- Modify page/document content within workflows
- Access workflow run analytics/reporting
- Create integrations (Zapier/native) — these must be described, not built

Skills should build as much as possible via MCP, and document anything that requires manual setup.

---

## Business Context

**Why this matters commercially:**
- SEs currently spend 4–8 hours building tailored demos per prospect
- Faster demo turnaround = more demos per week = more pipeline
- Higher-quality demos (built from actual prospect data, not generic templates) = higher conversion
- The open-source repo becomes a GTM asset — prospects and partners can use it, which drives PS adoption

**Who uses this:**
- SEs (Shawntee, Jerry, Lincoln, Gabriel) for prospect demo prep
- AEs (Abdul, Jerry) for pre-call workflow mockups
- CS for customer onboarding (build their first workflows from existing docs)
- Partners for implementation projects

---

## How to use this skill

When invoked, this skill:
1. Explains the project architecture to whoever is asking
2. Provides context for building any of the individual skills
3. Can help scope new skills that fit into the pipeline
4. Can review a skill draft for consistency with the overall architecture

```
/process-builder                    # Overview and architecture
/process-builder scope [idea]       # Scope a new skill idea against the architecture
/process-builder review [skill]     # Review a skill for consistency
```

---

## Open Questions (to resolve with team)

- Where does the gap analysis JSON schema get versioned? (GitHub repo vs. local convention)
- Should skills write directly to a shared PS organization, or to each SE's personal org?
- How do we handle prospect-specific data cleanup for the open-source version?
- Does the BPMN → Workflow skill need to support Lucidchart/Miro exports specifically?
