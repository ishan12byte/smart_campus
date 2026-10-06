import pytest

from ai.components.evidence import EvidenceCollection
from ai.components.evidence_fusion import (
    FusedEvidenceResult,
    FUSION_NO_ACTION,
    FUSION_REVIEW,
    FUSION_SUPPORTING,
)
from ai.components.decision_fusion import (
    DecisionContext,
    DecisionFusion,
    DecisionRecommendation,
    NO_RECOMMENDATION,
    REVIEW_DUPLICATE,
    REVIEW_RECURRENCE,
    REVIEW_RESPONSIBILITY,
    REVIEW_EVIDENCE,
    SUPPORTING_EVIDENCE,
)


def make_evidence(
    incident_id="INC001",
    status=FUSION_NO_ACTION,
    signals=(),
    confidence=0.0,
    supporting=(),
    limitations=(),
    human_review_required=False,
):
    return FusedEvidenceResult(
        incident_id=incident_id,
        status=status,
        signals=tuple(signals),
        evidence=(),
        supporting_evidence=tuple(supporting),
        limitations=tuple(limitations),
        evidence_count=len(supporting),
        assessment_count=1,
        confidence=confidence,
        human_review_required=human_review_required,
    )


def make_context():
    return DecisionContext(
        priority="HIGH",
        responsibility_status="PENDING_REVIEW",
        assigned_department="IT",
        escalation_level="NONE",
    )


