---
doc: prd
status: approved
---

# Sahyog AI — Product Requirements

A rapid community disaster and relief coordination app for citizens needing help and local responders coordinating relief.
Source: `scope.md > The Unique Kernel`, `Who It's For`, and `The POC Boundary`.

## The Core Journey

1. A user opens Sahyog AI and can enter an emergency report or review the operations dashboard.
2. The person reporting an emergency enters a location, chooses Medical, Food, Water, or Shelter, describes the situation, and submits it.
3. Sahyog AI uses Gemini when configured, or transparent local rules without a key, to display an urgency estimate and coordination steps. The app identifies the source and makes clear that the result is not official emergency dispatch.
4. The new report and its assessment appear in the operations view so responders can review the need and current status.
5. A responder can mark the report resolved; unresolved reports remain active. The dashboard reflects the updated status.

Source: `scope.md > The Core Loop` and `What "Working" Looks Like`.

## Screens and Layout

The proof of concept uses one primary app surface with an emergency reporting area and an operations dashboard. The report area contains location, category, description, and a submit action. The operations area presents active and resolved reports with their category, location, description, assessment and source, recommendation, and status. Volunteer status is visible in the operations area.

No separate account, victim profile, or volunteer-management screen is required for this proof of concept.

Source: `scope.md > The POC Boundary`.

## Look and Feel

Fast, clear, and practical in an emergency context. Prioritize legibility and make report status and urgency easy to distinguish. The learner has not specified a visual reference or a more detailed style.

Source: `scope.md > Inspiration & Identity`.

## Features and Behavior

### Emergency report and AI assessment

- A reporter provides a location, selects one category (Medical, Food, Water, or Shelter), and enters a crisis description.
- When a Gemini key is configured, submitting a valid report requests a Gemini urgency assessment and step-by-step dispatch recommendation.
- Without a Gemini key, a valid report can be assessed by transparent local rules so the form remains usable. The result is labeled as non-AI, explains the simple rule basis, and is not represented as validated emergency triage.
- If a configured Gemini request fails, show the failure and allow retry or an explicit user choice to use the local rules instead. Never silently downgrade an attempted Gemini assessment.
- The assessment is displayed with the report and is not presented as a substitute for official emergency services.
- Required fields must be provided before a report can be submitted. Invalid or missing input gets a clear prompt and does not create a report.
- If Gemini is unavailable or returns unusable output, show a clear error and allow a retry. Do not fabricate an AI score or recommendation.

Acceptance criteria:
- [ ] A valid report can be submitted with all four fields and receives a Gemini-generated urgency score and action plan.
- [ ] Without a Gemini key, a valid report can be submitted and receives a clearly labeled local-rules estimate with an explanation of the matched rule or category baseline.
- [ ] A Gemini request failure remains visible and offers an explicit local-rules alternative; the result source is not mislabeled.
- [ ] The user can identify the report's urgency and recommendation after submission.
- [ ] Missing required input is explained, and no report is created.
- [ ] A Gemini failure is visible, offers retry, and does not appear as a successful assessment.

Source: `scope.md > The Unique Kernel`, `The Core Loop`, and `The POC Boundary`.

### Relief operations dashboard

- The dashboard shows reports created in the app, including their location, category, description, urgency assessment, recommendation, and active/resolved status.
- Reports are grouped or filterable by active and resolved status so responders can focus on outstanding needs.
- A responder can mark an active report resolved; the visible status updates. A resolved report can be returned to active.
- Volunteer status is represented in the dashboard as a simple operational view; full volunteer assignment and supply matching are outside this proof of concept.
- A user can load clearly labeled sample reports to explore the dashboard without a Gemini API key. Sample assessments must be identified as examples, never as Gemini output.
- When there are no reports, show an empty state that invites the user to submit a report.

