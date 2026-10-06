from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from ai.components.embedding_matcher import EmbeddingIncidentMatcher
from ai.components.context_scorer import ContextAwareScorer


NO_RECURRENCE = "NO_RECURRENCE"
RECURRENCE_DETECTED = "RECURRENCE_DETECTED"
REVIEW_RECURRING_PATTERN = "REVIEW_RECURRING_PATTERN"


@dataclass(frozen=True)
class RecurringCandidate:
    incident_id: str
    semantic_score: float
    context_score: float
    location_conflict: bool
    category_match: bool
    subcategory_match: bool
    service_cycle_match: bool


@dataclass(frozen=True)
class SemanticRecurrenceResult:
    incident_id: str
    status: str
    occurrence_count: int
    matching_incident_ids: Tuple[str, ...]
    candidates: Tuple[RecurringCandidate, ...]
    reason: str


class SemanticRecurrenceAnalyzer:
    """
    Detect recurring incident patterns using semantic similarity
    combined with operational context.

    Category is treated as a hard compatibility constraint.

    Location is intentionally NOT a hard constraint because the
    same underlying event can affect multiple rooms or areas.

    This component only produces an intelligence signal.
    It does not modify priority, responsibility, assignment,
    escalation, or incident records.
    """

    def __init__(
        self,
        matcher: Optional[EmbeddingIncidentMatcher] = None,
        context_scorer: Optional[ContextAwareScorer] = None,
        semantic_threshold: float = 0.50,
        recurrence_threshold: float = 0.55,
        minimum_occurrences: int = 3,
        top_k: int = 10,
    ):
        if not 0.0 <= semantic_threshold <= 1.0:
            raise ValueError(
                "semantic_threshold must be between 0 and 1"
            )

        if not 0.0 <= recurrence_threshold <= 1.0:
            raise ValueError(
                "recurrence_threshold must be between 0 and 1"
            )

        if minimum_occurrences < 2:
            raise ValueError(
                "minimum_occurrences must be at least 2"
            )

        if top_k < 1:
            raise ValueError(
                "top_k must be at least 1"
            )

        self.matcher = matcher or EmbeddingIncidentMatcher(
            threshold=semantic_threshold
        )

        self.context_scorer = (
            context_scorer or ContextAwareScorer()
        )

        self.semantic_threshold = semantic_threshold
        self.recurrence_threshold = recurrence_threshold
        self.minimum_occurrences = minimum_occurrences
        self.top_k = top_k

    @staticmethod
    def _normalize(value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        value = str(value).strip()

        return value.upper() if value else None

    @staticmethod
    def _parse_time(value):
        if not value:
            return None

        try:
            from datetime import datetime

            return datetime.fromisoformat(
                str(value).replace("Z", "+00:00")
            )

        except ValueError:
            return None

    def _within_time_window(
        self,
        query: Dict[str, str],
        candidate: Dict[str, str],
        time_window_days: Optional[int],
    ) -> bool:

        if time_window_days is None:
            return True

        query_time = self._parse_time(
            query.get("reported_at")
        )

        candidate_time = self._parse_time(
            candidate.get("reported_at")
        )

        if query_time is None or candidate_time is None:
            return True

        delta_days = abs(
            (query_time - candidate_time).total_seconds()
        ) / 86400

        return delta_days <= time_window_days

    def _category_compatible(
        self,
        query: Dict[str, str],
        candidate: Dict[str, str],
    ) -> bool:

        query_category = self._normalize(
            query.get("category")
        )

        candidate_category = self._normalize(
            candidate.get("category")
        )

        # If either category is missing, do not invent a mismatch.
        if not query_category or not candidate_category:
            return True

        return query_category == candidate_category

    def analyze(
        self,
        query_incident: Dict[str, str],
        historical_incidents: List[Dict[str, str]],
        time_window_days: Optional[int] = 30,
    ) -> SemanticRecurrenceResult:

        if not query_incident:
            raise ValueError(
                "query_incident is required"
            )

        incident_id = query_incident.get("incident_id")

        if not incident_id:
            raise ValueError(
                "query_incident must contain incident_id"
            )

        if historical_incidents is None:
            raise ValueError(
                "historical_incidents is required"
            )

        if (
            time_window_days is not None
            and time_window_days <= 0
        ):
            raise ValueError(
                "time_window_days must be positive or None"
            )

        matcher_result = self.matcher.predict(
            {
                "query_incident": query_incident,
                "candidate_incidents": historical_incidents,
            }
        )

        candidate_scores = {
            candidate.incident_id: candidate.score
            for candidate in matcher_result.candidates
        }

        incident_lookup = {
            incident.get("incident_id"): incident
            for incident in historical_incidents
            if incident.get("incident_id")
        }

        recurring_candidates = []

        for candidate_id, semantic_score in candidate_scores.items():

            if candidate_id == incident_id:
                continue

            candidate = incident_lookup.get(candidate_id)

            if candidate is None:
                continue

            # Category is a hard compatibility constraint.
            if not self._category_compatible(
                query_incident,
                candidate,
            ):
                continue

            if not self._within_time_window(
                query_incident,
                candidate,
                time_window_days,
            ):
                continue

            context = self.context_scorer.score(
                query_incident,
                candidate,
                semantic_score,
            )

            if context.final_score < self.recurrence_threshold:
                continue

            recurring_candidates.append(
                RecurringCandidate(
                    incident_id=candidate_id,
                    semantic_score=semantic_score,
                    context_score=context.final_score,
                    location_conflict=context.location_conflict,
                    category_match=bool(
                        context.category_match
                    ),
                    subcategory_match=bool(
                        context.subcategory_match
                    ),
                    service_cycle_match=bool(
                        context.service_cycle_match
                    ),
                )
            )

        recurring_candidates.sort(
            key=lambda candidate: candidate.context_score,
            reverse=True,
        )

        recurring_candidates = recurring_candidates[
            : self.top_k
        ]

        occurrence_count = (
            len(recurring_candidates) + 1
        )

        matching_ids = tuple(
            candidate.incident_id
            for candidate in recurring_candidates
        )

        if occurrence_count < self.minimum_occurrences:
            return SemanticRecurrenceResult(
                incident_id=incident_id,
                status=NO_RECURRENCE,
                occurrence_count=occurrence_count,
                matching_incident_ids=matching_ids,
                candidates=tuple(recurring_candidates),
                reason=(
                    "Insufficient semantically and contextually "
                    "similar incidents to establish recurrence."
                ),
            )

        has_location_conflict = any(
            candidate.location_conflict
            for candidate in recurring_candidates
        )

        if has_location_conflict:
            return SemanticRecurrenceResult(
                incident_id=incident_id,
                status=REVIEW_RECURRING_PATTERN,
                occurrence_count=occurrence_count,
                matching_incident_ids=matching_ids,
                candidates=tuple(recurring_candidates),
                reason=(
                    "A recurring semantic pattern was detected, "
                    "but at least one strong candidate occurs at "
                    "a different known location. Human review is "
                    "required to determine whether the incidents "
                    "represent one underlying event or separate "
                    "recurring issues."
                ),
            )

        return SemanticRecurrenceResult(
            incident_id=incident_id,
            status=RECURRENCE_DETECTED,
            occurrence_count=occurrence_count,
            matching_incident_ids=matching_ids,
            candidates=tuple(recurring_candidates),
            reason=(
                f"Recurring semantic pattern detected across "
                f"{occurrence_count} incidents within the "
                f"configured time window."
            ),
        )