---
doc: spec
status: approved
---

# Sahyog AI — Technical Spec

## How This Works, In Plain Language

Sahyog AI runs on your computer as a Streamlit app in a browser tab. With a Gemini key configured, a submitted report goes to Google's Gemini service for an assessment. Without a key, the form uses transparent local keyword and category rules instead. The app labels which source produced each result, checks the answer, then keeps the report in memory while the app is running and shows it on the operations dashboard. You can change a report's status there. Sample dashboard reports are separate examples, not AI results. The volunteer panel also uses sample information; it does not claim that real people are available or dispatched.

There is no account, database, or live multi-user connection in this proof of concept. Reports disappear when the app process restarts. This keeps the demo small while preserving the central idea: a real Gemini assessment connected to a usable operations view.

## The Core Journey Through the System

1. A person enters a location, category, and crisis description in the Streamlit form, or loads the separate sample dataset to preview operations.
2. `app.py` checks the required fields and whether Gemini is configured. With a key, it calls `sahyog_ai/gemini.py`; without one, it calls `sahyog_ai/local_triage.py`.
3. Gemini returns structured JSON, or the local rules return a simple category/keyword estimate. `sahyog_ai/models.py` validates the assessment and records its source.
4. If the assessment is valid, `app.py` creates a report and stores it in Streamlit's session state. The same run displays it on the operations dashboard.
5. A responder changes a report's status in the dashboard. The in-memory record updates and Streamlit redraws the current view.
6. If a Gemini request fails or its answer cannot be validated, the app shows an explicit error. A person may retry or explicitly choose local rules; the resulting report is labeled non-AI. The app never silently downgrades or invents a Gemini result.

PRD ref: `prd.md > The Core Journey`, `Features and Behavior > Emergency report and AI assessment`, and `Features and Behavior > Relief operations dashboard`.

## Stack

- **Python 3.10+** — the learner selected Python. The minimum supports the type syntax and SDK baseline used by the app.
- **Streamlit** — the learner selected Streamlit for a quick interactive browser interface. Its session state holds reports only for the current app session.
- **Google GenAI Python SDK (`google-genai`)** — calls Gemini using the official Python client and structured output. Tradeoff: the AI feature requires internet access, an API key, and may be subject to account quotas or billing.
- **HTTPX** — recognizes transport and timeout errors from the Gemini SDK so the app can show a clear retry message.
- **Pydantic** — validates the structured AI response before it is shown or saved into the current session.
- **python-dotenv** — optionally loads the ignored local `.env` file for the API key and model name.
- **Local Python rules** — provides an explainable no-key fallback using category baselines and a small keyword list; it is not AI or validated emergency triage.

