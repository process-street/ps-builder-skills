# Sample: Discovery Call — Field Inspection Process

A sanitized, condensed discovery-call excerpt (fictional regional insurance carrier) and the
workflow spec a correct extraction should produce. Use it to smoke-test the skill end-to-end
in `dry-run` mode.

---

## Transcript excerpt (timestamps in `[mm:ss]`)

> **[02:10] Facilitator:** Walk me through what happens when an inspection request comes in.
>
> **[02:24] Ops Manager:** So every request comes through our intake mailbox. Sarah's team —
> the coordinators — they log it. They grab the policy number, which county the property's
> in, and any photos the agent sent over.
>
> **[03:40] Facilitator:** And then?
>
> **[03:46] Ops Manager:** Then it depends on the county. We keep a spreadsheet that says
> which inspector covers which county. The coordinator looks that up and assigns it out.
> That spreadsheet's a problem honestly, people forget to check the latest version.
>
> **[05:12] Ops Manager:** The inspector goes out, does the inspection, uploads their photos
> and the report. They've got 5 business days from assignment, that's our standard.
>
> **[06:30] Facilitator:** What happens if the property's outside your network counties?
>
> **[06:38] Ops Manager:** If it's out of network it goes to a totally different team — the
> external review desk. That's maybe one in ten.
>
> **[08:05] Ops Manager:** Once the report's in, my desk reviews it. Nothing closes until a
> manager signs off. Just one of us, whoever picks it up.
>
> **[09:20] Facilitator:** Would you ever want the system to update your policy admin system
> automatically when it closes?
>
> **[09:27] Ops Manager:** Ideally, yeah, someday — that'd be great. Right now we just
> re-key it.
>
> **[10:02] Ops Manager:** Oh — and every Monday morning we pull a list of anything still
> open past its due date. I guess if an inspector ever quit mid-inspection we'd have to
> reassign everything manually, but that's only happened once.

---

## What a correct extraction produces

### Voice classification
| Statement | Voice | Action |
|---|---|---|
| Intake via mailbox, log policy # / county / photos | Practice | Build |
| County → inspector spreadsheet lookup | Practice (+ pain) | Build as **Data Set** |
| 5-business-day inspection SLA | Practice | Relative due-date rule |
| Out-of-network → external review desk | Practice (conditional) | Logic-rule branch |
| Manager sign-off, single approver | Practice | Approval task |
| Auto-update policy admin system | **Aspiration** ("ideally, someday") | Deferred list |
| Monday overdue report | Practice (separate cadence) | Separate scheduled workflow — note, confirm with user |
| Reassign-on-inspector-quit | **Hypothesis** ("I guess if...", happened once) | Skip; open question |

### Spec (abridged)

```yaml
workflow:
  name: "Acme Mutual — Property Inspection Request"
  classification: OPS
  tasks:
    - name: "Intake — Log Inspection Request"
      assignee_role: "Coordinator"
      confidence: high
      evidence: "[02:24] 'every request comes through our intake mailbox... they log it'"
      fields:
        - { type: "Text",      name: "Policy Number", required: true }
        - { type: "Select",    name: "County",        required: true, options: from_data_set }
        - { type: "MultiFile", name: "Agent Photos" }
    - name: "Assign — Inspector by County"
      assignee_role: "Coordinator"
      confidence: high
      evidence: "[03:46] 'we keep a spreadsheet that says which inspector covers which county'"
      uses_data_set: "County → Inspector"
    - name: "Inspect — Site Visit & Report"
      assignee_role: "Inspector"
      due_rule: "5 business days after Assign task completes"
      confidence: high
      evidence: "[05:12] 'they've got 5 business days from assignment'"
      fields:
        - { type: "MultiFile", name: "Inspection Photos", required: true }
        - { type: "File",      name: "Inspection Report", required: true }
    - name: "Review — Manager Sign-off"
      assignee_role: "Ops Manager"
      task_type: "Approval"
      confidence: high
      evidence: "[08:05] 'nothing closes until a manager signs off. Just one of us'"
    - name: "Escalate — External Review Desk"
      assignee_role: "External Review"
      hidden_by_default: true
      confidence: high
      evidence: "[06:38] 'if it's out of network it goes to a totally different team'"
  logic_rules:
    - when: { field: "County", op: "Is", value: "Out of Network" }
      then:
        - { action: "Show", task: "Escalate — External Review Desk" }
        - { action: "Hide", task: "Assign — Inspector by County" }
  data_sets:
    - name: "County → Inspector"
      reason: "replaces the versioning-prone spreadsheet [03:46]"
  deferred:
    - item: "Policy admin system writeback on close"
      reason: "aspiration — 'ideally, yeah, someday' [09:27]"
    - item: "Monday overdue-report run"
      reason: "real practice but a separate scheduled workflow — confirm scope with user [10:02]"
  open_questions:
    - "Bulk reassignment if an inspector leaves — hypothesis only [10:02]; worth one question"
```

### The mistakes this example is designed to catch

1. Building the policy-admin writeback (aspiration voice, suggested by the facilitator).
2. Folding the Monday overdue report into the main workflow (different cadence = different workflow).
3. Hardcoding inspector names instead of the Data Set lookup.
4. Missing the out-of-network branch because it's "only one in ten."
5. Making "Agent Photos" required (the speaker said "any photos" — optional).
