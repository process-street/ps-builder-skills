# Browser Recording — sample-0000-0000-0000

Recorded with the PS Builder Chrome Extension.

- Started: 2026-05-26T15:00:00.000Z
- Ended: 2026-05-26T15:02:14.000Z
- Events: 9

## Instructions for Claude

This is a recording of a user performing a process in their browser. Convert it into a Process Street workflow:

1. Use the Process Street MCP tools to create a new workflow.
2. Infer the workflow name from the events (typically the first meaningful page title or the URL pattern).
3. Group events into logical tasks. Heuristic: each navigation = a new task; form interactions on the same page belong to one task.
4. For each task, write a clear name + description. Reference the screenshot (`screenshots/step-NNN.png`) in the description if useful.
5. When events include `form_field` data, add corresponding PS form fields (short text, long text, email, dropdown, etc.) to the matching task.
6. Ignore noise: duplicate clicks, non-meaningful navigations, programmatic re-renders.

## Events

### Event 1 — navigation
- Time: 2026-05-26T15:00:01.100Z
- URL: https://app.example.com/customers/new
- Screenshot: ![navigation](screenshots/step-001.png)

### Event 2 — input
- Time: 2026-05-26T15:00:08.200Z
- URL: https://app.example.com/customers/new
- Page: New Customer — Example CRM
- Element: `input`
  - Name: "Company name"
  - Selector: `#customer_company`
- Form field:
  - Name: company
  - Type: text
  - Label: Company name
  - Value: "Acme Corp"
- Screenshot: ![input](screenshots/step-002.png)

### Event 3 — input
- Time: 2026-05-26T15:00:14.500Z
- URL: https://app.example.com/customers/new
- Element: `input`
  - Name: "Primary contact email"
- Form field:
  - Name: email
  - Type: email
  - Label: Primary contact email
  - Value: "alex@acme.example"
- Screenshot: ![input](screenshots/step-003.png)

### Event 4 — input
- Time: 2026-05-26T15:00:21.000Z
- URL: https://app.example.com/customers/new
- Element: `select`
  - Name: "Account tier"
- Form field:
  - Name: tier
  - Type: select-one
  - Label: Account tier
  - Value: "enterprise"
- Screenshot: ![input](screenshots/step-004.png)

### Event 5 — click
- Time: 2026-05-26T15:00:30.700Z
- URL: https://app.example.com/customers/new
- Element: `button`
  - Name: "Save customer"
  - Text: "Save customer"
  - Selector: `button[type="submit"]`
- Screenshot: ![click](screenshots/step-005.png)

### Event 6 — navigation
- Time: 2026-05-26T15:00:32.100Z
- URL: https://app.example.com/customers/2117/welcome
- Screenshot: ![navigation](screenshots/step-006.png)

### Event 7 — click
- Time: 2026-05-26T15:00:45.300Z
- URL: https://app.example.com/customers/2117/welcome
- Page: Welcome Acme Corp — Example CRM
- Element: `a`
  - Name: "Send welcome email"
  - Selector: `a.btn-primary`
  - Href: https://app.example.com/customers/2117/welcome/send
- Screenshot: ![click](screenshots/step-007.png)

### Event 8 — input
- Time: 2026-05-26T15:01:05.000Z
- URL: https://app.example.com/customers/2117/welcome/send
- Element: `textarea`
  - Name: "Personal note"
- Form field:
  - Name: note
  - Type: textarea
  - Label: Personal note
  - Value: "Looking forward to working with you!"
- Screenshot: ![input](screenshots/step-008.png)

### Event 9 — submit
- Time: 2026-05-26T15:01:30.000Z
- URL: https://app.example.com/customers/2117/welcome/send
- Element: `form`
  - Selector: `form#send-welcome`
- Screenshot: ![submit](screenshots/step-009.png)

## Raw events (JSON, screenshots stripped)

