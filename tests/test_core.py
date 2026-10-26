import os
import unittest
from unittest.mock import patch

from pydantic import ValidationError

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


if __name__ == "__main__":
    unittest.main()
