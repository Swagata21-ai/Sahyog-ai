import logging
from html import escape

import streamlit as st

from sahyog_ai.gemini import (
    GeminiAssessmentError,
    assess_report,
    has_gemini_api_key,
)
from sahyog_ai.local_triage import assess_with_local_rules
from sahyog_ai.models import (
    Assessment,
    AssessmentSource,
    EmergencyReport,
    OperationsAssistance,
)
from sahyog_ai.operations_assist import (
    OperationsAssistError,
    SAMPLE_SUPPLIES,
    SAMPLE_VOLUNTEERS,
    TARGET_LANGUAGES,
    analyze_with_gemini,
    local_suggestions,
)

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
      --ink: #20203c;
      --muted: #656783;
      --violet: #6846d7;
      --violet-dark: #5031b2;
      --canvas: #f7f5ff;
      --line: #e5e1f2;
    }
    .stApp {
      background: linear-gradient(160deg, #f7f5ff 0%, #fff9f4 48%, #f2fbff 100%);
      color: var(--ink);
    }
    .block-container { max-width: 1380px; padding-top: 1.7rem; padding-bottom: 4rem; }
    [data-testid="stHeader"] { background: transparent; }
    .hero {
      padding: 2rem 2.2rem;
      border: 1px solid #7560df;
      border-radius: 24px;
      background: linear-gradient(115deg, #4430a8 0%, #7850da 55%, #e66e9a 100%);
      color: white;
      margin-bottom: 1.25rem;
      box-shadow: 0 16px 40px rgba(83, 57, 171, .18);
    }
    .hero-kicker {
      color: #f1dfff; font-size: .78rem; font-weight: 750;
      letter-spacing: .14em; text-transform: uppercase;
    }
    .hero h1 { color: white; font-size: clamp(2rem, 4vw, 3rem); margin: .45rem 0; }
    .hero p { color: #f8efff; margin: 0; font-size: 1.05rem; }
    .feature-pills { display: flex; flex-wrap: wrap; gap: .55rem; margin-top: 1.15rem; }
    .feature-pill {
      display: inline-block; padding: .35rem .75rem; border-radius: 99px;
      background: rgba(255, 255, 255, .17); border: 1px solid rgba(255, 255, 255, .34);
      color: white; font-size: .82rem; font-weight: 700;
    }
    .notice {
      border: 1px solid #ffc5a6; background: #fff3eb; color: #793b24;
      border-radius: 14px; padding: .9rem 1rem; margin: .8rem 0 1rem;
      font-size: .9rem;
    }
    .metric-card, .report-card, .volunteer-card {
      border: 1px solid var(--line); border-radius: 17px;
      background: white; padding: 1rem 1.15rem; margin-bottom: .85rem;
    }
    [data-testid="stMetric"] {
      padding: .8rem 1rem; border: 1px solid var(--line); border-radius: 16px;
      background: linear-gradient(145deg, #fff 0%, #f5f1ff 100%);
      box-shadow: 0 5px 18px rgba(48, 43, 100, .05);
    }
    [data-testid="stMetricLabel"] { color: var(--muted); }
    [data-testid="stMetricValue"] { color: var(--ink); }
    div[data-testid="stVerticalBlockBorderWrapper"] {
      border-color: var(--line); border-radius: 18px; background: rgba(255, 255, 255, .9);
    }
    .score {
      display: inline-block; border-radius: 99px; background: #dff7f1;
      color: #126351; padding: .28rem .72rem; font-weight: 800;
    }
    .score-medium { background: #fff0c7; color: #79530a; }
    .score-high { background: #ffe0e5; color: #932d4a; }
    .status {
      display: inline-block; border-radius: 99px; padding: .2rem .65rem;
      font-size: .8rem; font-weight: 750;
    }
    .status-active { background: #e1f6ec; color: #176444; }
    .status-resolved { background: #edf0f7; color: #515b75; }
    .source-demo {
      display: inline-block; border-radius: 99px; padding: .2rem .65rem;
      background: #fff0c7; color: #79530a; font-size: .8rem; font-weight: 750;
    }
    .source-gemini {
      display: inline-block; border-radius: 99px; padding: .2rem .65rem;
      background: #eee8ff; color: #5538b7; font-size: .8rem; font-weight: 750;
    }
    .source-local {
      display: inline-block; border-radius: 99px; padding: .2rem .65rem;
      background: #e4f3ff; color: #23577c; font-size: .8rem; font-weight: 750;
    }
    .report-meta { color: var(--muted); font-size: .88rem; }
    .muted-note { color: var(--muted); font-size: .86rem; }
    div[data-testid="stTabs"] button { font-weight: 700; }
    div[data-testid="stTabs"] button[aria-selected="true"] {
      color: var(--violet); border-bottom-color: var(--violet);
    }
    div[data-testid="stForm"] {
      padding: 1.3rem; border: 1px solid var(--line);
      border-radius: 18px; background: rgba(255, 255, 255, .94);
      box-shadow: 0 8px 26px rgba(48, 43, 100, .06);
    }
    .stButton button[kind="primary"] {
      background: linear-gradient(100deg, #6344d2, #a34fcd);
      border-color: #6344d2; color: white; font-weight: 750;
    }
    .stButton button[kind="primary"]:hover {
      background: var(--violet-dark); border-color: var(--violet-dark); color: white;
    }
    [data-testid="stExpander"] {
      border-color: #ddd5f4; border-radius: 14px; background: rgba(255, 255, 255, .78);
    }
    .volunteer-card {
      border-color: #dcd5f2;
      background: linear-gradient(130deg, #fff 0%, #f7f2ff 100%);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "reports" not in st.session_state:
    st.session_state.reports = []
if "pending_report" not in st.session_state:
    st.session_state.pending_report = None
if "pending_gemini_error" not in st.session_state:
    st.session_state.pending_gemini_error = ""
if "assistance_results" not in st.session_state:
    st.session_state.assistance_results = {}
if "assistance_errors" not in st.session_state:
    st.session_state.assistance_errors = {}
key_configured = has_gemini_api_key()


def save_report(
    location: str,
    category: str,
    description: str,
    assessment: Assessment,
    source: AssessmentSource,
) -> EmergencyReport:
    report = EmergencyReport(
        location=location,
        category=category,
        description=description,
        assessment=assessment,
        assessment_source=source,
    )
    st.session_state.reports.insert(0, report)
    return report


def render_new_assessment(report: EmergencyReport) -> None:
    st.success(f"Report added to Operations · {report.assessment_source}")
    st.markdown(
        f"**{report.assessment_source} assessment · urgency {report.assessment.severity_score}/5**"
    )
    st.caption(report.assessment.urgency_rationale)
    for index, step in enumerate(report.assessment.action_steps, start=1):
        st.text(f"{index}. {step}")


def request_assistance(
    report: EmergencyReport,
    target_language: str,
    use_local_rules: bool = False,
) -> None:
    state_key = f"{report.id}:{target_language}"
    comparison_reports = [
        item for item in st.session_state.reports if item.id != report.id
    ]
    try:
        if use_local_rules:
            result = local_suggestions(report, comparison_reports)
        else:
            result = analyze_with_gemini(
                report,
                comparison_reports,
                target_language,
            )
    except OperationsAssistError as exc:
        st.session_state.assistance_errors[state_key] = str(exc)
    else:
        st.session_state.assistance_results[state_key] = result
        st.session_state.assistance_errors.pop(state_key, None)


def render_assistance(
    result: OperationsAssistance,
    reports_by_id: dict[str, EmergencyReport],
) -> None:
    source_label = (
        "Gemini AI suggestions · verify before acting"
        if result.source == "Gemini"
        else "Local rules · not AI"
    )
    st.markdown(f"**{source_label}**")

    if result.translated_description:
        st.markdown(
            f"**Translation to {result.target_language} · "
            f"{result.detected_language} detected**"
        )
        st.text(result.translated_description)
    else:
        st.info("Translation is available with Gemini; local rules do not translate text.")

    st.markdown("**Possible duplicate reports · verify manually**")
    if result.duplicate_matches:
        for match in result.duplicate_matches:
            candidate = reports_by_id.get(match.report_id)
            if candidate is None:
                continue
            st.text(
                f"{candidate.category} · {candidate.location} · {candidate.status} · "
                f"{match.similarity_score}% similarity signal — {match.rationale}"
            )
    else:
        st.caption("No possible duplicates were suggested.")

    for label, suggestions, catalog in (
        (
            "Sample volunteer suggestions · not assigned",
            result.volunteer_suggestions,
            SAMPLE_VOLUNTEERS,
        ),
        (
            "Sample supply suggestions · not confirmed inventory",
            result.supply_suggestions,
            SAMPLE_SUPPLIES,
        ),
    ):
        st.markdown(f"**{label}**")
        if not suggestions:
            st.caption("No matching sample options were suggested.")
            continue
        candidates_by_id = {candidate.id: candidate for candidate in catalog}
        for suggestion in suggestions:
            candidate = candidates_by_id.get(suggestion.candidate_id)
            if candidate is not None:
                st.text(f"{candidate.name} — {suggestion.rationale}")


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
      <div class="feature-pills">
        <span class="feature-pill">🌐 Report translation</span>
        <span class="feature-pill">🔎 Possible duplicates</span>
        <span class="feature-pill">🤝 Sample resource suggestions</span>
      </div>
    </div>
    <div class="notice"><strong>Safety:</strong> This demo is not an emergency service.
    AI assessments and local rule estimates are informational only, not validated triage
    or dispatch. If someone is in immediate danger, contact local emergency services.</div>
    """,
    unsafe_allow_html=True,
)

report_tab, operations_tab = st.tabs(["＋  Submit a report", "▤  Operations"])

with report_tab:
    st.subheader("Tell us what is happening")
    st.caption("Share the essentials so the response team can assess the need.")
    if key_configured:
        st.caption("Gemini is configured for live AI assessments.")
    else:
        st.info(
            "No Gemini key configured. Submissions use transparent local rules, "
            "labeled non-AI. The keyword rules can miss or misread context and are not "
            "validated triage; no key is needed to try the form."
        )
    with st.form("emergency_report", clear_on_submit=False):
        location = st.text_input(
            "Location",
            placeholder="Neighborhood, landmark, or address",
            max_chars=160,
            key="report_location",
        )
        category = st.selectbox(
            "What is needed?",
            ["Medical", "Food", "Water", "Shelter"],
            key="report_category",
        )
        description = st.text_area(
            "Describe the emergency",
            placeholder="What happened, who needs help, and what support is needed?",
            max_chars=1200,
            height=130,
            key="report_description",
        )
        submitted = st.form_submit_button(
            "Assess report with Gemini" if key_configured else "Assess with local rules",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        st.session_state.pending_report = None
        st.session_state.pending_gemini_error = ""
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
        elif not key_configured:
            report = save_report(
                location=location.strip(),
                category=category,
                description=description.strip(),
                assessment=assess_with_local_rules(category, description.strip()),
                source="Local rules",
            )
            render_new_assessment(report)
        else:
            try:
                with st.spinner("Gemini is reviewing the report…"):
                    assessment = assess_report(
                        location=location.strip(),
                        category=category,
                        description=description.strip(),
                    )
            except GeminiAssessmentError as exc:
                st.session_state.pending_report = {
                    "location": location.strip(),
                    "category": category,
                    "description": description.strip(),
                }
                st.session_state.pending_gemini_error = str(exc)
            else:
                report = save_report(
                    location=location.strip(),
                    category=category,
                    description=description.strip(),
                    assessment=assessment,
                    source="Gemini",
                )
                render_new_assessment(report)

    if st.session_state.pending_report:
        pending = st.session_state.pending_report
        retry_column, local_column = st.columns(2)
        with retry_column:
            if st.button("Retry Gemini assessment", use_container_width=True):
                try:
                    with st.spinner("Retrying Gemini assessment…"):
                        assessment = assess_report(**pending)
                except GeminiAssessmentError as exc:
                    st.session_state.pending_gemini_error = str(exc)
                else:
                    report = save_report(
                        **pending,
                        assessment=assessment,
                        source="Gemini",
                    )
                    st.session_state.pending_report = None
                    st.session_state.pending_gemini_error = ""
                    render_new_assessment(report)
        with local_column:
            if st.button("Use local rules instead", use_container_width=True):
                report = save_report(
                    **pending,
                    assessment=assess_with_local_rules(
                        pending["category"],
                        pending["description"],
                    ),
                    source="Local rules",
                )
                st.session_state.pending_report = None
                st.session_state.pending_gemini_error = ""
                render_new_assessment(report)
        if st.session_state.pending_report:
            st.error(st.session_state.pending_gemini_error)

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
            source_class, assessment_label, rationale_label, steps_label = {
                "Gemini": (
                    "source-gemini",
                    "Gemini assessment",
                    "AI urgency rationale",
                    "Recommended coordination steps",
                ),
                "Local rules": (
                    "source-local",
                    "Local rules · not AI",
                    "Local rule explanation · not AI",
                    "Local rule-based coordination steps · not AI",
                ),
                "Demo example": (
                    "source-demo",
                    "Demo example · not Gemini",
                    "Illustrative example rationale · not AI",
                    "Example coordination steps · not AI",
                ),
            }[report.assessment_source]

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
                with st.expander("Coordination helpers · translation, duplicates, matches"):
                    target_language = st.selectbox(
                        "Translate report to",
                        TARGET_LANGUAGES,
                        key=f"target_language_{report.id}",
                    )
                    assistance_key = f"{report.id}:{target_language}"
                    st.caption(
                        "On request, Gemini receives this report and up to 8 other "
                        "current-session reports for comparison. Suggestions are not "
                        "verified and never dispatch or assign anyone."
                    )
                    action_label = (
                        "Run Gemini coordination helpers"
                        if key_configured
                        else "Get local suggestions · not AI"
                    )
                    if st.button(
                        action_label,
                        key=f"assist_{report.id}",
                        use_container_width=True,
                    ):
                        request_assistance(
                            report,
                            target_language,
                            use_local_rules=not key_configured,
                        )
                    if assistance_key in st.session_state.assistance_errors:
                        st.error(st.session_state.assistance_errors[assistance_key])
                        retry_column, local_column = st.columns(2)
                        with retry_column:
                            if st.button(
                                "Retry Gemini helpers",
                                key=f"retry_assist_{report.id}",
                                use_container_width=True,
                            ):
                                request_assistance(report, target_language)
                        with local_column:
                            if st.button(
                                "Use local suggestions instead",
                                key=f"local_assist_{report.id}",
                                use_container_width=True,
                            ):
                                request_assistance(
                                    report,
                                    target_language,
                                    use_local_rules=True,
                                )
                    result = st.session_state.assistance_results.get(assistance_key)
                    if result is not None:
                        render_assistance(
                            result,
                            {item.id: item for item in st.session_state.reports},
                        )

    with volunteer_column:
        st.markdown("#### Volunteer status")
        st.caption("Illustrative sample data only · not connected to real volunteers")
        for volunteer in SAMPLE_VOLUNTEERS:
            st.markdown(
                f"""
                <div class="volunteer-card">
                  <strong>{escape(volunteer.name)}</strong><br>
                  <span class="muted-note">Sample status · availability unverified; not assigned</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
