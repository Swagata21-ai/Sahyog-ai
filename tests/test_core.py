import os
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import httpx
from pydantic import ValidationError
from streamlit.testing.v1 import AppTest

from sahyog_ai.gemini import GeminiAssessmentError, assess_report, parse_assessment
from sahyog_ai.models import Assessment, EmergencyReport


class AssessmentTests(unittest.TestCase):
    def test_valid_assessment_can_be_parsed(self):
        assessment = parse_assessment(
            '{"severity_score": 4, "urgency_rationale": "Unsafe flooding reported.", '
            '"action_steps": ["Contact local responders."]}'
        )

        self.assertEqual(assessment.severity_score, 4)
        self.assertEqual(assessment.action_steps, ["Contact local responders."])

    def test_out_of_range_score_is_rejected(self):
        with self.assertRaises(GeminiAssessmentError):
            parse_assessment(
                '{"severity_score": 6, "urgency_rationale": "Urgent.", '
                '"action_steps": ["Contact responders."]}'
            )

    def test_empty_action_steps_are_rejected(self):
        with self.assertRaises(ValidationError):
            Assessment(
                severity_score=2,
                urgency_rationale="A rationale.",
                action_steps=[],
            )

    def test_blank_action_step_is_rejected(self):
        with self.assertRaises(ValidationError):
            Assessment(
                severity_score=2,
                urgency_rationale="A rationale.",
                action_steps=["   "],
            )

    def test_report_starts_active(self):
        report = EmergencyReport(
            location="North Block",
            category="Water",
            description="Water supply is interrupted.",
            assessment=Assessment(
                severity_score=2,
                urgency_rationale="Supply interruption reported.",
                action_steps=["Confirm the affected area."],
            ),
        )

        self.assertEqual(report.status, "Active")

    def test_missing_api_key_does_not_create_an_assessment(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": ""}):
            with self.assertRaisesRegex(GeminiAssessmentError, "No report was saved"):
                assess_report("North Block", "Water", "Water supply is interrupted.")

    def test_gemini_request_uses_structured_assessment_schema(self):
        client = Mock()
        client.interactions.create.return_value = SimpleNamespace(
            output_text=(
                '{"severity_score": 3, "urgency_rationale": "Flooding reported.", '
                '"action_steps": ["Contact local responders."]}'
            )
        )
        with (
            patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}),
            patch("sahyog_ai.gemini.genai.Client", return_value=client),
        ):
            assessment = assess_report(
                "North Block",
                "Water",
                "Floodwater is entering several homes.",
            )

        self.assertEqual(assessment.severity_score, 3)
        request = client.interactions.create.call_args.kwargs
        self.assertEqual(request["model"], "gemini-3.8-flash")
        self.assertEqual(
            request["response_format"]["schema"],
            Assessment.model_json_schema(),
        )

    def test_gemini_connection_failure_is_reported_for_retry(self):
        client = Mock()
        client.interactions.create.side_effect = httpx.ConnectError("offline")
        with (
            patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}),
            patch("sahyog_ai.gemini.genai.Client", return_value=client),
        ):
            with self.assertRaisesRegex(GeminiAssessmentError, "No report was saved"):
                assess_report("North Block", "Water", "Water supply is interrupted.")

    def test_operations_dashboard_can_resolve_and_reopen_reports(self):
        report = EmergencyReport(
            location="North Block",
            category="Water",
            description="Floodwater is entering several homes.",
            assessment=Assessment(
                severity_score=4,
                urgency_rationale="Flooding is reported in homes.",
                action_steps=["Contact local responders."],
            ),
        )
        app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py")
        app.session_state["reports"] = [report]
        app.run()

        self.assertFalse(app.exception)
        next(button for button in app.button if button.label == "Mark resolved").click().run()
        self.assertEqual(app.session_state["reports"][0].status, "Resolved")

        next(button for button in app.button if button.label == "Reopen report").click().run()
        self.assertEqual(app.session_state["reports"][0].status, "Active")

    def test_no_key_demo_loads_and_clears_labeled_sample_reports(self):
        app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py")
        app.run()

        next(button for button in app.button if button.label == "Load sample reports").click().run()
        reports = app.session_state["reports"]
        self.assertEqual(len(reports), 3)
        self.assertTrue(all(report.assessment_source == "Demo example" for report in reports))
        self.assertTrue(
            any("Demo example · not Gemini" in element.value for element in app.markdown)
        )

        next(button for button in app.button if button.label == "Clear sample reports").click().run()
        self.assertEqual(app.session_state["reports"], [])


if __name__ == "__main__":
    unittest.main()
