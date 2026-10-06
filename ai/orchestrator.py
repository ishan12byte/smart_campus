"""M9 - End-to-end Campus AI Decision Orchestrator.

This is the high-level integration boundary for the complete AI layer.

Flow:

    deterministic decision
        -> semantic candidates / semantic recurrence
        -> evidence collection
        -> evidence evaluation
        -> evidence fusion
        -> decision fusion
        -> deterministic validation
        -> optional human authorization
        -> final decision/audit contract

The orchestrator never silently mutates the incident, resource, priority,
responsibility, assignment, or escalation records based on AI output.
"""

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Optional, Sequence

from decision_engine.engine import DecisionInput, DecisionResult, process_decision

from .components.decision_fusion import DecisionContext, DecisionFusion, DecisionRecommendation
from .components.decision_validator import DecisionValidator, ValidationResult
from .components.evidence import EvidenceCollector
from .components.evidence_evaluator import EvidenceAssessment, EvidenceEvaluator
from .components.evidence_fusion import EvidenceFusion, FusedEvidenceResult
from .components.final_decision import FinalDecision, build_final_decision
from .components.human_authorization import HumanAuthorization, HumanAuthorizationGateway
from .components.human_review import HumanReviewService, ReviewDecision
from .components.feedback_store import FeedbackStore, FeedbackRecord


@dataclass(frozen=True)
class AIOrchestrationInput:
    decision_input: DecisionInput
    historical_incidents: Sequence[Mapping[str, Any]] = ()
    service_records: Sequence[str | Mapping[str, Any]] = ()
    image_evidence: Sequence[str | Mapping[str, Any]] = ()
    human_feedback: Sequence[str | Mapping[str, Any]] = ()
    recurrence_time_window_days: int = 30


@dataclass(frozen=True)
class AIOrchestrationTrace:
    deterministic_decision: DecisionResult
    ranked_candidates: tuple[Any, ...]
    recurrence: Any | None
    evidence_assessment: EvidenceAssessment
    fused_evidence: FusedEvidenceResult
    recommendation: DecisionRecommendation
    validation: ValidationResult
    final_decision: FinalDecision


