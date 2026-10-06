from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class ContextScore:
    semantic_score: float
    category_match: float
    subcategory_match: float
    location_match: float
    service_cycle_match: float
    final_score: float
    location_conflict: bool


class ContextAwareScorer:
    """
    Combines semantic similarity with structured incident context.

    Location is treated as contextual evidence, NOT as a hard
    contradiction.

    A different location can indicate that two incidents are
    distinct, but it can also indicate a common underlying event
    such as a building-wide power or network outage.

    Final duplicate decisions therefore remain subject to the
    human-in-the-loop policy.

    This component does NOT:
        - merge incidents
        - delete incidents
        - determine responsibility
        - assign departments
        - change incident priority
    """

    SEMANTIC_WEIGHT = 0.70
    CATEGORY_WEIGHT = 0.10
    SUBCATEGORY_WEIGHT = 0.10
    SERVICE_CYCLE_WEIGHT = 0.10

    def score(
        self,
        query_incident: Dict[str, Any],
        candidate_incident: Dict[str, Any],
        semantic_score: float,
    ) -> ContextScore:

        if not 0.0 <= semantic_score <= 1.0:
            raise ValueError(
                "semantic_score must be between 0 and 1"
            )

        category_match = self._match(
            query_incident,
            candidate_incident,
            "category",
        )

        subcategory_match = self._match(
            query_incident,
            candidate_incident,
            "subcategory",
        )

        location_match = self._match(
            query_incident,
            candidate_incident,
            "location",
        )

        service_cycle_match = self._match(
            query_incident,
            candidate_incident,
            "service_cycle_id",
        )

        location_conflict = self._location_conflict(
            query_incident,
            candidate_incident,
        )

        final_score = (
            self.SEMANTIC_WEIGHT * semantic_score
            + self.CATEGORY_WEIGHT * category_match
            + self.SUBCATEGORY_WEIGHT * subcategory_match
            + self.SERVICE_CYCLE_WEIGHT * service_cycle_match
        )

        return ContextScore(
            semantic_score=semantic_score,
            category_match=category_match,
            subcategory_match=subcategory_match,
            location_match=location_match,
            service_cycle_match=service_cycle_match,
            final_score=final_score,
            location_conflict=location_conflict,
        )

    @staticmethod
    def _normalize(value: Any) -> str:
        return str(value or "").strip().lower()

    @classmethod
    def _match(
        cls,
        query_incident: Dict[str, Any],
        candidate_incident: Dict[str, Any],
        field: str,
    ) -> float:

        query_value = cls._normalize(
            query_incident.get(field)
        )

        candidate_value = cls._normalize(
            candidate_incident.get(field)
        )

        if not query_value or not candidate_value:
            return 0.0

        return 1.0 if query_value == candidate_value else 0.0

    @classmethod
    def _location_conflict(
        cls,
        query_incident: Dict[str, Any],
        candidate_incident: Dict[str, Any],
    ) -> bool:

        query_location = cls._normalize(
            query_incident.get("location")
        )

        candidate_location = cls._normalize(
            candidate_incident.get("location")
        )

        # Unknown location is not considered a conflict.
        if not query_location or not candidate_location:
            return False

        return query_location != candidate_location