class TestDecisionFusion:

    def test_no_evidence_produces_no_recommendation(self):
        evidence = make_evidence()

        result = DecisionFusion().fuse(
            "INC001",
            evidence,
            make_context(),
        )

        assert isinstance(result, DecisionRecommendation)
        assert result.recommendation == NO_RECOMMENDATION
        assert result.human_review_required is False
        assert result.deterministic_priority == "HIGH"
        assert result.deterministic_responsibility == "PENDING_REVIEW"
        assert result.deterministic_department == "IT"
        assert result.deterministic_escalation == "NONE"

    def test_duplicate_evidence_produces_duplicate_review(self):
        evidence = make_evidence(
            status=FUSION_REVIEW,
            signals=("DUPLICATE_REVIEW",),
            confidence=0.91,
            supporting=(
                "Related historical incidents were identified.",
            ),
            human_review_required=True,
        )

        result = DecisionFusion().fuse(
            "INC001",
            evidence,
            make_context(),
        )

        assert result.recommendation == REVIEW_DUPLICATE
        assert result.confidence == 0.91
        assert result.human_review_required is True

    def test_recurrence_evidence_produces_recurrence_review(self):
        evidence = make_evidence(
            status=FUSION_REVIEW,
            signals=("RECURRENCE_REVIEW",),
            confidence=0.85,
            supporting=(
                "Recurring incident pattern detected.",
            ),
            human_review_required=True,
        )

        result = DecisionFusion().fuse(
            "INC001",
            evidence,
            make_context(),
        )

        assert result.recommendation == REVIEW_RECURRENCE

    def test_responsibility_evidence_produces_review(self):
        evidence = make_evidence(
            status=FUSION_REVIEW,
            signals=("RESPONSIBILITY_REVIEW",),
            confidence=0.80,
            supporting=(
                "Relevant service-record evidence is available.",
            ),
            human_review_required=True,
        )

        result = DecisionFusion().fuse(
            "INC001",
            evidence,
            make_context(),
        )

        assert result.recommendation == REVIEW_RESPONSIBILITY

    def test_generic_review_produces_evidence_review(self):
        evidence = make_evidence(
            status=FUSION_REVIEW,
            signals=(),
            confidence=0.70,
            limitations=("Additional interpretation required.",),
            human_review_required=True,
        )

        result = DecisionFusion().fuse(
            "INC001",
            evidence,
            make_context(),
        )

        assert result.recommendation == REVIEW_EVIDENCE
        assert result.human_review_required is True

    def test_supporting_evidence_does_not_trigger_review(self):
        evidence = make_evidence(
            status=FUSION_SUPPORTING,
            confidence=0.60,
            supporting=(
                "Image evidence is available as supporting evidence.",
            ),
        )

        result = DecisionFusion().fuse(
            "INC001",
            evidence,
            make_context(),
        )

        assert result.recommendation == SUPPORTING_EVIDENCE
        assert result.human_review_required is False

    def test_duplicate_takes_priority_over_recurrence(self):
        evidence = make_evidence(
            status=FUSION_REVIEW,
            signals=(
                "RECURRENCE_REVIEW",
                "DUPLICATE_REVIEW",
            ),
            confidence=0.90,
            human_review_required=True,
        )

        result = DecisionFusion().fuse(
            "INC001",
            evidence,
            make_context(),
        )

        assert result.recommendation == REVIEW_DUPLICATE

    def test_duplicate_takes_priority_over_responsibility(self):
        evidence = make_evidence(
            status=FUSION_REVIEW,
            signals=(
                "RESPONSIBILITY_REVIEW",
                "DUPLICATE_REVIEW",
            ),
            confidence=0.90,
            human_review_required=True,
        )

        result = DecisionFusion().fuse(
            "INC001",
            evidence,
            make_context(),
        )

        assert result.recommendation == REVIEW_DUPLICATE

    def test_deterministic_decision_is_not_modified(self):
        context = DecisionContext(
            priority="CRITICAL",
            responsibility_status="DEPARTMENT_FAILURE",
            assigned_department="ELECTRICAL",
            escalation_level="SUPER_ADMIN",
        )

        evidence = make_evidence(
            status=FUSION_REVIEW,
            signals=("DUPLICATE_REVIEW",),
            confidence=0.92,
            human_review_required=True,
        )

        result = DecisionFusion().fuse(
            "INC001",
            evidence,
            context,
        )

        assert result.deterministic_priority == "CRITICAL"
        assert (
            result.deterministic_responsibility
            == "DEPARTMENT_FAILURE"
        )
        assert result.deterministic_department == "ELECTRICAL"
        assert result.deterministic_escalation == "SUPER_ADMIN"

    def test_incident_id_mismatch_is_rejected(self):
        evidence = make_evidence(
            incident_id="INC002",
        )

        with pytest.raises(ValueError):
            DecisionFusion().fuse(
                "INC001",
                evidence,
                make_context(),
            )

    def test_invalid_incident_id_is_rejected(self):
        evidence = make_evidence()

        with pytest.raises(ValueError):
            DecisionFusion().fuse(
                "",
                evidence,
                make_context(),
            )

    def test_invalid_evidence_type_is_rejected(self):
        with pytest.raises(TypeError):
            DecisionFusion().fuse(
                "INC001",
                "invalid evidence",
                make_context(),
            )

    def test_invalid_context_type_is_rejected(self):
        evidence = make_evidence()

        with pytest.raises(TypeError):
            DecisionFusion().fuse(
                "INC001",
                evidence,
                "invalid context",
            )

    def test_supporting_evidence_and_limitations_are_preserved(self):
        evidence = make_evidence(
            status=FUSION_SUPPORTING,
            confidence=0.72,
            supporting=(
                "Service record available.",
                "Related historical incident found.",
            ),
            limitations=(
                "Service activity does not prove effectiveness.",
            ),
        )

        result = DecisionFusion().fuse(
            "INC001",
            evidence,
            make_context(),
        )

        assert result.supporting_evidence == (
            "Service record available.",
            "Related historical incident found.",
        )

        assert result.limitations == (
            "Service activity does not prove effectiveness.",
        )

    def test_confidence_is_preserved(self):
        evidence = make_evidence(
            status=FUSION_REVIEW,
            signals=("RECURRENCE_REVIEW",),
            confidence=0.8732,
            human_review_required=True,
        )

        result = DecisionFusion().fuse(
            "INC001",
            evidence,
            make_context(),
        )

        assert result.confidence == 0.8732

    def test_ai_does_not_create_automatic_department_assignment(self):
        context = DecisionContext(
            priority="HIGH",
            responsibility_status="PENDING_REVIEW",
            assigned_department=None,
            escalation_level="NONE",
        )

        evidence = make_evidence(
            status=FUSION_REVIEW,
            signals=("RESPONSIBILITY_REVIEW",),
            confidence=0.90,
            human_review_required=True,
        )

        result = DecisionFusion().fuse(
            "INC001",
            evidence,
            context,
        )

        assert result.recommendation == REVIEW_RESPONSIBILITY
        assert result.deterministic_department is None