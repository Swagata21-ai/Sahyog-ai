# Sahyog AI

A rapid community disaster and relief coordination proof of concept. Submit an emergency report, receive a Gemini assessment when configured or a clearly labeled local-rules estimate otherwise, then review the report and suggested coordination steps in the operations view.

> **Safety:** This demo is not an emergency service. AI output is informational prioritization support, not medical, rescue, or dispatch instructions. For immediate danger, contact local emergency services.

## Run locally

Requirements: Python 3.10+. Internet access and a Gemini API key enable live Gemini assessments; the form also works without a key using clearly labeled local rule-based estimates.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

To use Gemini, add your API key to the local `.env` file as `GEMINI_API_KEY=...`. `.env` is ignored by Git; never commit or share the key. You can optionally set `GEMINI_MODEL` in that file. The default model is `gemini-3.8-flash`. Without a key, report submissions use local keyword/category rules, visibly labeled as non-AI and not validated for real emergency triage. If a configured Gemini request fails, the app shows the error and lets you retry or explicitly choose local rules; it never switches silently.

Start the app:

```powershell
streamlit run app.py
```

Open the local URL printed by Streamlit, usually `http://localhost:8501`.

## Try the proof of concept

1. Submit a sample report with a location, category, and situation description.
2. Review the assessment source, urgency score, and coordination steps in Operations.
3. Resolve or reactivate a report and inspect the dashboard filters.
4. Volunteer statuses in the demo are sample data, not confirmed availability or assignments.

Without a Gemini API key, submit a report to try the local rules estimate, or use **Load sample reports** in Operations to explore the dashboard. Local rules use a small keyword list and category baselines; they do not understand context, can miss or misread details, and are not validated triage. Rule-based estimates and sample records are explicitly labeled and are not Gemini results.

Reports live only in the current app session and are lost when the process restarts. The app does not synchronize between users or contact volunteers and emergency services. Gemini API usage may be subject to account rate limits or charges; check Google's current [pricing](https://ai.google.dev/gemini-api/docs/pricing) before use.

## Checks

```powershell
python -m compileall -q app.py sahyog_ai tests
python -m unittest discover -s tests -v
```
