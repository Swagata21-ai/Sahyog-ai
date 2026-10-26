import logging
import os

from dotenv import load_dotenv
from google import genai
from google.genai import errors
import httpx
from pydantic import ValidationError

from sahyog_ai.models import Assessment

logger = logging.getLogger(__name__)


class GeminiAssessmentError(Exception):
    """Raised when Gemini cannot return a usable report assessment."""


def parse_assessment(response_text: str) -> Assessment:
    try:
        return Assessment.model_validate_json(response_text)
    except ValidationError as exc:
        raise GeminiAssessmentError(
            "Gemini returned an assessment that could not be validated. Please retry."
        ) from exc


def assess_report(location: str, category: str, description: str) -> Assessment:
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise GeminiAssessmentError(
            "Gemini is not configured yet. Add your API key to a local .env file "
            "(see .env.example), then retry. No report was saved."
        )

    model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()
    prompt = (
        "Assess the urgency of this community emergency report for coordination support. "
        "Return a severity score from 1 (lower urgency) to 5 (highest urgency), a short "
        "rationale grounded only in the report, and 1 to 5 practical coordination steps. "
        "Do not diagnose, promise rescue, or claim that anyone has been dispatched. "
        "This is informational prioritization support, not official emergency response.\n\n"
        f"Location: {location}\nCategory: {category}\nReport: {description}"
    )

    try:
        client = genai.Client(api_key=api_key)
        response = client.interactions.create(
            model=model,
            input=prompt,
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": Assessment.model_json_schema(),
            },
        )
    except (errors.APIError, httpx.HTTPError) as exc:
        logger.exception("Gemini API request failed")
        raise GeminiAssessmentError(
            "Gemini could not assess this report. Check your connection and API "
            "access, then retry. No report was saved."
        ) from exc

    response_text = response.output_text
    if not response_text:
        raise GeminiAssessmentError(
            "Gemini returned no assessment. Please retry. No report was saved."
        )
    return parse_assessment(response_text)
