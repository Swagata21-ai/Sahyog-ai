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
