# Extraction Playbook — Verbal Process Descriptions

How to turn what people *say* about their process into what the process *actually is*.
This is the reference layer behind `SKILL.md` Steps 2–4.

---

## 1. The four voices on a call

Every process conversation mixes four kinds of statements. Classify before extracting:

| Voice | Sounds like | Evidence value |
|---|---|---|
| **Practice** | "We do X." "Every intake starts with..." "Then Maria's team takes it." | **Build.** The procedure. |
| **Aspiration** | "Ideally..." "We'd love..." "Down the road..." | Future-enhancements list only. |
| **Hypothesis** | "I suppose if..." "Theoretically..." | Skip unless operationally confirmed. |
| **Suggestion** | (From the facilitator/vendor) "What if you routed that automatically?" | Only build if the owner confirms: "yes, exactly" / "that's what we need." |

The most common extraction error is building the *suggestion* voice — the workflow ends up
describing the demo, not the customer's process.

---

## 2. Verbal pattern → Process Street primitive catalog

### Triggers
| Pattern | Primitive |
|---|---|
| "When a request comes in..." / "Someone fills out a form..." | Manual run or workflow incoming webhook; the named inputs become kickoff form fields |
| "Every morning / Monday / month-end..." | Scheduled workflow |
| "When the deal closes / ticket opens..." (another system) | API/webhook trigger from that system |

### Structure
| Pattern | Primitive |
|---|---|
| "First... then... after that... finally..." | Sequential tasks |
| "While that's happening, the other team..." | Parallel tasks (no dependency between them) |
| "That whole part is its own thing..." | Candidate for a *separate workflow* — don't force one giant flow |
| Step counts ("there are about six steps") | Sanity check your extracted task count against it |

### Decisions
| Pattern | Primitive |
|---|---|
| "If X, then Y" | Logic rule: show/hide task(s) |
| "It depends on the type/region/tier/amount..." | Dropdown field + logic rules per value — and if the mapping is big, a **Data Set** |
| "Usually A, but sometimes B" | A is the main path; B is a conditional branch flagged ⚠️ |
| "If it gets rejected / fails / bounces..." | Rejection branch: a handling task revealed by logic, often looping back to the submitter |

### People
| Pattern | Primitive |
|---|---|
| Job titles, team names | Role-based assignment (groups, never individuals) |
| "Whoever's available..." | Group assignment + flag "fuzzy role — confirm" |
| "Then it goes over to..." | Handoff: new assignee on the next task + notification |
| "has to sign off" / "approves" | Approval task (single approver) |
| "two of the three managers" / "everyone on the committee" | Voting approval with explicit threshold / mandatory voters |

### Data
| Pattern | Primitive |
|---|---|
| Nouns captured repeatedly across steps (ID numbers, dates, amounts, names) | Promote to **kickoff form fields** — first-class data, not per-task notes |
| "We attach the photos / report / evidence" | File (single definitive doc) or MultiFile (evidence packets, up to 10) |
| "We check the spreadsheet to see who covers that..." | **Data Set** + linked dropdown — lookup-driven routing |
| "We track it in [other system]" | Integration note in the report; don't silently rebuild another system's database |

### Cadence & deadlines
| Pattern | Primitive |
|---|---|
| "within 48 hours" / "by end of week" | Relative due-date rule on the task (never hardcoded dates) |
| "30 days before the deadline we..." | Due-date rule keyed off a date field |

---

## 3. Field-type selection guide

| Use | Field type |
|---|---|
| Anything reportable or that must be consistent | **Dropdown (Select)** — options go in `config.items` as `[{"name": "..."}]` |
| Multiple applicable categories | MultiSelect |
| Deadline, audit point, anything time-anchored | **Date** |
| One definitive document (re-upload replaces) | **File** |
| Photos / evidence packets (uploads append, max 10) | **MultiFile** (supports extension constraints) |
| Free-form context | Text / Textarea |
| Checklist of acknowledgements or sign-off items | MultiChoice |
| Picking a user (e.g., "assign the next reviewer") | Member |
| Typed contact data with validation | Email / URL / Phone |
| Anything fed by another system | Hidden field populated via API |

Default required = the fields the speaker said the process *cannot proceed without*.
Everything else optional.

---

## 4. Failure modes of verbal description (and the countermove)

| Verbal tell | What it usually means | Countermove |
|---|---|---|
| "And then, you know, sometimes we..." | Edge case, not the main path | Conditional branch, flagged ⚠️ |
| "We just kind of..." | Real step, never formalized | Build as optional task; raise in report |
| "Whoever's available" | Role not actually defined | Group assignment + open question |
| "It depends on the customer" | Data-driven branch, source unknown | Data-set-backed lookup; defer if no source for the records |
| Same noun in five steps | A first-class field | Promote to kickoff form |
| Speaker A: "we always..." Speaker B: "well, not always..." | Conflicting versions | Build the simpler one; flag both in report |
| Long silence then "...yeah basically" (agreeing with facilitator) | Weak confirmation | Treat as medium confidence at best |
| "We tried automating that before and it broke" | Landmine | Note in report; do not auto-build that integration |
| Step described only while screen-sharing, never narrated | Visible but unexplained | Use the frame; name the task from the UI; flag for confirmation |

---

## 5. Confidence scoring

Score every extracted element:

- **high** — stated as current practice AND (repeated, confirmed by a second speaker, or
  demonstrated on screen). → Build.
- **medium** — stated once, clearly, no contradiction. → Build, flag ⚠️ with the assumption.
- **low** — inferred, mumbled, contradicted, or suggestion-voice only. → Defer, with reason.

Never average scores across elements. A workflow of 12 high-confidence tasks plus 6 deferred
items is a *better* deliverable than 18 built tasks where 6 are guesses — the deferred list
drives the follow-up conversation.

---

## 6. Key-moment detection for frame extraction

Anchor phrases that mark a demonstration moment worth a frame:

- "let me share my screen" / "can you see my screen?" (start of the demonstration region)
- "so this is where we..." / "as you can see here"
- "I just click..." / "then you hit..."
- "this is the form / report / dashboard / queue"
- A step from the extraction (Section 2) whose timestamp falls inside the demonstration region

Frame hygiene rules:

1. Review every frame before embedding — actually look at it.
2. Reject: webcam-only shots, transition blur, anything with real customer data, credentials,
   inboxes, or unrelated tabs.
3. Prefer the frame ~2–3 seconds *after* the anchor phrase (the screen has settled).
4. One frame per task maximum — the clearest one.
5. When unsure whether a frame is safe to embed, show it to the user and ask.
