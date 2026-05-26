# /gap-analysis

Analyze a prospect's situation and produce an internal gap analysis that determines what to demo, why, how to frame it, and what to build — before any workflow construction begins.

This is the strategic intelligence layer for the Process Builders pipeline. It runs BEFORE the document-to-workflow, transcript-to-workflow, or BPMN-to-workflow skills.

---

## When to use

Run this skill when:
- You have an upcoming demo or tailored walkthrough for a prospect
- You've completed discovery and have research context (Gong, HubSpot, docs from the prospect)
- You need to decide what to build in Process Street for a demo environment
- You want a structured internal brief that the SE team can work from

**This is an internal document. It is never shared with the prospect.**

---

## Inputs

The skill accepts a company name and/or contact email. It will automatically pull from all available sources:

### Required (at least one)
- Company name or domain
- Contact email address

### Auto-gathered
- **HubSpot:** contact properties, company properties, deal stage, form submission message, associated notes
- **Gong:** call transcripts (via `gong_search.py` or Gong MCP if available), AI-generated summaries from #gong-sales Slack channel
- **Gmail:** email threads with the prospect (via `gmail_search.py` or Gmail MCP), including attachments
- **Slack:** #opp-[company] channel, #gong-sales summaries, #solutions-engineering threads, #sales mentions
- **Web:** company overview, industry context, recent news, team size, tech stack signals
- **Apollo:** contact title, seniority, company headcount/revenue/industry (via `apollo_research.py`)
- **Calendar:** upcoming meeting details, attendees, prior meeting history

### Optional (if the prospect sent materials)
- PDF SOPs, checklists, or process documents (attached to emails or shared via Drive)
- Spreadsheets with process data
- Screenshots or diagrams of their current workflows

---

## Execution

### Step 1 — Research (parallel)

Run ALL available research sources in parallel. Use whichever tools are configured in your environment:

**Scripts (if installed):**
```bash
python3 scripts/apollo_research.py "FIRST" "LAST" "DOMAIN" "COMPANY"
python3 scripts/gong_search.py "FIRST" "LAST" "DOMAIN" "COMPANY"
python3 scripts/gmail_search.py "FIRST" "LAST" "EMAIL" "DOMAIN"
```

**MCP tools (if connected):**
- HubSpot MCP: search contacts, companies, notes, deals
- Slack MCP: search channels, threads, Gong summaries
- Gmail MCP: search threads, download attachments
- Google Calendar MCP: upcoming meetings, attendees

**Always run:** WebSearch for company overview, industry context, recent news.

If the prospect sent documents (PDFs, spreadsheets), download and extract their content. These are critical — they show you exactly how the prospect thinks about their processes today.

### Step 1b — Document Deep Analysis (if materials exist)

If the prospect provided ANY documents — SOPs, checklists, spreadsheets, process maps, sample procedures — this step is **not optional**. The documents are the single richest input into the gap analysis. They show you how the prospect actually thinks, what language they use, what they care about enforcing, and where their current process breaks down.

**For EACH document, produce a structured breakdown:**

1. **What is this document?** Type (SOP, checklist, script, policy, procedure, form), who uses it, when it's used, how often.

2. **Step-by-step extraction:** Walk through the document and extract every discrete step, decision point, and data capture moment. Not a summary — the actual steps. For example:
   - "Step 1: Greet the customer by name" → PS: text display or script page
   - "Step 3: If emergency, transfer to on-call manager" → PS: conditional logic branch
   - "Step 7: Record caller's property address" → PS: form field (address/text)
   - "Step 9: Take before photo of job site" → PS: file upload field (photo capture)

3. **PS feature mapping per step:** For each extracted step, identify the specific PS feature:
   - Static instruction → Page content or task description
   - Data entry → Form field (specify type: text, dropdown, date, number, email, phone)
   - Decision/branch → Conditional logic ("if X then show Y")
   - Sign-off/approval → Approval step with role assignment
   - Photo/file requirement → File upload field
   - Calculation or threshold → Form field with validation or conditional logic
   - Handoff to another person → Task assignment (dynamic or role-based)
   - Reference lookup → Data set integration
   - External system action → Integration note (Zapier/API)

