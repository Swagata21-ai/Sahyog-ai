---
doc: checklist
status: approved
---

# Build Checklist

Build mode: fast

## Slices

- [x] **1. Submit an emergency and see Gemini's assessment**
  Becomes usable: A local Streamlit app accepts a valid emergency report, sends it to Gemini, and shows a validated urgency score and action steps alongside the report. Missing credentials or failed/invalid AI output is shown as an error, never as a fabricated success.
  Why now: This bootstraps the app while proving the unique kernel early. The real report-to-Gemini-to-screen flow surfaces API and response-shape risk before dashboard refinements.
  PRD ref: `prd.md > The Core Journey`; `prd.md > Features and Behavior > Emergency report and AI assessment`
  Spec ref: `spec.md > Stack`; `spec.md > Components > Emergency report form`; `spec.md > Components > Gemini assessment service`; `spec.md > Components > Assessment and report data`; `spec.md > Where It Runs and How Someone Tries It`
  Build: Create the Streamlit app and dependencies; add validated assessment/report types, the official Gemini structured-output call, local key configuration guidance, report submission and in-session storage, safety copy, and a visible assessment result.
  Verify (mechanical): Run `python -m compileall -q app.py sahyog_ai tests`; run `python -m unittest discover -s tests -v` for assessment validation, structured Gemini request wiring, and status controls; start Streamlit and confirm the local page responds. If no API key is configured, submit a valid report and confirm the app reports the missing key without creating a fake assessed report.
  Learner check: Open the local app, submit a sample emergency with your own locally configured Gemini key, and check that its urgency score and action steps appear. If you do not have a key configured yet, check that the app explains the missing key and does not invent an AI result.
  Commit: `Build Gemini emergency assessment flow`

- [ ] **2. Review and manage relief operations**
  Becomes usable: The dashboard shows submitted reports with clear urgency, active/resolved controls, empty and filtered views, and explicitly labeled sample volunteer statuses.
  Why now: Once the AI kernel works, responders can use its output in the agreed operations view; this finishes the core journey without adding persistence or real volunteer matching.
  PRD ref: `prd.md > The Core Journey`; `prd.md > Features and Behavior > Relief operations dashboard`; `prd.md > States and Boundaries`
  Spec ref: `spec.md > Components > Relief operations dashboard`; `spec.md > Components > Volunteer status panel`; `spec.md > Data Model`; `spec.md > Look and Feel`
  Build: Add the complete operations layout, active/resolved filters and status updates, empty state, sample volunteer panel, and responsive visual polish following the spec.
  Verify (mechanical): Run `python -m compileall -q app.py sahyog_ai tests` and `python -m unittest discover -s tests -v`; start Streamlit, exercise report submission/error handling and active/resolved transitions, and confirm the page responds without runtime errors.
  Learner check: Open the app and review an assessed report in the operations dashboard; switch it between active and resolved, inspect both views, and confirm the volunteer panel is labeled as sample data.
  Commit: `Add relief operations dashboard`

## Hands-on Checkpoints

- [x] Early usable behavior explored — learner observed the missing-key message; the error path was verified to save no report, and no change was requested.
- [ ] Final kick-the-tires exploration and feedback completed — after slice 2, try the full journey and report anything broken, confusing, or worth changing.

## Final Review

- [ ] Final review complete — feedback resolved and learner confirms ready to ship

## Code Tour and App Map

- [ ] Learning activity complete — focused on the real Gemini report flow and its verification
- [ ] Optional edit and transfer reflection addressed — offered/declined/already covered/not applicable as appropriate
- [ ] `devpost/app-map.html` generated from finished code, checked, and shown, including a project-grounded practice to reuse

Activity and evidence: [what actually happened; real document/test/code references; unfinished work if interrupted]
Route and stops: [actual paths and symbols; guided stops completed, or reference-only route]
Edit outcome: [tried/kept/reverted/declined/not applicable; verification if changed]
Reflection: [offered/answered/declined/already covered — personal answer belongs only in the ignored profile]
Activity mode: [live app and editor, explicit static fallback, focused alternative, prior practice, or recap]

## Revisions