Acceptance criteria:
- [ ] A successfully assessed report appears in the dashboard with its submitted details, assessment source, recommendation, and active status.
- [ ] Marking a report resolved updates its status and resolved view; returning it to active is reflected as well.
- [ ] With no reports, the dashboard explains that reports will appear after submission.
- [ ] Volunteer status is visible without implying that a volunteer has been dispatched or assigned.
- [ ] Sample reports can be loaded and cleared without an API key; every sample assessment is visibly labeled as illustrative and non-AI.

Source: `scope.md > The Core Loop` and `The POC Boundary`.

## States and Boundaries

- **First use / empty dashboard** — Explain that no reports have been submitted yet and provide a path to the report form.
- **Invalid report** — Identify the missing required information; do not submit the report.
- **Assessment in progress** — Indicate that the report is being analyzed while waiting for Gemini.
- **Gemini failure** — Explain that the AI assessment could not be completed and allow retry. Offer local rules only through an explicit action and label the resulting assessment as non-AI.
- **No Gemini key** — Use local rules for a valid form submission; label the result as a simple code-based estimate, not AI or validated triage.
- **No-key demo** — Valid report submissions use local category/keyword rules and are labeled non-AI; the user can also separately load explicitly labeled sample reports to explore dashboard filters and status controls.
- **Successful report** — Show the report and validated assessment in the operations view as active, with its source identified.
- **Resolved report** — Show resolved status in the dashboard; allow a responder to return it to active.
- **AI and safety boundary** — AI recommendations are informational prioritization support only. The app is not an emergency service; people facing immediate danger should contact local emergency services.
- **Demo boundary** — This proof of concept demonstrates reports entered in the current app run. It does not promise durable storage, live synchronization between users, verified volunteer availability, or real-world dispatch.

Source: `scope.md > The POC Boundary`, `Later`, and `Explicitly Cut`.

## Product Decisions

- Use the name Sahyog AI and the user-selected emergency categories Medical, Food, Water, and Shelter.
- Use Gemini to assess urgency and produce a step-by-step recommendation.
- When Gemini is unavailable, allow a transparent local rule-based estimate rather than blocking report submission; distinguish the source clearly.
- Include both active/resolved crisis status and a volunteer-status view in the relief operations dashboard.
- Allow dashboard exploration with explicitly labeled sample reports when no Gemini key is configured; real submissions use the separately labeled local-rules path.
- Keep this as a demonstrable proof of concept, not an operational emergency-response service.

Source: `scope.md > The Unique Kernel`, `The POC Boundary`, and `Explicitly Cut`.

## What We're Building

- A reporting interface for location, emergency category, and crisis description.
- Gemini-generated urgency assessment and dispatch recommendation for a valid report.
- A connected operations dashboard showing reports, AI output, active/resolved status, and volunteer status.
- An optional no-key demo dataset whose illustrative assessments are clearly distinguished from Gemini output.
- A local rule-based report-assessment path for no-key runs and an explicit opt-in after Gemini request failure.
- Clear empty, validation, in-progress, and AI-failure states.
- A visible informational-only emergency guidance boundary.

## Deferred From the POC

- Durable storage and reports that persist across restarts — not required to demonstrate the report-to-dashboard flow.
- Live synchronization between different users — the POC is not a deployed coordination service.
- Verified nearby volunteer availability, assignment, and supply matching — these require operational data and coordination beyond the current demo.
- Real-world dispatch and integration with emergency services — explicitly outside the POC and unsafe to imply.

## Possible Later Enhancements

With appropriate operational partners and verified data, a later version could explore live coordination, nearby volunteer and supply matching, and durable shared reports.

## Non-Goals

- Providing authoritative medical, rescue, or dispatch instructions.
- Replacing emergency services or directing people to rely on this demo during a real emergency.
- Claiming that volunteers shown in the demo are verified, available, or assigned.

## Open Questions

- None blocking the proof-of-concept behavior described here. The review-format preference is visual HTML, as recorded in `learner-profile.md`.
