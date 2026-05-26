# Gap Analysis

Analyze a prospect's situation and produce an internal gap analysis that determines what to demo, why, how to frame it, and what to build — before any workflow construction begins.

This is the strategic intelligence layer for the Process Builders pipeline. It runs BEFORE the document-to-workflow, transcript-to-workflow, or BPMN-to-workflow skills.

## What it does

Given a company name and/or contact email, the skill:

1. **Researches** the prospect in parallel across all available sources (HubSpot, Gong, Gmail, Slack, Apollo, web, Google Calendar)
2. **Analyzes** any documents the prospect sent (SOPs, checklists, spreadsheets) — extracting every step, decision point, and data capture moment
3. **Classifies** the use case as OPS, DOCS, or HYBRID — this determines the entire demo shape
4. **Maps** every pain point to a specific PS feature with evidence and demo approach
5. **Architects** the demo — what to build, what to show live vs. pre-build, competitive positioning
6. **Frames** the business narrative — current state, cost of inaction, objection prep

## Output

Two artifacts:

- **JSON brief** (`/tmp/<company_slug>_gap_analysis.json`) — structured data that downstream builder skills consume to know what to build
- **HTML document** (`/tmp/<company_slug>_gap_analysis.html`) — formatted internal brief for the SE team with build specs, pain-to-feature map, and demo architecture

## Installation

### 1. Copy commands to your Claude Code commands directory

```bash
cp commands/gap-analysis.md ~/.claude/commands/
cp commands/process-builder.md ~/.claude/commands/
```

Or for project-scoped usage:
```bash
cp commands/*.md your-project/.claude/commands/
```

### 2. (Optional) Set up research scripts

The scripts provide offline search of local Gong transcripts, Gmail threads, and Apollo enrichment. They're optional — the skill will use MCP tools (HubSpot, Slack, Gmail, Calendar) when available and skip anything that isn't configured.

```bash
# Apollo enrichment (requires API key)
export APOLLO_API_KEY="your-key-here"

# Gong local search (requires transcript files)
# Run your Gong extract script first to populate scripts/gong_output/transcripts/

# Gmail local search (requires thread files)
# Run your Gmail extract script first to populate scripts/gmail_output/threads/
```

### 3. MCP connections (recommended)

The skill is most powerful when Claude Code has MCP connections to:
- **HubSpot** — contact/company/deal lookup, notes
- **Slack** — channel search, Gong summaries, SE threads
- **Gmail** — thread search, attachment download
- **Google Calendar** — meeting details, attendees
- **Process Street** — for downstream skills to build workflows

The skill uses whatever is available and skips the rest.

## Usage

```
/gap-analysis Tree Masters of Tennessee lindsay@treemasterstn.com
/gap-analysis westinghouse
/gap-analysis
```

## How it connects to other skills

The gap analysis JSON is the input contract for all downstream builder skills:

| Downstream Skill | What it reads from the JSON |
|---|---|
| Document → Workflow | `source_documents[].step_breakdown` — pre-digested build spec |
| Transcript → Workflow | `pain_feature_map` where `evidence_source = "gong"` |
| BPMN/Image → Workflow | `source_documents` where `type = "image"` |

All downstream skills also use `business_framing`, `competition`, and `use_case_classification` to inform how they build.

## File structure

```
gap-analysis/
├── README.md                          # This file
├── commands/
│   ├── gap-analysis.md                # The main skill prompt
│   └── process-builder.md             # Project architecture context
└── scripts/
    ├── apollo_research.py             # Apollo person + company enrichment
    ├── gong_search.py                 # Local Gong transcript search
    └── gmail_search.py                # Local Gmail thread search
```
