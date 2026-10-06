import pytest

from ai.components.evidence import (
    EvidenceCollection,
    EvidenceCollector,
)
from ai.components.evidence_evaluator import (
    EvidenceAssessment,
    NO_ACTION,
    RESPONSIBILITY_REVIEW,
    RECURRENCE_REVIEW,
    DUPLICATE_REVIEW,
)
from ai.components.evidence_fusion import (
    EvidenceFusion,
    FusedEvidenceResult,
    FUSION_NO_ACTION,
    FUSION_REVIEW,
    FUSION_SUPPORTING,
)


def make_collection(incident_id="INC001"):
    collector = EvidenceCollector()

    collector.add_incident_description(
        incident_id,
        "Projector is not working.",
    )

    return collector.collect(incident_id)


def make_assessment(
    incident_id="INC001",
    signal=NO_ACTION,
    confidence=0.8,
    supporting=(),
    limitations=(),
):
    return EvidenceAssessment(
        incident_id=incident_id,
        signal=signal,
        confidence=confidence,
        supporting_evidence=tuple(supporting),
        limitations=tuple(limitations),
        evidence_count=len(supporting),
    )


class TestEvidenceFusion:

    def test_no_evidence_returns_no_action(self):
        collection = EvidenceCollection(
            incident_id="INC001",
            items=(),
            evidence_count=0,
            has_image_evidence=False,
            has_human_feedback=False,
            has_recurrence_evidence=False,
            has_service_evidence=False,
        )

        assessment = make_assessment(
            signal=NO_ACTION,
            confidence=0.0,
        )

        result = EvidenceFusion().fuse(
            collection,
            (assessment,),
        )

        assert isinstance(result, FusedEvidenceResult)
        assert result.incident_id == "INC001"
        assert result.status == FUSION_NO_ACTION
        assert result.signals == ()
        assert result.evidence_count == 0
        assert result.confidence == 0.0
        assert result.human_review_required is False

    def test_evidence_without_actionable_signal_is_supporting(self):
        collection = make_collection()

        assessment = make_assessment(
            signal=NO_ACTION,
            confidence=0.75,
        )

        result = EvidenceFusion().fuse(
            collection,
            (assessment,),
        )

        assert result.status == FUSION_SUPPORTING
        assert result.evidence_count == 1
        assert result.confidence == 0.75
        assert result.human_review_required is False

    def test_recurrence_signal_requires_review(self):
        collection = make_collection()

        assessment = make_assessment(
            signal=RECURRENCE_REVIEW,
            confidence=0.85,
            supporting=(
                "Recurring incident pattern detected.",
            ),
        )

        result = EvidenceFusion().fuse(
            collection,
            (assessment,),
        )

        assert result.status == FUSION_REVIEW
        assert result.signals == (RECURRENCE_REVIEW,)
        assert result.human_review_required is True

    def test_duplicate_signal_requires_review(self):
        collection = make_collection()

        assessment = make_assessment(
            signal=DUPLICATE_REVIEW,
            confidence=0.90,
            supporting=(
                "Related historical incidents were identified.",
            ),
        )

        result = EvidenceFusion().fuse(
            collection,
            (assessment,),
        )

        assert result.status == FUSION_REVIEW
        assert result.signals == (DUPLICATE_REVIEW,)
        assert result.human_review_required is True

    def test_responsibility_signal_requires_review(self):
        collection = make_collection()

        assessment = make_assessment(
            signal=RESPONSIBILITY_REVIEW,
            confidence=0.80,
            supporting=(
                "Relevant service-record evidence is available.",
            ),
        )

        result = EvidenceFusion().fuse(
            collection,
            (assessment,),
        )

        assert result.status == FUSION_REVIEW
        assert result.signals == (RESPONSIBILITY_REVIEW,)
        assert result.human_review_required is True

    def test_multiple_signals_are_preserved(self):
        collection = make_collection()

        assessments = (
            make_assessment(
                signal=RECURRENCE_REVIEW,
                confidence=0.80,
                supporting=(
                    "Recurring incident pattern detected.",
                ),
            ),
            make_assessment(
                signal=DUPLICATE_REVIEW,
                confidence=0.90,
                supporting=(
                    "Related historical incidents were identified.",
                ),
            ),
            make_assessment(
                signal=RESPONSIBILITY_REVIEW,
                confidence=0.70,
                supporting=(
                    "Relevant service-record evidence is available.",
                ),
            ),
        )

        result = EvidenceFusion().fuse(
            collection,
            assessments,
        )

        assert result.status == FUSION_REVIEW

        assert result.signals == (
            RECURRENCE_REVIEW,
            DUPLICATE_REVIEW,
            RESPONSIBILITY_REVIEW,
        )

        assert result.human_review_required is True

    def test_duplicate_supporting_evidence_is_removed(self):
        collection = make_collection()

        assessments = (
            make_assessment(
                signal=RECURRENCE_REVIEW,
                confidence=0.80,
                supporting=(
                    "Recurring incident pattern detected.",
                ),
            ),
            make_assessment(
                signal=DUPLICATE_REVIEW,
                confidence=0.90,
                supporting=(
                    "Recurring incident pattern detected.",
                ),
            ),
        )

        result = EvidenceFusion().fuse(
            collection,
            assessments,
        )

        assert result.supporting_evidence == (
            "Recurring incident pattern detected.",
        )

    def test_duplicate_limitations_are_removed(self):
        collection = make_collection()

        limitation = (
            "Image evidence alone does not establish responsibility "
            "or causation."
        )

        assessments = (
            make_assessment(
                signal=NO_ACTION,
                confidence=0.70,
                limitations=(limitation,),
            ),
            make_assessment(
                signal=NO_ACTION,
                confidence=0.80,
                limitations=(limitation,),
            ),
        )

        result = EvidenceFusion().fuse(
            collection,
            assessments,
        )

        assert result.limitations == (limitation,)

    def test_confidence_is_average_of_assessments(self):
        collection = make_collection()

        assessments = (
            make_assessment(confidence=0.80),
            make_assessment(confidence=0.60),
        )

        result = EvidenceFusion().fuse(
            collection,
            assessments,
        )

        assert result.confidence == 0.70

    def test_confidence_never_exceeds_one(self):
        collection = make_collection()

        assessments = (
            make_assessment(confidence=1.0),
            make_assessment(confidence=1.0),
        )

        result = EvidenceFusion().fuse(
            collection,
            assessments,
        )

        assert result.confidence <= 1.0

    def test_evidence_count_is_preserved(self):
        collector = EvidenceCollector()

        collector.add_incident_description(
            "INC001",
            "Network unavailable.",
        )

        collector.add_related_incident(
            "INC001",
            "INC002",
            "Similar network incident.",
            0.85,
        )

        collection = collector.collect("INC001")

        assessment = make_assessment(
            signal=DUPLICATE_REVIEW,
            confidence=0.88,
        )

        result = EvidenceFusion().fuse(
            collection,
            (assessment,),
        )

        assert result.evidence_count == 2
        assert result.assessment_count == 1

    def test_human_feedback_remains_evidence_not_authority(self):
        collector = EvidenceCollector()

        collector.add_human_feedback(
            "INC001",
            "Reviewer confirmed related event.",
        )

        collection = collector.collect("INC001")

        assessment = make_assessment(
            signal=RESPONSIBILITY_REVIEW,
            confidence=0.95,
            supporting=(
                "Human review feedback is available.",
            ),
        )

        result = EvidenceFusion().fuse(
            collection,
            (assessment,),
        )

        assert result.status == FUSION_REVIEW
        assert result.human_review_required is True

        assert not hasattr(result, "responsibility")
        assert not hasattr(result, "department")
        assert not hasattr(result, "priority")

    def test_image_evidence_does_not_automatically_create_review(self):
        collector = EvidenceCollector()

        collector.add_image_evidence(
            "INC001",
            "Photo of damaged projector.",
        )

        collection = collector.collect("INC001")

        assessment = make_assessment(
            signal=NO_ACTION,
            confidence=0.60,
            limitations=(
                "Image evidence alone does not establish responsibility "
                "or causation.",
            ),
        )

        result = EvidenceFusion().fuse(
            collection,
            (assessment,),
        )

        assert result.status == FUSION_SUPPORTING
        assert result.human_review_required is False

        assert (
            "Image evidence alone does not establish responsibility "
            "or causation."
            in result.limitations
        )

    def test_mismatched_incident_ids_are_rejected(self):
        collection = make_collection("INC001")

        assessment = make_assessment(
            incident_id="INC999",
        )

        with pytest.raises(ValueError):
            EvidenceFusion().fuse(
                collection,
                (assessment,),
            )

    def test_invalid_collection_type_is_rejected(self):
        with pytest.raises(TypeError):
            EvidenceFusion().fuse(
                "not a collection",
                (),
            )

    def test_invalid_assessment_type_is_rejected(self):
        collection = make_collection()

        with pytest.raises(TypeError):
            EvidenceFusion().fuse(
                collection,
                ("not an assessment",),
            )

    def test_invalid_assessment_confidence_is_rejected(self):
        collection = make_collection()

        assessment = EvidenceAssessment(
            incident_id="INC001",
            signal=NO_ACTION,
            confidence=1.5,
            supporting_evidence=(),
            limitations=(),
            evidence_count=0,
        )

        with pytest.raises(ValueError):
            EvidenceFusion().fuse(
                collection,
                (assessment,),
            )

    def test_invalid_signal_is_rejected(self):
        collection = make_collection()

        assessment = EvidenceAssessment(
            incident_id="INC001",
            signal="INVALID_SIGNAL",
            confidence=0.8,
            supporting_evidence=(),
            limitations=(),
            evidence_count=0,
        )

        with pytest.raises(ValueError):
            EvidenceFusion().fuse(
                collection,
                (assessment,),
            )

    def test_empty_assessments_with_evidence_have_zero_confidence(self):
        collection = make_collection()

        result = EvidenceFusion().fuse(
            collection,
            (),
        )

        assert result.status == FUSION_SUPPORTING
        assert result.evidence_count == 1
        assert result.assessment_count == 0
        assert result.confidence == 0.0
        assert result.human_review_required is False