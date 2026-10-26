from html import escape
import logging

import streamlit as st

from sahyog_ai.gemini import GeminiAssessmentError, assess_report
from sahyog_ai.models import Assessment, EmergencyReport

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
    .score-medium { background: #fff1c9; color: #71520b; }
    .score-high { background: #fbe2dc; color: #873c2b; }
    .status {
      display: inline-block; border-radius: 99px; padding: .2rem .65rem;
      font-size: .8rem; font-weight: 750;
    }
    .status-active { background: #e5f2e9; color: #14583e; }
    .status-resolved { background: #e9edf0; color: #465660; }
    .source-demo {
      display: inline-block; border-radius: 99px; padding: .2rem .65rem;
      background: #fff1c9; color: #71520b; font-size: .8rem; font-weight: 750;
    }
    .source-gemini {
      display: inline-block; border-radius: 99px; padding: .2rem .65rem;
      background: #e5f2e9; color: #14583e; font-size: .8rem; font-weight: 750;
    }
    .report-meta { color: var(--muted); font-size: .88rem; }
    .muted-note { color: var(--muted); font-size: .86rem; }
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


def make_demo_reports() -> list[EmergencyReport]:
    return [
        EmergencyReport(
            location="Riverside Ward (sample)",
            category="Water",
            description=(
                "Sample report: heavy rain is affecting several ground-floor homes; "
                "residents request clean water."
            ),
            assessment=Assessment(
                severity_score=4,
                urgency_rationale="Illustrative example only; not a real assessment.",
                action_steps=[
                    "Example: confirm reported needs with a local coordinator.",
                    "Example: check whether a verified clean-water source is nearby.",
                ],
            ),
            assessment_source="Demo example",
        ),
        EmergencyReport(
            location="Market Street (sample)",
            category="Food",
            description=(
                "Sample report: a community center requests food packs for residents."
            ),
            assessment=Assessment(
                severity_score=3,
                urgency_rationale="Illustrative example only; not a real assessment.",
                action_steps=[
                    "Example: confirm the number of people and dietary needs.",
                    "Example: identify a verified distribution point.",
                ],
            ),
            assessment_source="Demo example",
        ),
        EmergencyReport(
            location="East Clinic (sample)",
            category="Medical",
            description=(
                "Sample report: coordinators have acknowledged a request for basic supplies."
            ),
            assessment=Assessment(
                severity_score=2,
                urgency_rationale="Illustrative example only; not a real assessment.",
                action_steps=[
                    "Example: confirm the request with the reporting coordinator.",
                ],
            ),
            assessment_source="Demo example",
            status="Resolved",
        ),
    ]


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
    st.caption(
        "Share the essentials so the response team can assess the need. "
        "To explore the dashboard without a Gemini key, open Operations and load sample reports."
    )
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
    has_demo_reports = any(
        report.assessment_source == "Demo example" for report in reports
    )
    active_count = sum(report.status == "Active" for report in reports)
    resolved_count = len(reports) - active_count
    urgent_count = sum(report.assessment.severity_score >= 4 for report in reports)

    st.subheader("Relief operations")
    st.caption("Reports submitted during this app session.")
    demo_action_column, demo_note_column = st.columns([1, 2])
    with demo_action_column:
        if has_demo_reports:
            if st.button("Clear sample reports", use_container_width=True):
                st.session_state.reports = [
                    report
                    for report in reports
                    if report.assessment_source != "Demo example"
                ]
                st.rerun()
        elif st.button("Load sample reports", use_container_width=True):
            st.session_state.reports.extend(make_demo_reports())
            st.rerun()
    with demo_note_column:
        st.caption(
            "No API key needed for examples. Sample scores and steps are illustrative, "
            "not Gemini output or real triage."
        )

    metric_columns = st.columns(3)
    metric_columns[0].metric("Active", active_count)
    metric_columns[1].metric("Resolved", resolved_count)
    metric_columns[2].metric("Urgency 4–5", urgent_count)

    report_column, volunteer_column = st.columns([2.2, 1], gap="large")

    with report_column:
        st.markdown("#### Response queue")
        status_filter = st.selectbox(
            "Show reports",
            ["All", "Active", "Resolved"],
            label_visibility="collapsed",
        )
        visible_reports = [
            report
            for report in reports
            if status_filter == "All" or report.status == status_filter
        ]

        if not reports:
            st.info("No assessed reports yet. Submit an emergency report to start the response queue.")
        elif not visible_reports:
            st.info(f"No {status_filter.lower()} reports right now.")

        visible_reports.sort(
            key=lambda report: (
                report.status != "Active",
                -report.assessment.severity_score,
                -report.created_at.timestamp(),
            )
        )
        for report in visible_reports:
            score = report.assessment.severity_score
            score_class = "score-high" if score >= 4 else "score-medium" if score == 3 else ""
            status_class = "status-active" if report.status == "Active" else "status-resolved"
            is_demo = report.assessment_source == "Demo example"
            source_class = "source-demo" if is_demo else "source-gemini"
            assessment_label = (
                "Demo example · not Gemini" if is_demo else "Gemini assessment"
            )
            rationale_label = (
                "Illustrative example rationale · not AI"
                if is_demo
                else "AI urgency rationale"
            )
            steps_label = (
                "Example coordination steps · not AI"
                if is_demo
                else "Recommended coordination steps"
            )

            with st.container(border=True):
                heading_column, action_column = st.columns([3, 1])
                with heading_column:
                    st.text(f"{report.category} · {report.location}")
                    st.markdown(
                        f'<span class="score {score_class}">Urgency {score}/5</span> '
                        f'<span class="status {status_class}">{escape(report.status)}</span> '
                        f'<span class="{source_class}">{escape(assessment_label)}</span>',
                        unsafe_allow_html=True,
                    )
                with action_column:
                    button_label = (
                        "Mark resolved" if report.status == "Active" else "Reopen report"
                    )
                    if st.button(
                        button_label,
                        key=f"status_{report.id}",
                        use_container_width=True,
                    ):
                        report.status = (
                            "Resolved" if report.status == "Active" else "Active"
                        )
                        st.rerun()

                st.text(report.description)
                st.markdown(f"**{rationale_label}**")
                st.text(report.assessment.urgency_rationale)
                with st.expander(steps_label):
                    for index, step in enumerate(report.assessment.action_steps, start=1):
                        st.text(f"{index}. {step}")

    with volunteer_column:
        st.markdown("#### Volunteer status")
        st.caption("Illustrative sample data only · not connected to real volunteers")
        volunteer_samples = [
            {"Volunteer": "Sample responder A", "Status": "Available (sample)"},
            {"Volunteer": "Sample responder B", "Status": "Preparing supplies (sample)"},
            {"Volunteer": "Sample responder C", "Status": "Unavailable (sample)"},
        ]
        for volunteer in volunteer_samples:
            st.markdown(
                f"""
                <div class="volunteer-card">
                  <strong>{escape(volunteer["Volunteer"])}</strong><br>
                  <span class="muted-note">{escape(volunteer["Status"])}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
