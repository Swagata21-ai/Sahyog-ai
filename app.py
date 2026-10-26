from html import escape
import logging

import streamlit as st

from sahyog_ai.gemini import GeminiAssessmentError, assess_report
from sahyog_ai.models import EmergencyReport

logging.basicConfig(level=logging.INFO)

st.set_page_config(
    page_title="Sahyog AI | Relief response",
    page_icon="🫱🏽‍🫲🏾",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    :root {
      --ink: #142a24;
      --muted: #60736a;
      --green: #16704f;
      --green-dark: #0e4f39;
      --canvas: #f5f7f3;
      --line: #dfe7df;
    }
    .stApp { background: var(--canvas); }
    .block-container { max-width: 1320px; padding-top: 2rem; padding-bottom: 4rem; }
    [data-testid="stHeader"] { background: transparent; }
    .hero {
      padding: 1.8rem 2rem;
      border: 1px solid var(--line);
      border-radius: 22px;
      background: linear-gradient(115deg, #103d2f 0%, #176b4c 62%, #2c835e 100%);
      color: white;
      margin-bottom: 1.2rem;
    }
    .hero-kicker {
      color: #cde8d5; font-size: .78rem; font-weight: 750;
      letter-spacing: .14em; text-transform: uppercase;
    }
    .hero h1 { color: white; font-size: clamp(2rem, 4vw, 3rem); margin: .45rem 0; }
    .hero p { color: #e0eee4; margin: 0; font-size: 1.05rem; }
    .notice {
      border: 1px solid #ecd9a8; background: #fff8e8; color: #684d16;
      border-radius: 12px; padding: .85rem 1rem; margin: .8rem 0 1rem;
      font-size: .9rem;
    }
    .metric-card, .report-card, .volunteer-card {
      border: 1px solid var(--line); border-radius: 16px;
      background: white; padding: 1rem 1.15rem; margin-bottom: .85rem;
    }
    .score {
      display: inline-block; border-radius: 99px; background: #e5f2e9;
      color: #14583e; padding: .25rem .7rem; font-weight: 800;
    }
    .report-meta { color: var(--muted); font-size: .88rem; }
    div[data-testid="stTabs"] button { font-weight: 700; }
    div[data-testid="stForm"] {
      padding: 1.2rem; border: 1px solid var(--line);
      border-radius: 16px; background: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "reports" not in st.session_state:
    st.session_state.reports = []

st.markdown(
    """
    <div class="hero">
      <div class="hero-kicker">Community response desk</div>
      <h1>Sahyog AI</h1>
      <p>Turn urgent local reports into clearer next steps for relief teams.</p>
    </div>
    <div class="notice"><strong>Safety:</strong> This demo is not an emergency service.
    AI assessments are informational only. If someone is in immediate danger, contact
    local emergency services.</div>
    """,
    unsafe_allow_html=True,
)

report_tab, operations_tab = st.tabs(["＋  Submit a report", "▤  Operations"])

with report_tab:
    st.subheader("Tell us what is happening")
    st.caption("Share the essentials so the response team can assess the need.")
    with st.form("emergency_report", clear_on_submit=False):
        location = st.text_input(
            "Location",
            placeholder="Neighborhood, landmark, or address",
            max_chars=160,
        )
        category = st.selectbox(
            "What is needed?",
            ["Medical", "Food", "Water", "Shelter"],
        )
        description = st.text_area(
            "Describe the emergency",
            placeholder="What happened, who needs help, and what support is needed?",
            max_chars=1200,
            height=130,
        )
        submitted = st.form_submit_button(
            "Assess report with Gemini",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        missing_fields = [
            label
            for label, value in (
                ("location", location),
                ("description", description),
            )
            if not value.strip()
        ]
        if missing_fields:
            st.error("Please add " + " and ".join(missing_fields) + " before submitting.")
        else:
            try:
                with st.spinner("Gemini is reviewing the report…"):
                    assessment = assess_report(
                        location=location.strip(),
                        category=category,
                        description=description.strip(),
                    )
            except GeminiAssessmentError as exc:
                st.error(str(exc))
            else:
                report = EmergencyReport(
                    location=location.strip(),
                    category=category,
                    description=description.strip(),
                    assessment=assessment,
                )
                st.session_state.reports.insert(0, report)
                st.success("Assessment complete. The report is now in Operations.")
                st.rerun()

with operations_tab:
    reports = st.session_state.reports
    st.subheader("Relief operations")
    st.caption("Reports submitted during this app session.")
    if not reports:
        st.info("No assessed reports yet. Submit an emergency report to start the response queue.")
    for report in reports:
        st.markdown(
            f"""
            <div class="report-card">
              <div class="report-meta">{escape(report.category)} · {escape(report.location)} · {escape(report.status)}</div>
              <p>{escape(report.description)}</p>
              <span class="score">Urgency {report.assessment.severity_score}/5</span>
              <p><strong>Assessment:</strong> {escape(report.assessment.urgency_rationale)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.expander("Recommended coordination steps"):
            for index, step in enumerate(report.assessment.action_steps, start=1):
                st.write(f"{index}. {step}")