Documentation:
- [Python](https://docs.python.org/3/)
- [Streamlit documentation](https://docs.streamlit.io/)
- [Google GenAI Python SDK](https://github.com/googleapis/python-genai)
- [HTTPX documentation](https://www.python-httpx.org/)
- [Gemini API quickstart](https://ai.google.dev/gemini-api/docs/get-started?lang=python)
- [Gemini structured output](https://ai.google.dev/gemini-api/docs/structured-output?lang=python)
- [Pydantic documentation](https://docs.pydantic.dev/latest/)

## Where It Runs and How Someone Tries It

- **Runtime:** a local Python process opens the Streamlit interface in a browser, normally at `http://localhost:8501`.
- **Requirements:** Python 3.10+ and dependencies installed from `requirements.txt`. Internet access and a locally stored `GEMINI_API_KEY` enable Gemini; without it, report submissions use local rules. Never paste the key into chat or commit it. `.env` is ignored by Git; `.env.example` contains no secret.
- **Install and run from the repository root in PowerShell:**

  ```powershell
  py -m venv .venv
  .\.venv\Scripts\Activate.ps1
  python -m pip install -r requirements.txt
  $env:GEMINI_API_KEY = "<your key from Google AI Studio>"
  streamlit run app.py
  ```

- **Try it:** open the local URL printed by Streamlit, submit a sample emergency, then review the urgency score, recommended steps, and report in the dashboard; change its status and inspect the volunteer sample panel.
- **Record the demo:** use the same local app and show one report moving from submission through Gemini assessment to the operations dashboard. Deployment is optional; the hackathon separately requires a short demo video and a public GitHub repository.

## Look and Feel

Use a bright, colorful operations dashboard with a warm light canvas, high-contrast text, and teal, violet, coral, and sunny accent colors. Give the hero and key cards colorful surfaces while keeping form fields and report text calm and readable. Keep distinct urgency treatments and active/resolved/source text badges so color is never the only status cue. Use Streamlit's layout, columns, forms, and status elements rather than adding a styling framework; exact custom typography and pixel-level control are limited by Streamlit's native components.

PRD ref: `prd.md > Look and Feel`.

## Components

### Emergency report form (`app.py`)

Collects location, category, and description; rejects missing values; shows the emergency-service disclaimer; and initiates the Gemini or local-rules assessment, according to the configured path. A report is added only after a valid assessment is received.

Implements `prd.md > Features and Behavior > Emergency report and AI assessment`.

### Gemini assessment service (`sahyog_ai/gemini.py`)

Builds a focused prompt from the submitted fields, asks the configured Gemini model for a structured assessment, and turns missing credentials, API errors, or unusable output into an explicit failure for the UI to display. It does not fabricate a fallback score or recommendation.

Implements `prd.md > Features and Behavior > Emergency report and AI assessment`.

### Local rules assessment (`sahyog_ai/local_triage.py`)

When Gemini is not configured, calculates a simple score from the selected category and a small, explicit set of report keywords. Returns a rationale naming the category baseline and matched rule cues, plus generic coordination reminders. The UI labels every result `Local rules · not AI`; it does not claim to understand context, validate a triage decision, or replace emergency services.

When a configured Gemini request fails, this component is used only after the user explicitly selects the local-rules alternative.

Implements `prd.md > Features and Behavior > Emergency report and AI assessment` and `States and Boundaries`.

### Report coordination helpers (`sahyog_ai/operations_assist.py`)

For a report, requests a structured Gemini result containing a translation into the chosen target language, possible duplicates among the bounded current-session report candidates, and suggestions selected from the fixed sample volunteer and supply lists. The service validates the response and rejects candidate IDs outside those lists. The original report remains unchanged. No match creates an assignment or dispatch.

Without a Gemini key, a separate local-rules helper may identify likely duplicate reports and category-matched sample resources. It labels this output non-AI and leaves translation unavailable. If Gemini fails, the UI shows the failure and requires the coordinator to choose retry or local rules.

Implements `prd.md > Features and Behavior > Report translation and coordination suggestions`.

### Assessment and report data (`sahyog_ai/models.py`)

Defines the validated assessment (integer urgency from 1 to 5, short rationale, ordered action steps) and report record (unique ID, submitted details, assessment source—Gemini, Local rules, or Demo example—creation time, and active/resolved status). The 1–5 range is an implementation convention for a legible demo scale, not a validated emergency triage standard.

Implements `prd.md > Features and Behavior > Emergency report and AI assessment` and `Relief operations dashboard`.

### Relief operations dashboard (`app.py`)

Reads reports from session state, summarizes and filters active/resolved items, displays submitted details with validated assessments and explicit source labels, and updates a report's status on responder action. Provides a separate load/clear action for explicitly labeled sample reports so the dashboard can be explored without Gemini credentials. Shows a useful empty state when there are no reports.

Implements `prd.md > Features and Behavior > Relief operations dashboard`.

### Volunteer status panel (`app.py`)

Displays a small, static, explicitly labeled sample volunteer-status view. It demonstrates the requested dashboard content without representing real availability, matching, or dispatch.

Implements `prd.md > Features and Behavior > Relief operations dashboard` and `States and Boundaries`.

### Sample relief roster (`sahyog_ai/operations_assist.py`)

Defines a small fixed list of illustrative volunteer skills and supply categories. Both AI and local suggestions are constrained to these known entries, visibly labeled as sample, unverified recommendations. The list does not represent actual availability, inventory, assignment, or dispatch.

Implements `prd.md > Features and Behavior > Report translation and coordination suggestions`.

## Data Model

- **EmergencyReport:** `id` (unique string), `location` (string), `category` (Medical/Food/Water/Shelter), `description` (string), `assessment` (validated score 1–5, rationale, and action steps), `assessment_source` (Gemini, Local rules, or Demo example), `status` (active/resolved), and `created_at` (timestamp).
- **Assessment:** Gemini-generated, local-rule, or sample score, short rationale, and ordered recommendations, validated against a Pydantic schema before creating an EmergencyReport.
- **Volunteer sample:** a small fixed list of example names/statuses in the app; clearly labeled as demonstration data and not connected to real volunteers.
- **Operations assistance:** validated detected-language and translated text, possible-duplicate report IDs with a similarity signal, sample volunteer IDs, sample supply IDs, and an explicit source (`Gemini` or `Local rules`). Gemini candidate IDs are checked against bounded session reports and the fixed roster before display.
- **Sample roster:** fixed candidate IDs, names, supported categories, and caveats; all matches are suggestions only and never update a person's status or report state.
- **Storage and updates:** reports live in `st.session_state` for the current browser/app session. New reports are appended only after successful validation; status actions update the corresponding in-memory report. Refreshes during the same session preserve state according to Streamlit's session behavior; ending/restarting the app loses reports. There is no account, cross-user sharing, or durable storage.

## File Structure

```text
sahyog-ai/
├── app.py                    # Streamlit report form, dashboard, session state, sample volunteers
├── sahyog_ai/
│   ├── __init__.py           # Package marker
│   ├── gemini.py             # Gemini request and API error handling
│   ├── local_triage.py       # Transparent no-key rule-based estimate
│   ├── operations_assist.py  # Translation, duplicate, and sample-match helpers
│   └── models.py             # Pydantic response validation and report types
├── tests/
│   └── test_core.py          # Built-in unittest checks for validation and key errors
├── requirements.txt          # Streamlit, Gemini SDK, HTTPX, Pydantic, dotenv
├── .env.example              # Secret-free example of required local configuration
├── .gitignore                # Excludes local credentials and learner profile
├── README.md                 # Setup, run, safety, and demo instructions
└── devpost/                  # Approved project plan and build records
```

## External Services and Dependencies

### Gemini API

- **Use:** analyze an emergency description and return urgency score, rationale, and action steps.
- **Client:** official `google-genai` Python SDK.
- **Request:** `client.interactions.create(model="gemini-3.8-flash", input=<report category, location, and description plus safety-focused instructions>, response_format=<JSON schema for score, rationale, and steps>)`.
- **Response handling:** validate the returned JSON with Pydantic; reject missing, malformed, or out-of-range scores and empty action steps.
- **Credentials:** `GEMINI_API_KEY` in the local environment; do not hardcode, print, or commit it.
- **Privacy:** a coordinator's explicit helper request sends the selected report details and up to eight current-session comparison reports, plus the fixed sample candidate list, to Gemini. The original report remains unchanged.
- **Cost/limits:** Google AI Studio API access is governed by model/account rate limits and may incur charges depending on the account and tier. Check current [pricing](https://ai.google.dev/gemini-api/docs/pricing) and [rate limits](https://ai.google.dev/gemini-api/docs/rate-limits) before use; no cost or quota is assumed here.
- **Documentation:** [API quickstart](https://ai.google.dev/gemini-api/docs/get-started?lang=python), [structured output](https://ai.google.dev/gemini-api/docs/structured-output?lang=python), and [Python SDK](https://github.com/googleapis/python-genai).

No database, map service, hosting provider, messaging provider, or other external service is part of the POC.

## Important Failure Modes

- **Missing API key** → use local category/keyword rules for the submitted report and label the assessment `Local rules · not AI`; explain that Gemini needs a key for live AI analysis.
- **No API key during a demo** → allow loading sample records to explore the dashboard, with every score and recommendation visibly marked as an example, not Gemini output.
- **Gemini request failure or quota/network error** → show a concise failure message and retry option; offer local rules as a separate explicit action and label the result as non-AI.
- **Gemini helper failure** → preserve the report, show the error, and allow retry or explicit local helper suggestions; translation is not faked.
- **Unknown helper candidate ID** → reject the structured result instead of showing a resource or report that was not in the provided candidate lists.
- **Malformed or unsafe-looking AI response** → reject it through schema/range validation and offer retry; display the fixed emergency-services disclaimer independently of the model response.
- **Empty dashboard** → explain that submitted reports appear there and show the form.

## What Was Simplified and Why

- **One local Streamlit process with session-only report storage** instead of accounts, a shared database, and live synchronization — keeps setup small and is sufficient for a single-run demo; reports are lost when the app restarts.
- **Static sample volunteer statuses** instead of live nearby volunteer matching — the POC has no verified volunteer data or coordination service; sample status is labeled as such.
- **Static sample reports for no-key exploration** instead of fabricated AI output — reviewers can exercise dashboard behavior without credentials while the real Gemini path remains explicit and verifiable.
- **Structured Gemini assessment in the submit flow** instead of background dispatch or automatic assignment — keeps the AI kernel visible and verifiable in the short demo.
- **Small explicit category/keyword rule set** instead of blocking the form when there is no API key — makes a no-key demo possible while clearly distinguishing the fallback from AI.
- **Small sample roster and bounded suggestions** instead of live volunteer/supply integrations — the app can demonstrate matching UX without claiming real availability or dispatch.
- **A simple 1–5 score** instead of an operational triage protocol — easy to display for the prototype, explicitly not validated for real-world decisions.

## Decisions and Open Issues

- **Learner-selected:** Python, Streamlit, Google Gemini; one connected reporting-to-dashboard proof of concept; active/resolved status and a volunteer-status view.
- **Implementation convention:** use a simple 1–5 Gemini-generated score for display. It is not a medical or operational triage scale.
- **Learner-requested fallback:** use local category/keyword rules when no Gemini key is available, and offer the same fallback only after explicit choice if a Gemini request fails. Label this path as code-based and non-AI.
- **Implementation convention:** keep reports in Streamlit session state and label volunteer status as sample data, consistent with the PRD's current-run demo boundary.
- **Useful uncertainty:** no specific technical uncertainty was identified in the conversation. The build should verify early that the configured Gemini model and SDK return output accepted by the response schema; failure remains visible rather than being hidden by mock AI output.
- **Open questions:** none blocking implementation. The API key and access tier must be supplied/configured by the learner on their own machine; no credentials are requested in chat.
