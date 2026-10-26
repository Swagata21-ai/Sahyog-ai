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

- [x] **2. Review and manage relief operations**
  Becomes usable: The dashboard shows submitted reports with clear urgency, active/resolved controls, empty and filtered views, and explicitly labeled sample volunteer statuses.
  Why now: Once the AI kernel works, responders can use its output in the agreed operations view; this finishes the core journey without adding persistence or real volunteer matching.
  PRD ref: `prd.md > The Core Journey`; `prd.md > Features and Behavior > Relief operations dashboard`; `prd.md > States and Boundaries`
  Spec ref: `spec.md > Components > Relief operations dashboard`; `spec.md > Components > Volunteer status panel`; `spec.md > Data Model`; `spec.md > Look and Feel`
  Build: Add the complete operations layout, active/resolved filters and status updates, empty state, sample volunteer panel, and responsive visual polish following the spec.
  Verify (mechanical): Run `python -m compileall -q app.py sahyog_ai tests` and `python -m unittest discover -s tests -v`; start Streamlit, exercise report submission/error handling and active/resolved transitions, and confirm the page responds without runtime errors.
  Learner check: Open the app and review an assessed report in the operations dashboard; switch it between active and resolved, inspect both views, and confirm the volunteer panel is labeled as sample data.
  Commit: `Add relief operations dashboard`

- [x] **3. Add translation and coordination helpers**
  Becomes usable: A coordinator can translate a report, review likely duplicate reports, and get suggestions drawn only from the fixed sample volunteer/supply roster. Gemini results are labeled as AI suggestions; without a key, local duplicate/resource suggestions are clearly non-AI and translation is unavailable.
  Why now: These helpers extend the existing report-to-operations flow without changing core submission. Restricting recommendations to known sample IDs keeps suggestions reviewable and prevents invented dispatch actions.
  PRD ref: `prd.md > Features and Behavior > Report translation and coordination suggestions`; `prd.md > States and Boundaries`
  Spec ref: `spec.md > Components > Report coordination helpers`; `spec.md > Components > Sample relief roster`; `spec.md > Data Model`; `spec.md > Important Failure Modes`
  Build: Add validated helper response types, a Gemini structured-output request for selected-language translation, possible duplicates, and allow-listed sample resource suggestions; add transparent local duplicate/resource suggestions and explicit retry/local fallback; show the original beside the translation and mark every recommendation as unverified.
  Verify (mechanical): Run `python -m compileall -q app.py sahyog_ai tests` and `python -m unittest discover -s tests -v`; test structured Gemini request/validation, candidate-ID rejection, no-key labeling, original-text preservation, and visible failure with explicit local fallback.
  Learner check: Submit/load sample reports, request helpers on one report, and confirm translation, possible duplicates, and suggested sample resources are distinct from confirmed actions.
  Commit: `Add report translation and coordination helpers`

- [ ] **4. Refresh the interface with a colorful visual system**
  Becomes usable: The report form and operations dashboard use a brighter, colorful palette with clear cards and badges while keeping urgency, report status, and source easy to distinguish.
  Why now: Apply the requested visual update after the new helper content exists so its layout, labels, and safety notes are styled together rather than retouched twice.
  PRD ref: `prd.md > Look and Feel`; `prd.md > Screens and Layout`
  Spec ref: `spec.md > Look and Feel`; `spec.md > Components > Emergency report form`; `spec.md > Components > Relief operations dashboard`
  Build: Refresh the Streamlit CSS and visible labels/cards with teal, violet, coral, and sunny accents; preserve accessible contrast, responsive layout, and text labels independent of color.
  Verify (mechanical): Run the full compile and unit-test commands; open the local app and inspect both tabs for legibility, overflow, source/status badges, and the emergency disclaimer.
  Learner check: Open both tabs, submit a fictional report, inspect helper results, and tell me what feels clear or crowded.
  Commit: `Refresh Sahyog AI colorful interface`

## Hands-on Checkpoints

- [x] Early usable behavior explored — learner observed the missing-key message; the error path was verified to save no report, and no change was requested.
- [ ] Final kick-the-tires exploration and feedback completed — after slice 2, try the full journey and report anything broken, confusing, or worth changing.

## Final Review

- [x] Add a no-key dashboard demo with explicitly labeled sample assessments; verify it never presents samples as Gemini output.
- [x] Add a no-key local-rules report path and explicit Gemini-failure fallback; verify all results identify their source and remain clearly non-AI when rule-based.
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

- Added the requested translation, possible duplicate detection, and sample volunteer/supply suggestions; all are optional coordinator aids, never real assignment or dispatch. Added a colorful UI refresh. Gemini is used when configured; no-key local suggestions remain labeled non-AI and translation is unavailable.
- Implemented report translation, possible duplicate detection, and bounded sample-resource suggestions with explicit source labels, opt-in local fallback, and no-key rules; structured response, candidate-ID allowlisting, UI fallback, and app integration pass tests. All 22 unit tests and compile checks passed. Live Gemini output requires a local key.
- Live Gemini output was not verified in this environment because no `GEMINI_API_KEY` is configured; tests cover request wiring, response validation, and visible missing-key/transport failures. A real assessment still needs a locally configured key.
- Added a no-key dashboard preview so hackathon reviewers can explore operations controls without credentials; sample results remain explicitly non-AI and real Gemini submissions still require a key.
- Added a no-key report submission path using transparent local rules at the learner's request; Gemini remains the live AI path when configured, and fallback after a request failure requires an explicit choice.
- Verified local baseline and keyword scoring, missing-field handling, report submission/source labels, explicit local fallback and retry after mocked Gemini failure, plus compileall and all 17 unit tests. Live Gemini output still requires a locally configured key.
