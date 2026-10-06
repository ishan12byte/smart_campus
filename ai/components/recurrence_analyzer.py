from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional


NO_RECURRENCE = "NO_RECURRENCE"
RECURRENCE_DETECTED = "RECURRENCE_DETECTED"


@dataclass(frozen=True)
class RecurrenceResult:
    incident_id: str
    status: str
    occurrence_count: int
    matching_incident_ids: tuple
    category: Optional[str]
    subcategory: Optional[str]
    location: Optional[str]
    service_cycle_id: Optional[str]
    time_window_days: Optional[int]
    reason: str


class RecurrenceAnalyzer:
    """
    Detects recurring operational patterns in historical incidents.

    Recurrence is an intelligence signal only. It does not modify
    priority, responsibility, assignment, or escalation.
    """

    def __init__(
        self,
        minimum_occurrences: int = 3,
        time_window_days: Optional[int] = 30,
    ):
        if minimum_occurrences < 2:
            raise ValueError(
                "minimum_occurrences must be at least 2"
            )

        if time_window_days is not None and time_window_days <= 0:
            raise ValueError(
                "time_window_days must be positive or None"
            )

        self.minimum_occurrences = minimum_occurrences
        self.time_window_days = time_window_days

    @staticmethod
    def _normalize(value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        value = str(value).strip()

        return value.upper() if value else None

    @staticmethod
    def _parse_datetime(
        value: Optional[str],
    ) -> Optional[datetime]:
        if not value:
            return None

        try:
            return datetime.fromisoformat(
                value.replace("Z", "+00:00")
            )
        except ValueError:
            return None

    def _same_pattern(
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

        if (
            query_category
            and candidate_category
            and query_category != candidate_category
        ):
            return False

        query_subcategory = self._normalize(
            query.get("subcategory")
        )
        candidate_subcategory = self._normalize(
            candidate.get("subcategory")
        )

        if (
            query_subcategory
            and candidate_subcategory
            and query_subcategory != candidate_subcategory
        ):
            return False

        query_location = self._normalize(
            query.get("location")
        )
        candidate_location = self._normalize(
            candidate.get("location")
        )

        if (
            query_location
            and candidate_location
            and query_location != candidate_location
        ):
            return False

        query_service_cycle = self._normalize(
            query.get("service_cycle_id")
        )
        candidate_service_cycle = self._normalize(
            candidate.get("service_cycle_id")
        )

        if (
            query_service_cycle
            and candidate_service_cycle
            and query_service_cycle != candidate_service_cycle
        ):
            return False

        return True

    def analyze(
        self,
        query_incident: Dict[str, str],
        historical_incidents: List[Dict[str, str]],
    ) -> RecurrenceResult:

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

        matches = []

        query_time = self._parse_datetime(
            query_incident.get("reported_at")
        )

        for incident in historical_incidents:

            candidate_id = incident.get("incident_id")

            if not candidate_id:
                continue

            if candidate_id == incident_id:
                continue

            if not self._same_pattern(
                query_incident,
                incident,
            ):
                continue

            if self.time_window_days is not None:

                candidate_time = self._parse_datetime(
                    incident.get("reported_at")
                )

                if query_time and candidate_time:

                    delta_days = abs(
                        (query_time - candidate_time).total_seconds()
                    ) / 86400

                    if delta_days > self.time_window_days:
                        continue

            matches.append(incident)

        occurrence_count = len(matches) + 1

        matching_ids = tuple(
            incident["incident_id"]
            for incident in matches
        )

        if occurrence_count >= self.minimum_occurrences:

            return RecurrenceResult(
                incident_id=incident_id,
                status=RECURRENCE_DETECTED,
                occurrence_count=occurrence_count,
                matching_incident_ids=matching_ids,
                category=query_incident.get("category"),
                subcategory=query_incident.get("subcategory"),
                location=query_incident.get("location"),
                service_cycle_id=query_incident.get(
                    "service_cycle_id"
                ),
                time_window_days=self.time_window_days,
                reason=(
                    f"Recurring pattern detected across "
                    f"{occurrence_count} incidents matching "
                    f"the same operational context."
                ),
            )

        return RecurrenceResult(
            incident_id=incident_id,
            status=NO_RECURRENCE,
            occurrence_count=occurrence_count,
            matching_incident_ids=matching_ids,
            category=query_incident.get("category"),
            subcategory=query_incident.get("subcategory"),
            location=query_incident.get("location"),
            service_cycle_id=query_incident.get(
                "service_cycle_id"
            ),
            time_window_days=self.time_window_days,
            reason=(
                "Insufficient matching incidents to establish "
                "a recurring pattern."
            ),
        )