```json
[
  { "type": "navigation", "timestamp": "2026-05-26T15:00:01.100Z", "url": "https://app.example.com/customers/new", "screenshot": "[saved as png]" },
  { "type": "input", "timestamp": "2026-05-26T15:00:08.200Z", "url": "https://app.example.com/customers/new", "page_title": "New Customer — Example CRM", "element": { "tag": "input", "selector": "#customer_company", "accessible_name": "Company name" }, "form_field": { "name": "company", "type": "text", "label": "Company name", "value": "Acme Corp" }, "screenshot": "[saved as png]" },
  { "type": "input", "timestamp": "2026-05-26T15:00:14.500Z", "url": "https://app.example.com/customers/new", "element": { "tag": "input", "accessible_name": "Primary contact email" }, "form_field": { "name": "email", "type": "email", "label": "Primary contact email", "value": "alex@acme.example" }, "screenshot": "[saved as png]" },
  { "type": "input", "timestamp": "2026-05-26T15:00:21.000Z", "url": "https://app.example.com/customers/new", "element": { "tag": "select", "accessible_name": "Account tier" }, "form_field": { "name": "tier", "type": "select-one", "label": "Account tier", "value": "enterprise" }, "screenshot": "[saved as png]" },
  { "type": "click", "timestamp": "2026-05-26T15:00:30.700Z", "url": "https://app.example.com/customers/new", "element": { "tag": "button", "selector": "button[type=\"submit\"]", "text": "Save customer", "accessible_name": "Save customer" }, "screenshot": "[saved as png]" },
  { "type": "navigation", "timestamp": "2026-05-26T15:00:32.100Z", "url": "https://app.example.com/customers/2117/welcome", "screenshot": "[saved as png]" },
  { "type": "click", "timestamp": "2026-05-26T15:00:45.300Z", "url": "https://app.example.com/customers/2117/welcome", "page_title": "Welcome Acme Corp — Example CRM", "element": { "tag": "a", "selector": "a.btn-primary", "accessible_name": "Send welcome email", "href": "https://app.example.com/customers/2117/welcome/send" }, "screenshot": "[saved as png]" },
  { "type": "input", "timestamp": "2026-05-26T15:01:05.000Z", "url": "https://app.example.com/customers/2117/welcome/send", "element": { "tag": "textarea", "accessible_name": "Personal note" }, "form_field": { "name": "note", "type": "textarea", "label": "Personal note", "value": "Looking forward to working with you!" }, "screenshot": "[saved as png]" },
  { "type": "submit", "timestamp": "2026-05-26T15:01:30.000Z", "url": "https://app.example.com/customers/2117/welcome/send", "element": { "tag": "form", "selector": "form#send-welcome" }, "screenshot": "[saved as png]" }
]
```

---

## What this sample maps to (reference for the skill)

Running `chrome-recording-to-workflow` on the events above should yield a workflow with **3 tasks**:

1. **Fill in new customer details** (page `/customers/new`)
   - Text widget: "Open the New Customer page in Example CRM and fill in the form."
   - FormField `Text` — Label: "Company name"
   - FormField `Email` — Label: "Primary contact email"
   - FormField `Select` — Label: "Account tier" (options inferred or left empty for user to fill)
   - Text widget: "Click **Save customer** when done. See screenshots/step-005.png."

2. **Open the welcome screen** (page `/customers/<id>/welcome`)
   - Text widget: "On the customer's welcome screen, click **Send welcome email** to start the welcome flow."

3. **Send the welcome email** (page `/customers/<id>/welcome/send`)
   - Text widget: "Write a short personal note and submit."
   - FormField `Textarea` — Label: "Personal note"
   - Text widget: "Submit the form."

Workflow name: **"New Customer Onboarding"** (inferred from the first meaningful page title, with the trailing site name stripped).

The skill should ask the user which folder to put it in before calling `createWorkflow`, and should confirm the plan before calling `publishWorkflowRevision`.
