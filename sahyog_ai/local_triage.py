from sahyog_ai.models import Assessment

CATEGORY_BASELINES = {
    "Medical": 3,
    "Food": 1,
    "Water": 2,
    "Shelter": 2,
}

HIGH_PRIORITY_CUES = (
    "unconscious",
    "not breathing",
    "cannot breathe",
    "can't breathe",
    "trapped",
    "severe bleeding",
    "fire",
    "collapse",
    "rising floodwater",
)

ELEVATED_CUES = (
    "injured",
    "flood",
    "no clean water",
    "without food",
    "no food",
    "power outage",
    "elderly",
    "child",
    "infant",
    "pregnant",
    "evacuation",
)

CATEGORY_STEPS = {
    "Medical": (
        "For medical needs, contact qualified medical responders; this estimate is not medical advice.",
    ),
    "Food": (
        "Confirm the number of people and dietary needs with a relief coordinator.",
    ),
    "Water": (
        "Verify water safety and distribution through a trusted local relief group.",
    ),
    "Shelter": (
        "Confirm safe shelter arrangements through a trusted local relief organization.",
    ),
}


def assess_with_local_rules(category: str, description: str) -> Assessment:
    baseline = CATEGORY_BASELINES[category]
    text = description.casefold()
    high_matches = [cue for cue in HIGH_PRIORITY_CUES if cue in text]
    elevated_matches = [cue for cue in ELEVATED_CUES if cue in text]

    if high_matches:
        score = 5
        rule_explanation = (
            "High-priority keyword rule matched: "
            + ", ".join(high_matches)
            + f" (category baseline {baseline}/5, score set to 5)."
        )
    elif elevated_matches:
        increase = 2 if len(elevated_matches) > 1 else 1
        score = min(5, baseline + increase)
        rule_explanation = (
            "Keyword rule matched: "
            + ", ".join(elevated_matches)
            + f" (category baseline {baseline}/5, adjusted by +{increase})."
        )
    else:
        score = baseline
        rule_explanation = (
            f"No configured keyword matched; category baseline is {baseline}/5."
        )

    return Assessment(
        severity_score=score,
        urgency_rationale=(
            "Local rules only — not AI or validated emergency triage. "
            + rule_explanation
        ),
        action_steps=[
            "Confirm the report details and current needs with the reporter or a trusted local coordinator.",
            "For immediate danger, contact local emergency services; do not wait for this estimate.",
            *CATEGORY_STEPS[category],
        ],
    )
