---
doc: spec
status: approved
---

# Sahyog AI — Technical Spec

## How This Works, In Plain Language

Sahyog AI runs on your computer as a Streamlit app in a browser tab. You fill in a report, and the app sends its details to Google's Gemini service, which returns a severity score and action steps. The app checks that answer, then keeps the completed report in memory while the app is running and shows it on the operations dashboard. You can change a report's status there. The volunteer panel uses clearly labeled sample information; it does not claim that real people are available or dispatched.

There is no account, database, or live multi-user connection in this proof of concept. Reports disappear when the app process restarts. This keeps the demo small while preserving the central idea: a real Gemini assessment connected to a usable operations view.

## The Core Journey Through the System

1. A person enters a location, category, and crisis description in the Streamlit form.
2. `app.py` checks the required fields and passes the report text to `sahyog_ai/gemini.py`.
3. The Gemini service uses the API key from the local environment and requests structured JSON from Gemini. `sahyog_ai/models.py` validates the returned score and action steps.
4. If the response is valid, `app.py` creates a report and stores it in Streamlit's session state. The same run displays it on the operations dashboard.
5. A responder changes the report status in the dashboard. The in-memory record updates and Streamlit redraws the current view.
6. If there is no API key, the service call fails, or the answer cannot be validated, the app shows an explicit error. It does not create a successful-looking report or invent an AI result.

PRD ref: `prd.md > The Core Journey`, `Features and Behavior > Emergency report and AI assessment`, and `Features and Behavior > Relief operations dashboard`.

## Stack

- **Python 3.10+** — the learner selected Python. The minimum supports the type syntax and SDK baseline used by the app.
- **Streamlit** — the learner selected Streamlit for a quick interactive browser interface. Its session state holds reports only for the current app session.
- **Google GenAI Python SDK (`google-genai`)** — calls Gemini using the official Python client and structured output. Tradeoff: the AI feature requires internet access, an API key, and may be subject to account quotas or billing.
- **Pydantic** — validates the structured AI response before it is shown or saved into the current session.
- **python-dotenv** — optionally loads the ignored local `.env` file for the API key and model name.

