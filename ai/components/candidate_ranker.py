from dataclasses import dataclass
from typing import Any, Dict, Iterable, List

from ai.components.context_scorer import (
    ContextAwareScorer,
)
from ai.components.embedding_matcher import (
    EmbeddingIncidentMatcher,
)
from ai.components.semantic_decision import (
    SemanticDecisionEngine,
)


@dataclass(frozen=True)
class RankedCandidate:
    """
    A ranked historical incident candidate.

    Both semantic and context-aware scores are retained so that
    the recommendation remains explainable.
    """

    incident_id: str
    semantic_score: float
    context_score: float
    category_match: float
    subcategory_match: float
    location_match: float
    service_cycle_match: float
    location_conflict: bool
    decision: str
    reason: str


class SemanticCandidateRanker:
    """
    Finds and ranks historical incidents using semantic similarity
    plus structured incident context.

    The ranker does NOT:
        - merge incidents
        - delete incidents
        - assign responsibility
        - determine department fault
        - change incident priority
        - automatically close incidents

    High similarity across different locations is deliberately
    routed to human review rather than automatically classified
    as a duplicate.
    """

    def __init__(
        self,
        matcher=None,
        decision_engine=None,
        context_scorer=None,
        top_k: int = 5,
    ):

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than zero"
            )

        self.matcher = (
            matcher
            or EmbeddingIncidentMatcher(
                threshold=0.0
            )
        )

        self.decision_engine = (
            decision_engine
            or SemanticDecisionEngine(
                review_threshold=0.40,
                duplicate_threshold=0.50,
            )
        )

        self.context_scorer = (
            context_scorer
            or ContextAwareScorer()
        )

        self.top_k = top_k

    def rank(
        self,
        query_incident: Dict[str, Any],
        historical_incidents: Iterable[Dict[str, Any]],
    ) -> List[RankedCandidate]:

        if not isinstance(query_incident, dict):
            raise ValueError(
                "query_incident must be a dictionary"
            )

        if not query_incident.get("incident_id"):
            raise ValueError(
                "query_incident must contain incident_id"
            )

        if not query_incident.get("description"):
            raise ValueError(
                "query_incident must contain description"
            )

        if historical_incidents is None:
            raise ValueError(
                "historical_incidents cannot be None"
            )

        query_id = query_incident["incident_id"]

        candidates = list(historical_incidents)

        # Never compare an incident with itself.
        candidates = [
            incident
            for incident in candidates
            if incident.get("incident_id") != query_id
        ]

        if not candidates:
            return []

        result = self.matcher.predict(
            {
                "query_incident": query_incident,
                "candidate_incidents": candidates,
            }
        )

        candidate_by_id = {
            incident["incident_id"]: incident
            for incident in candidates
        }

        ranked = []

        for candidate in result.candidates:

            incident_id = candidate.incident_id
            semantic_score = float(candidate.score)

            candidate_incident = candidate_by_id.get(
                incident_id
            )

            if candidate_incident is None:
                continue

            context = self.context_scorer.score(
                query_incident,
                candidate_incident,
                semantic_score,
            )

            decision = self.decision_engine.decide(
                context.final_score
            )

            # Different known locations + otherwise strong
            # similarity should require human review.
            if (
                context.location_conflict
                and decision.decision
                == SemanticDecisionEngine.LIKELY_DUPLICATE
            ):
                decision = type(decision)(
                    decision=SemanticDecisionEngine.REVIEW,
                    score=context.final_score,
                    reason=(
                        "High semantic/context similarity was "
                        "detected, but the incidents occur at "
                        "different known locations. Human review "
                        "is required to determine whether they "
                        "represent the same underlying event."
                    ),
                )

            ranked.append(
                RankedCandidate(
                    incident_id=incident_id,
                    semantic_score=semantic_score,
                    context_score=context.final_score,
                    category_match=context.category_match,
                    subcategory_match=context.subcategory_match,
                    location_match=context.location_match,
                    service_cycle_match=context.service_cycle_match,
                    location_conflict=context.location_conflict,
                    decision=decision.decision,
                    reason=decision.reason,
                )
            )

        # Rank using the context-aware score.
        ranked.sort(
            key=lambda candidate: candidate.context_score,
            reverse=True,
        )

        return ranked[: self.top_k]