from datetime import datetime, timezone
from typing import Annotated, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

AssessmentSource = Literal["Gemini", "Local rules", "Demo example"]


ActionStep = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=240),
]


class Assessment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    severity_score: int = Field(ge=1, le=5)
    urgency_rationale: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=280),
    ]
    action_steps: list[ActionStep] = Field(min_length=1, max_length=5)


class EmergencyReport(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    location: str
    category: Literal["Medical", "Food", "Water", "Shelter"]
    description: str
    assessment: Assessment
    assessment_source: AssessmentSource = "Gemini"
    status: Literal["Active", "Resolved"] = "Active"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DuplicateSuggestion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    report_id: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=80),
    ]
    similarity_score: int = Field(ge=0, le=100)
    rationale: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=200),
    ]


class ResourceSuggestion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidate_id: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=80),
    ]
    rationale: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=200),
    ]


class OperationsAssistancePayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    detected_language: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=80),
    ]
    translated_description: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=2400),
    ]
    duplicate_matches: list[DuplicateSuggestion] = Field(max_length=3)
    volunteer_suggestions: list[ResourceSuggestion] = Field(max_length=3)
    supply_suggestions: list[ResourceSuggestion] = Field(max_length=3)


class OperationsAssistance(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: Literal["Gemini", "Local rules"]
    target_language: str | None = None
    detected_language: str | None = None
    translated_description: str | None = None
    duplicate_matches: list[DuplicateSuggestion] = Field(default_factory=list)
    volunteer_suggestions: list[ResourceSuggestion] = Field(default_factory=list)
    supply_suggestions: list[ResourceSuggestion] = Field(default_factory=list)
