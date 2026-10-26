---
doc: scope
status: approved
---

# Sahyog AI

A rapid community disaster and relief coordination app that uses Gemini AI to help prioritize local emergencies and coordinate relief.

## The Unique Kernel
Gemini turns a citizen's urgent local report into a severity score and a step-by-step dispatch recommendation, helping local responders prioritize what needs attention. The operations view connects that assessment to active reports, volunteers, and relief needs.

## Who It's For
Citizens and victims who need immediate help or essentials such as food, clean water, medical aid, or shelter; and local NGO teams, volunteers, and rescue coordinators organizing a response.

## The Core Loop
A citizen submits a location, emergency category, and description. With Gemini configured, the app returns its urgency assessment and next steps; without a key, a clearly labeled local rule-based estimate keeps the demo form usable. Responders review the report and its assessment source on the operations dashboard and track whether it is active or resolved.

## Inspiration & Identity
Fast, clear, and practical in an emergency context. The learner chose Python, Streamlit, and Google Gemini for a rapid interactive proof of concept. Specific visual references are not established.

## Why This Matters to the Learner
The learner wants to build Sahyog AI and get a working proof of concept.

## What "Working" Looks Like
In a short demo, submit a local emergency report and see Gemini return a severity score and actionable dispatch recommendation, then see the report represented in the relief-operations view with its status. That AI-assisted prioritization is the key "oh, that's useful" moment.

## The POC Boundary
- An emergency dispatch form for location, category (medical, food, water, shelter), and crisis description.
- Gemini-powered urgency scoring and a step-by-step dispatch recommendation.
- A relief operations dashboard showing reports as active or resolved and volunteer status.
- A demonstrable coordination flow connecting a report and its AI assessment to the operations view.
- An explicitly labeled sample-data path to explore dashboard behavior without an API key; sample results must not be presented as Gemini output.
- A transparent local rule-based estimate when Gemini is not configured, labeled as non-AI and not validated for real emergency triage.
- Optional report helpers to translate a report, flag possible duplicate reports, and suggest matches from a fixed sample volunteer/supply roster. These are suggestions for a human coordinator, never actual assignments.
- A brighter, colorful interface that keeps status, source, and urgency labels legible.

## Later
- Real-time coordination and operational deployment for actual emergencies.
- More complete nearby volunteer and supply matching beyond the proof-of-concept flow.

## Explicitly Cut
- Replacing official emergency services or treating AI output as authoritative dispatch instructions; the POC demonstrates coordination, not real-world emergency response.
