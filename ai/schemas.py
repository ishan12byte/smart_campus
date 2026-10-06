from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AICandidate:
    """
    A candidate produced by an AI component.

    The candidate is only a recommendation.
    It does not automatically change incident state.
    """

    incident_id: int
    score: float
    reason: str = ""


@dataclass(frozen=True)
class AIRecommendation:
    """
    Generic AI recommendation.

    AI components should return structured recommendations
    rather than directly modifying Decision Engine state.
    """

    recommendation_type: str
    confidence: float
    reason: str = ""
    evidence: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AIResult:
    """
    Standard output from the AI layer.
    """

    candidates: tuple[AICandidate, ...] = ()
    recommendations: tuple[AIRecommendation, ...] = ()
    model_name: str | None = None
    model_version: str | None = None
    fallback_used: bool = False