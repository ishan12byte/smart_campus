WEIGHTS = {
    "impact": 0.30,
    "urgency": 0.25,
    "safety": 0.25,
    "deadline": 0.10,
    "recurrence": 0.10,
}

EMERGENCY_TYPES = {
    "FIRE",
    "MEDICAL_EMERGENCY",
    "IMMEDIATE_SECURITY_THREAT",
    "MAJOR_ELECTRICAL_HAZARD",
    "CRITICAL_CYBER_INCIDENT",
}

def validate_score(value: int, name: str) -> None:
    if not isinstance(value, int):
        raise TypeError(f"{name} must be an integer.")

    if value < 1 or value > 5:
        raise ValueError(f"{name} must be between 1 and 5.")

def get_priority_level(score: float) -> str:
    if score >= 4.0:
        return "CRITICAL"
    elif score >= 3.0:
        return "HIGH"
    elif score >= 2.0:
        return "MEDIUM"
    else:
        return "LOW"

def is_emergency(incident_type: str | None) -> bool:
    if incident_type is None:
        return False

    return incident_type.upper() in EMERGENCY_TYPES

def calculate_priority(
    impact: int,
    urgency: int,
    safety: int,
    deadline: int,
    recurrence: int,
    incident_type: str | None = None,
) -> dict:

    validate_score(impact, "impact")
    validate_score(urgency, "urgency")
    validate_score(safety, "safety")
    validate_score(deadline, "deadline")
    validate_score(recurrence, "recurrence")

    if is_emergency(incident_type):
        return {
            "score": 5.0,
            "level": "CRITICAL",
            "reason": "Emergency incident override",
        }

    score = (
        impact * WEIGHTS["impact"]
        + urgency * WEIGHTS["urgency"]
        + safety * WEIGHTS["safety"]
        + deadline * WEIGHTS["deadline"]
        + recurrence * WEIGHTS["recurrence"]
    )

    score = round(score, 2)
    level = get_priority_level(score)

    return {
        "score": score,
        "level": level,
	"factors": {
		"impact":impact,
		"urgency":urgency,
		"safety":safety,
		"dealine":deadline,
		"recurrence":recurrence,
	},
        "reason": (
            "Calculated using impact, urgency, safety, "
            "deadline, and recurrence."
        ),
    }