4. **Conditional logic opportunities:** Identify every branching point — explicit ("if emergency...") and implicit (different paths for different job types, customer types, escalation levels). These are the moments that differentiate PS from a static document.

5. **Gaps and improvements:** What's missing from the document that PS could add?
   - Timestamp enforcement (they say "call 811 before digging" but have no proof it happened)
   - Photo evidence (they describe a visual check but don't capture it)
   - Accountability (a step says "verify" but doesn't track who verified or when)
   - Automation opportunities (a step says "notify the manager" — PS can auto-assign)
   - Data validation (they accept free-text where a dropdown would prevent errors)

6. **Demo narrative hook:** What's the one sentence that connects this document to the prospect's stated pain? This becomes the anchor line when showing this workflow in the demo. Example: "This is your call sheet — but now every call follows it, and you can see who deviated and when."

**For DOCS use cases specifically, also analyze:**
- Document header/footer structure (revision number, effective date, author, approver, classification)
- Section numbering convention (1.0, 1.1, 1.1.1 or similar)
- Cross-references to other documents or regulatory requirements
- Review/approval signature blocks — who signs, in what order
- Change history table format
- Distribution/acknowledgment requirements

**Output format per document:**

```
DOCUMENT: [filename]
TYPE: SOP | checklist | script | procedure | policy | form
USED BY: [role/team]
FREQUENCY: daily | per-job | per-event | periodic | on-change
STEPS EXTRACTED: [count]
CONDITIONAL BRANCHES: [count]
FORM FIELDS IDENTIFIED: [count by type]
PS WORKFLOW NAME: "[Company] - [Process Name] - DEMO"
DEMO PRIORITY: P1 | P2 | P3
ANCHOR LINE: "[the one sentence that sells this workflow]"
BUILD METHOD: pre-build | live-build
ESTIMATED BUILD: [minutes]

STEP BREAKDOWN:
1. [Step description] → [PS feature] | [field type if applicable]
2. [Step description] → [PS feature] | [field type if applicable]
   ↳ IF [condition] → [branch to step X / show additional fields]
...

GAPS & IMPROVEMENTS:
- [What's missing + what PS adds]
...

INTEGRATION POINTS:
- [Step N]: [External system action — Zapier/API to Jobber, Slack notification, etc.]
...
```

This breakdown feeds directly into Step 3 (pain-to-feature mapping — document evidence is the strongest evidence), Step 4 (demo architecture — the build spec IS this breakdown), and Step 5 (business framing — anchor lines become the narrative).

### Step 2 — Situational Analysis

From the research, determine:

**Company profile:**
- What does the company do? Industry, size, geography, growth stage
- What compliance/regulatory requirements apply?
- What tools do they currently use? (CRM, project management, field service, HRIS, etc.)
- Are they growing, restructuring, preparing for acquisition, or stable?

**Contact profile:**
- Who is the champion? Title, seniority, what they care about
- Who is the economic buyer? Are they engaged?
- Who else is involved? Technical evaluators, end users, blockers?

**Deal context:**
- What stage is this? Discovery, demo, trial, evaluation, negotiation?
- How many prior calls? What was discussed?
- What competition exists? What have they evaluated?
- What's the timeline driver? (Audit, launch, board deadline, seasonal pressure?)

### Step 2b — Docs vs. Ops Classification (CRITICAL)

This is the most important strategic call in the gap analysis. It determines the entire shape of the demo and what needs to be built. Classify the prospect into one of three lanes:

**OPS (Operational Execution)**
The prospect needs people to follow processes — checklists, SOPs, field workflows, onboarding sequences, inspections. They care about: did the crew do the thing? Was it done correctly? Can I prove it?

Signals: field teams, franchise/multi-location, safety checklists, onboarding, quality control, task completion tracking, mobile use, Trainual/Monday/Asana as competitors.

Demo approach: Standard PS demo — live-build workflows, show mobile execution, show audit trail, show conditional logic. Straightforward.

**DOCS (Document Lifecycle / Procedure Management)**
The prospect needs to manage the lifecycle of controlled documents — authoring, review cycles, approvals, version control, regulatory traceability, archival. They care about: who reviewed this? Is it the current version? Can we prove compliance to auditors?

Signals: regulated industry (nuclear, pharma, aerospace, energy, manufacturing), mentions of "procedure lifecycle" or "document control", SharePoint/Confluence/MasterControl as competitors, references to NQA-1/ISO/FDA/GxP/10 CFR, large reviewer pools, multi-language requirements, retention requirements (60-year archive, etc.).

**When you detect a DOCS use case, you must dig deeper.** Standard PS features alone may not tell the full story. The gap analysis must answer:

1. **Document approval workflow:** How do documents get approved today? How many review stages? Sequential or parallel? Who has veto power? What's the current cycle time?
2. **Reviewer matrix:** Who reviews what? Is it role-based (all QA managers) or named (specific people per document type)? How many reviewers per document? Do they review simultaneously or in sequence?
3. **Sample document structure:** What does one of their actual controlled documents look like? Section structure, numbering convention, header/footer requirements, revision history format. Ask for or find a sample.
4. **Auditor requirements:** What do their auditors actually check? Signature logs? Timestamped review evidence? Training acknowledgment records? Traceability from regulation → procedure → work instruction?
5. **Version control and retention:** How do they manage revisions? What's the retention requirement? Do superseded versions need to remain accessible? Is there an archival system (like Prime, Documentum, etc.)?
6. **Portal/UX layer:** Does the prospect need a user-friendly front end on top of the workflow engine? If they have hundreds of procedures and dozens of roles, they likely need role-based filtered views, not just a workflow list. This may require a custom portal page or data-set-driven navigation.

**HYBRID (Docs + Ops)**
The prospect needs both — controlled documents AND operational execution of those documents. Example: a nuclear plant that needs procedure lifecycle management AND field execution of those procedures with proof-of-completion.

This is the most complex demo. It requires showing both the document lifecycle (authoring → review → approval → publication → archival) AND the execution layer (running procedures as checklists in the field). The demo must show how these connect — a procedure change triggers re-training, a field execution links back to the controlled document version.

**Classification rules:**
- Default to OPS unless you see clear DOCS signals
- If the prospect mentions document control, procedure lifecycle, regulatory compliance, review cycles, or version management — it's DOCS or HYBRID
- If they mention SharePoint, Confluence, MasterControl, Veeva, Documentum, or similar — it's DOCS
- If they mention both field execution AND document management — it's HYBRID
- The classification goes into the JSON output and changes how every downstream skill builds

### Step 3 — Pain-to-Feature Mapping

This is the core of the gap analysis. For every pain point or need identified in research:

| Pain / Need | Evidence | PS Feature | Demo Approach | Priority |
|---|---|---|---|---|
| [Specific problem] | [Where you heard it — Gong timestamp, email quote, HubSpot note] | [The PS capability that solves it] | [How to show it — live build, pre-built workflow, data set, integration mock] | P1/P2/P3 |

**Evidence from documents is the strongest evidence.** When a prospect sends their actual SOPs, every gap you found in Step 1b becomes a row in this table. The document analysis turns generic pain ("we need accountability") into specific, demonstrable gaps ("your Job Site Departure Checklist has no proof-of-completion mechanism — Step 7 says 'verify cleanup' but nothing captures who verified or when").

**Priority rules:**
- **P1:** Prospect stated this explicitly as a goal or pain point. Must demo. Also: any gap found in their own documents that directly maps to a stated pain.
- **P2:** Implied by their situation or industry. Should demo if time allows. Also: gaps found in their documents that they haven't articulated yet but will recognize immediately.
- **P3:** PS capability that would impress but wasn't requested. Show only if natural.

**PS features to map against:**

*Core (all use cases):*
- Workflow execution with conditional logic (if/then branching)
- Form fields: text, dropdown, date, file upload, members, email, phone, number
- Approval steps with role-based routing
- Task assignments (static, dynamic, role-based)
- Due dates and SLA enforcement
- Data sets (structured reference data, RTMs, registries)
- Audit trail / compliance logging (timestamped completions)
- Mobile execution (field-friendly, photo capture)
- API / Zapier integrations (connect to their existing tools)
- Cora AI (workflow generation, document analysis, call analysis, form auto-population)
- Pages (embedded documentation within workflows)
- Reporting and dashboards (completion rates, overdue tasks, team performance)
- Permissions and role-based access control
- Multi-language support

*Docs-specific features (only for DOCS/HYBRID):*
- Data sets as Requirements Traceability Matrices (RTM) — regulation → procedure → section mapping
- Multi-stage review workflows with comment capture and resolution tracking
- Role-based portal views (author view, reviewer view, document admin view, coordinator view)
- Effective date enforcement with business-day logic
- Integration hooks to archival systems (API payload to Prime, Documentum, etc.)
- Document Change Request workflows triggered from execution
- Revision history tracking via data set records

### Step 4 — Demo Architecture

Based on the pain-to-feature map and the docs/ops classification, design the demo:

**What to build (ordered by priority):**
- List each workflow to pre-build, with specific steps/fields/logic
- Reference the prospect's actual documents if they sent any — build FROM their SOPs, not generic templates
- Note which workflows to build live vs. pre-build

**If documents were analyzed in Step 1b, the build spec is already done.** The step breakdown from each document IS the workflow spec. The demo architecture step now sequences them:
- Which document-based workflow opens the demo? (Pick the one with the strongest anchor line that connects to their #1 pain)
- Which one do you build live vs. pre-build? (Live-build the simplest one that still shows conditional logic; pre-build the complex ones)
- What's the "before and after" moment? (Show their actual document on screen, then show it as a living PS workflow — same steps, same language, but now with enforcement, tracking, and proof)
- What gaps from their documents do you call out during the demo? (These are your power moments: "Your checklist says 'take before photo' — but right now nobody can prove the photo was taken. In PS, the workflow won't advance until the photo is uploaded.")

**For DOCS use cases, also build:**
- A sample controlled document as a workflow (their actual document structure if available)
- A review/approval workflow with seeded reviewer comments (in their language if multi-lingual)
- A Requirements Traceability Matrix as a data set with realistic regulatory references
- Role-based filtered views showing what each persona sees
- If a portal/UX layer is needed, document what it requires and whether it can be built with PS Pages + data sets or needs custom work

**What NOT to show:**
- Features that don't connect to their stated needs
- Capabilities that require integrations they don't use
- Advanced features that will overwhelm a non-technical audience
- Anything that competes with a tool they love (e.g., don't demo task management if they're happy with Monday.com)

**Competitive positioning:**
- What are they comparing PS to? (Trainual, Monday, Asana, SharePoint, Confluence, MasterControl, Veeva, etc.)
- What's the one-liner differentiator for this specific prospect?
- What's the "only PS can do this" moment in the demo?

**For DOCS competitors specifically:**
- SharePoint: "SharePoint stores files. PS manages the entire lifecycle — authoring, review, approval, publication, execution, and audit trail in one system."
- Confluence: "Confluence is a wiki. PS enforces process — who reviews, when, in what order, with what evidence."
- MasterControl/Veeva: "Enterprise document control at a fraction of the cost and implementation time, with the operational execution layer built in."

**Integration story:**
- Which of their existing tools does PS connect to?
- What's real (native or Zapier) vs. what needs to be mocked?
- How does PS fit into their stack without replacing what works?
- For DOCS: how does PS connect to their archival system, training system, and change management process?

### Step 5 — Business Framing

For the AE and SE to align on messaging:

**The narrative arc:**
- Where they are today (current state — messy, manual, risky)
- What's at stake (cost of doing nothing — quantified if possible)
- Where they want to be (future state — in their words, from discovery)
- How PS gets them there (specific, not generic)

**Objection prep:**
- Based on research, what are the likely objections?
- For each: the objection, why it's coming up, and the response

**For DOCS use cases, expect these objections:**
- "Can PS handle our document complexity?" → Show the actual document structure built as a workflow
- "We need 100+ reviewers on a single document" → Show parallel review with comment capture
- "What about regulatory traceability?" → Show the RTM data set with drill-down
- "We've evaluated 5–6 vendors already" → Ask what they liked and didn't like about each; position PS as the one that does both docs AND ops
- "What about retention/archival?" → Show the API integration to their archival system

**Decision-maker engagement:**
- Is the economic buyer engaged? On the call?
- If not: what's the strategy to get them involved?
- What does the champion need to take back internally?

### Step 6 — Technical Considerations

For the SE building the demo:

- Estimated build time for each workflow
- MCP-buildable vs. requires manual setup
- Data set requirements (what reference data to seed)
- Integration mocks needed
- Mobile testing requirements
- Any PS platform limitations to be aware of for this use case

**For DOCS use cases, additional technical notes:**
- Portal/UX layer: what's needed, can it be done with Pages + data sets, or does it need custom HTML/embedding?
- Review workflow complexity: how many approval stages, parallel vs. sequential, comment threading requirements
- RTM data set size: how many regulations, how many procedures, how deep is the cross-reference?
- Multi-language requirements: which languages, does the UI need to switch, or just document content?
- Archival integration: what system, what payload format, what triggers the push?

---

## Output

The skill produces two artifacts:

### 1. Gap Analysis JSON (`/tmp/<company_slug>_gap_analysis.json`)

```json
{
  "company": "Company Name",
  "domain": "company.com",
  "analysis_date": "2026-05-19",
  "meeting_date": "2026-05-20",
  "meeting_type": "Demo | Trial Review | Discovery",

  "use_case_classification": {
    "type": "ops | docs | hybrid",
    "confidence": "high | medium | low",
    "rationale": "Why this classification — cite specific evidence",
    "docs_depth": {
      "applies": true,
      "approval_workflow": "Description of current document approval process",
      "reviewer_matrix": "Who reviews what, how many, sequential vs parallel",
      "sample_document": "What a controlled document looks like — structure, sections, conventions",
      "auditor_requirements": "What auditors check, what evidence format they need",
      "version_control": "How revisions are managed, retention requirements, archival system",
      "portal_ux_needed": true,
      "portal_ux_notes": "What roles need filtered views, complexity estimate"
    }
  },

  "people": {
    "champion": {"name": "", "title": "", "email": ""},
    "economic_buyer": {"name": "", "title": "", "engaged": true},
    "attendees": [{"name": "", "title": "", "role_in_deal": ""}]
  },

  "company_context": {
    "industry": "",
    "size": "",
    "geography": "",
    "growth_stage": "",
    "current_tools": [""],
    "compliance_requirements": [""],
    "timeline_driver": ""
  },

  "competition": {
    "evaluated": [""],
    "differentiator": "",
    "one_liner": ""
  },

  "pain_feature_map": [
    {
      "pain": "",
      "evidence": "",
      "evidence_source": "gong | hubspot | email | web | document",
      "ps_feature": "",
      "demo_approach": "pre-build | live-build | show-existing | mock",
      "priority": "P1 | P2 | P3"
    }
  ],

  "demo_plan": {
    "workflows_to_build": [
      {
        "name": "",
        "source_document": "filename.pdf or null",
        "build_method": "pre-build | live-build",
        "estimated_build_minutes": 0,
        "key_features": ["conditional_logic", "photo_capture", "approval_steps"],
        "anchor_line": "",
        "mcp_buildable": true,
        "manual_setup_notes": ""
      }
    ],
    "data_sets_to_build": [
      {
        "name": "",
        "purpose": "RTM | registry | reference data",
        "columns": [""],
        "sample_row_count": 0,
        "mcp_buildable": true
      }
    ],
    "portal_ux": {
      "needed": false,
      "roles": [""],
      "implementation": "pages | data-set-navigation | custom-html | not-needed",
      "notes": ""
    },
    "do_not_show": [""],
    "integration_mocks": [""],
    "mobile_test_required": true
  },

  "business_framing": {
    "current_state": "",
    "cost_of_inaction": "",
    "future_state": "",
    "narrative_arc": "",
    "likely_objections": [
      {"objection": "", "reason": "", "response": ""}
    ],
    "decision_maker_strategy": ""
  },

  "source_documents": [
    {
      "filename": "",
      "type": "pdf | spreadsheet | image | transcript",
      "document_type": "sop | checklist | script | procedure | policy | form",
      "used_by": "role or team",
      "frequency": "daily | per-job | per-event | periodic | on-change",
      "summary": "",
      "priority_for_demo": "P1 | P2 | P3",
      "anchor_line": "The one sentence that sells this workflow in the demo",
      "ps_workflow_name": "[Company] - [Process Name] - DEMO",
      "build_method": "pre-build | live-build",
      "estimated_build_minutes": 0,
      "step_breakdown": [
        {
          "step_number": 1,
          "description": "What the step says in the original document",
          "ps_feature": "page | form_field | conditional_logic | approval | task_assignment | file_upload | data_set_lookup | integration",
          "field_type": "text | dropdown | date | number | email | phone | file | members | null",
          "conditional_branch": "If [condition] → [outcome] or null",
          "gap_identified": "What's missing that PS adds, or null"
        }
      ],
      "conditional_branches_count": 0,
      "form_fields_count": {"text": 0, "dropdown": 0, "date": 0, "number": 0, "file": 0, "other": 0},
      "gaps_and_improvements": [
        "What's missing from the document + what PS adds"
      ],
      "integration_points": [
        {"step": 0, "system": "", "action": "", "method": "zapier | api | webhook | manual"}
      ]
    }
  ]
}
```

### 2. Internal Gap Analysis Document (`/tmp/<company_slug>_gap_analysis.html`)

A formatted, readable HTML document for the SE team that includes:
- Account context (one glance)
- **Docs/Ops classification with rationale** (prominently displayed)
- **Document analysis section** — for each prospect document: step-by-step breakdown, PS feature mapping per step, conditional logic identified, gaps found, anchor line, build estimate. This is the SE's build spec — they should be able to construct the PS workflow directly from this section without re-reading the original document.
- Pain-to-feature map (table, with document-sourced evidence highlighted)
- Demo architecture (sequenced demo flow with before/after moments from their documents)
- Competitive positioning
- Objection prep
- Technical build notes

This document is styled consistently with the demo runbook format (Inter font, clean layout, scannable sections).

---

## How this connects to other Process Builder skills

The gap analysis JSON is the input contract for downstream skills:

- **Document → Workflow** reads `source_documents` where `step_breakdown` is populated. The gap analysis has already done the hard work — extracted every step, mapped PS features, identified conditional logic, and specified field types. The Document → Workflow skill takes this pre-digested spec and constructs the actual PS workflow via MCP. It doesn't need to re-interpret the PDF; it builds from the gap analysis step breakdown. For DOCS use cases, it also builds the review/approval workflow and seeds the RTM data set.
- **Transcript → Workflow** reads `pain_feature_map` where `evidence_source = "gong"` and extracts the described processes from transcripts to build as workflows.
- **BPMN/Image → Workflow** reads `source_documents` where `type = "image"` and converts visual process maps into PS workflows.

Each downstream skill uses `business_framing`, `competition`, and `use_case_classification` to inform HOW it builds — e.g., if the classification is DOCS and the competitor is SharePoint, emphasize the review lifecycle and audit trail over operational execution.

---

## Example invocation

```
/gap-analysis Tree Masters of Tennessee lindsay@treemasterstn.com
/gap-analysis westinghouse    # domain lookup, pulls all contacts
/gap-analysis                 # prompts for company/contact
```