Documentation:
- [Python](https://docs.python.org/3/)
- [Streamlit documentation](https://docs.streamlit.io/)
- [Google GenAI Python SDK](https://github.com/googleapis/python-genai)
- [Gemini API quickstart](https://ai.google.dev/gemini-api/docs/get-started?lang=python)
- [Gemini structured output](https://ai.google.dev/gemini-api/docs/structured-output?lang=python)
- [Pydantic documentation](https://docs.pydantic.dev/latest/)

## Where It Runs and How Someone Tries It

- **Runtime:** a local Python process opens the Streamlit interface in a browser, normally at `http://localhost:8501`.
- **Requirements:** Python 3.10+, dependencies installed from `requirements.txt`, internet access for Gemini, and a Gemini API key stored locally as `GEMINI_API_KEY`. Never paste the key into chat or commit it. `.env` is ignored by Git; `.env.example` contains no secret.
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

Use a clean, legible operations dashboard with a calm neutral canvas, dark readable text, and green as the primary action color. Use distinct amber/red urgency treatments and clear active/resolved badges so color is not the only status cue. Keep form labels and emergency-safety messaging direct and practical. Use Streamlit's layout, columns, forms, and status elements rather than adding a styling framework; exact custom typography and pixel-level control are limited by Streamlit's native components.

PRD ref: `prd.md > Look and Feel`.

## Components

### Emergency report form (`app.py`)

Collects location, category, and description; rejects missing values; shows the emergency-service disclaimer; and initiates the AI assessment. A report is added only after a valid AI result is received.

Implements `prd.md > Features and Behavior > Emergency report and AI assessment`.

### Gemini assessment service (`sahyog_ai/gemini.py`)

Builds a focused prompt from the submitted fields, asks the configured Gemini model for a structured assessment, and turns missing credentials, API errors, or unusable output into an explicit failure for the UI to display. It does not fabricate a fallback score or recommendation.

Implements `prd.md > Features and Behavior > Emergency report and AI assessment`.

### Assessment and report data (`sahyog_ai/models.py`)

Defines the validated AI assessment (integer urgency from 1 to 5, short rationale, and ordered action steps) and the report record (unique ID, submitted details, assessment, creation time, and active/resolved status). The 1–5 range is an implementation convention for a legible demo scale, not a validated emergency triage standard.

Implements `prd.md > Features and Behavior > Emergency report and AI assessment` and `Relief operations dashboard`.

### Relief operations dashboard (`app.py`)

Reads reports from session state, summarizes and filters active/resolved items, displays submitted details with validated AI results, and updates a report's status on responder action. Shows a useful empty state when there are no reports.

Implements `prd.md > Features and Behavior > Relief operations dashboard`.

### Volunteer status panel (`app.py`)

Displays a small, static, explicitly labeled sample volunteer-status view. It demonstrates the requested dashboard content without representing real availability, matching, or dispatch.

Implements `prd.md > Features and Behavior > Relief operations dashboard` and `States and Boundaries`.

## Data Model

- **EmergencyReport:** `id` (unique string), `location` (string), `category` (Medical/Food/Water/Shelter), `description` (string), `urgency_score` (integer 1–5), `urgency_rationale` (string), `action_steps` (list of strings), `status` (active/resolved), and `created_at` (timestamp).
- **Assessment:** Gemini-generated score, short rationale, and ordered recommendations, validated against a Pydantic schema before creating an EmergencyReport.
- **Volunteer sample:** a small fixed list of example names/statuses in the app; clearly labeled as demonstration data and not connected to real volunteers.
- **Storage and updates:** reports live in `st.session_state` for the current browser/app session. New reports are appended only after successful validation; status actions update the corresponding in-memory report. Refreshes during the same session preserve state according to Streamlit's session behavior; ending/restarting the app loses reports. There is no account, cross-user sharing, or durable storage.

## File Structure

```text
sahyog-ai/
├── app.py                    # Streamlit report form, dashboard, session state, sample volunteers
├── sahyog_ai/
│   ├── __init__.py           # Package marker
│   ├── gemini.py             # Gemini request and API error handling
│   └── models.py             # Pydantic response validation and report types
├── tests/
│   └── test_core.py          # Built-in unittest checks for validation and key errors
├── requirements.txt          # Streamlit, google-genai, and Pydantic dependencies
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
- **Cost/limits:** Google AI Studio API access is governed by model/account rate limits and may incur charges depending on the account and tier. Check current [pricing](https://ai.google.dev/gemini-api/docs/pricing) and [rate limits](https://ai.google.dev/gemini-api/docs/rate-limits) before use; no cost or quota is assumed here.
- **Documentation:** [API quickstart](https://ai.google.dev/gemini-api/docs/get-started?lang=python), [structured output](https://ai.google.dev/gemini-api/docs/structured-output?lang=python), and [Python SDK](https://github.com/googleapis/python-genai).

No database, map service, hosting provider, messaging provider, or other external service is part of the POC.

## Important Failure Modes

- **Missing API key** → explain how to set `GEMINI_API_KEY`; keep the report unsubmitted and do not invent an assessment.
- **Gemini request failure or quota/network error** → show a concise failure message and retry option; do not add an unassessed report to the operations list.
- **Malformed or unsafe-looking AI response** → reject it through schema/range validation and offer retry; display the fixed emergency-services disclaimer independently of the model response.
- **Empty dashboard** → explain that submitted reports appear there and show the form.

## What Was Simplified and Why

- **One local Streamlit process with session-only report storage** instead of accounts, a shared database, and live synchronization — keeps setup small and is sufficient for a single-run demo; reports are lost when the app restarts.
- **Static sample volunteer statuses** instead of live nearby volunteer matching — the POC has no verified volunteer data or coordination service; sample status is labeled as such.
- **Structured Gemini assessment in the submit flow** instead of background dispatch or automatic assignment — keeps the AI kernel visible and verifiable in the short demo.
- **A simple 1–5 score** instead of an operational triage protocol — easy to display for the prototype, explicitly not validated for real-world decisions.

## Decisions and Open Issues

- **Learner-selected:** Python, Streamlit, Google Gemini; one connected reporting-to-dashboard proof of concept; active/resolved status and a volunteer-status view.
- **Implementation convention:** use a simple 1–5 Gemini-generated score for display. It is not a medical or operational triage scale.
- **Implementation convention:** keep reports in Streamlit session state and label volunteer status as sample data, consistent with the PRD's current-run demo boundary.
- **Useful uncertainty:** no specific technical uncertainty was identified in the conversation. The build should verify early that the configured Gemini model and SDK return output accepted by the response schema; failure remains visible rather than being hidden by mock AI output.
- **Open questions:** none blocking implementation. The API key and access tier must be supplied/configured by the learner on their own machine; no credentials are requested in chat.