@dataclass
class CampusAIOrchestrator:
    """Coordinates the frozen deterministic core and the AI layer."""

    ranker: Any = None
    recurrence_analyzer: Any = None
    review_service: HumanReviewService = field(default_factory=HumanReviewService)
    feedback_store: FeedbackStore = field(default_factory=FeedbackStore)
    evidence_evaluator: EvidenceEvaluator = field(default_factory=EvidenceEvaluator)
    evidence_fusion: EvidenceFusion = field(default_factory=EvidenceFusion)
    decision_fusion: DecisionFusion = field(default_factory=DecisionFusion)
    decision_validator: DecisionValidator = field(default_factory=DecisionValidator)
    human_authorization: HumanAuthorizationGateway = field(default_factory=HumanAuthorizationGateway)
    orchestrator_version: str = "1.0.0"
    policy_version: str = "1.0.0"

    def _get_ranker(self):
        if self.ranker is None:
            from .components.candidate_ranker import SemanticCandidateRanker
            self.ranker = SemanticCandidateRanker(top_k=5)
        return self.ranker

    def _get_recurrence_analyzer(self):
        if self.recurrence_analyzer is None:
            from .components.semantic_recurrence import SemanticRecurrenceAnalyzer
            self.recurrence_analyzer = SemanticRecurrenceAnalyzer(
                minimum_occurrences=3,
                top_k=10,
            )
        return self.recurrence_analyzer

    @staticmethod
    def _incident_to_dict(decision: DecisionResult) -> dict[str, Any]:
        report_id = decision.incident.report_ids[0] if decision.incident.report_ids else None
        return {
            "incident_id": str(decision.incident.id),
            "description": "",
            "category": decision.incident.category,
            "subcategory": decision.incident.subcategory,
            "location": decision.incident.location,
            "reported_at": decision.incident.started_at.isoformat(),
            "session_id": decision.incident.session_id,
            "service_cycle_id": decision.incident.service_cycle_id,
            "report_id": report_id,
        }

    @staticmethod
    def _report_to_dict(report) -> dict[str, Any]:
        return {
            "incident_id": str(report.id),
            "description": report.description,
            "category": report.category,
            "subcategory": report.subcategory,
            "location": report.location,
            "reported_at": report.reported_at.isoformat(),
            "session_id": report.session_id,
            "service_cycle_id": report.service_cycle_id,
        }

    @staticmethod
    def _normalize_history(
        historical_incidents: Sequence[Mapping[str, Any]],
    ) -> list[dict[str, Any]]:
        history: list[dict[str, Any]] = []
        for item in historical_incidents:
            if not isinstance(item, Mapping):
                raise TypeError("historical_incidents must contain mappings")
            normalized = dict(item)
            if not normalized.get("incident_id"):
                raise ValueError("each historical incident needs incident_id")
            if not str(normalized.get("description", "")).strip():
                raise ValueError(
                    "each historical incident needs a description for semantic AI"
                )
            history.append(normalized)
        return history

    @staticmethod
    def _add_optional_evidence(
        collector: EvidenceCollector,
        incident_id: str,
        entries: Iterable[str | Mapping[str, Any]],
        add_method,
        default_source_key: str = "description",
    ) -> None:
        for entry in entries:
            if isinstance(entry, Mapping):
                description = str(entry.get(default_source_key, "")).strip()
                confidence = float(entry.get("confidence", 1.0))
                metadata = dict(entry.get("metadata", {}))
            else:
                description = str(entry).strip()
                confidence = 1.0
                metadata = {}
            if description:
                add_method(
                    incident_id,
                    description,
                    confidence,
                    metadata,
                )

    def run(
        self,
        inputs: AIOrchestrationInput,
        *,
        authorization: Optional[dict[str, Any]] = None,
    ) -> AIOrchestrationTrace:
        if not isinstance(inputs, AIOrchestrationInput):
            raise TypeError("inputs must be an AIOrchestrationInput")

        deterministic = process_decision(inputs.decision_input)
        incident_id = str(deterministic.incident.id)
        query = self._report_to_dict(inputs.decision_input.report)
        query["incident_id"] = incident_id
        history = self._normalize_history(inputs.historical_incidents)

        ranked: list[Any] = []
        recurrence: Any | None = None

        if history:
            ranked = self._get_ranker().rank(query, history)
            recurrence = self._get_recurrence_analyzer().analyze(
                query,
                history,
                time_window_days=inputs.recurrence_time_window_days,
            )

        collector = EvidenceCollector()
        collector.add_incident_description(
            incident_id,
            inputs.decision_input.report.description,
        )

        for candidate in ranked:
            if candidate.decision in {"LIKELY_DUPLICATE", "REVIEW"}:
                collector.add_related_incident(
                    incident_id=incident_id,
                    related_incident_id=str(candidate.incident_id),
                    description=(
                        f"Candidate {candidate.incident_id}: "
                        f"semantic={candidate.semantic_score:.4f}, "
                        f"context={candidate.context_score:.4f}, "
                        f"decision={candidate.decision}."
                    ),
                    confidence=max(
                        0.0,
                        min(1.0, float(candidate.context_score)),
                    ),
                    metadata={
                        "semantic_score": candidate.semantic_score,
                        "context_score": candidate.context_score,
                        "location_conflict": candidate.location_conflict,
                    },
                )

        if recurrence is not None and recurrence.status != "NO_RECURRENCE":
            recurrence_confidence = min(
                1.0,
                max(
                    0.0,
                    0.60 + 0.05 * max(recurrence.occurrence_count - 2, 0),
                ),
            )
            collector.add_recurrence(
                incident_id=incident_id,
                description=recurrence.reason,
                confidence=recurrence_confidence,
                metadata={
                    "status": recurrence.status,
                    "occurrence_count": recurrence.occurrence_count,
                    "matching_incident_ids": list(recurrence.matching_incident_ids),
                },
            )

        self._add_optional_evidence(
            collector,
            incident_id,
            inputs.service_records,
            collector.add_service_record,
        )
        self._add_optional_evidence(
            collector,
            incident_id,
            inputs.image_evidence,
            collector.add_image_evidence,
        )
        self._add_optional_evidence(
            collector,
            incident_id,
            inputs.human_feedback,
            collector.add_human_feedback,
        )

        collection = collector.collect(incident_id)
        assessment = self.evidence_evaluator.evaluate(collection)
        fused = self.evidence_fusion.fuse(
            collection,
            (assessment,),
        )

        context = DecisionContext(
            priority=deterministic.priority["level"],
            responsibility_status=deterministic.responsibility["status"],
            assigned_department=(
                deterministic.assignment.resource.department
                if deterministic.assignment.resource is not None
                else None
            ),
            escalation_level=deterministic.escalation.level,
        )

        recommendation = self.decision_fusion.fuse(
            incident_id,
            fused,
            context,
        )
        validation = self.decision_validator.validate(recommendation)

        human_auth: HumanAuthorization | None = None
        if authorization is not None:
            human_auth = self.human_authorization.authorize(
                recommendation=recommendation,
                validation=validation,
                **authorization,
            )

        final = build_final_decision(
            deterministic_decision=deterministic,
            ai_recommendation=recommendation,
            validation=validation,
            human_authorization=human_auth,
            orchestrator_version=self.orchestrator_version,
            policy_version=self.policy_version,
        )

        return AIOrchestrationTrace(
            deterministic_decision=deterministic,
            ranked_candidates=tuple(ranked),
            recurrence=recurrence,
            evidence_assessment=assessment,
            fused_evidence=fused,
            recommendation=recommendation,
            validation=validation,
            final_decision=final,
        )
    def record_candidate_review(
        self,
        incident_id: str,
        candidate_incident_id: str,
        ai_decision: str,
        ai_score: float,
        outcome: str,
        reviewer_id: str,
        reviewer_reason: str | None = None,
    ) -> FeedbackRecord:
        """Record a human candidate review through the existing review/feedback path."""
        decision = self.review_service.review(
            incident_id=incident_id,
            candidate_incident_id=candidate_incident_id,
            ai_decision=ai_decision,
            ai_score=ai_score,
            outcome=outcome,
            reviewer_id=reviewer_id,
            reviewer_reason=reviewer_reason,
        )
        return self.feedback_store.record_review(decision)

