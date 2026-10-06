import pytest

from ai.components.decision_fusion import (
    DecisionRecommendation,
    NO_RECOMMENDATION,
    REVIEW_DUPLICATE,
    REVIEW_RECURRENCE,
    REVIEW_RESPONSIBILITY,
)
from ai.components.decision_validator import (
    DecisionValidator,
    ValidationResult,
    CRITICAL,
    HIGH,
)


def make_recommendation(**overrides):
    values = dict(
        incident_id="INC001",
        recommendation=NO_RECOMMENDATION,
        confidence=0.8,
        reason="Test.",
        evidence_signals=(),
        supporting_evidence=(),
        limitations=(),
        human_review_required=False,
        deterministic_priority="HIGH",
        deterministic_responsibility="PENDING_REVIEW",
        deterministic_department="IT",
        deterministic_escalation="NONE",
    )
    values.update(overrides)
    return DecisionRecommendation(**values)


def test_no_recommendation_is_allowed_and_not_human_required():
    result = DecisionValidator().validate(make_recommendation())
    assert isinstance(result, ValidationResult)
    assert result.allowed is True
    assert result.human_authorization_required is False


def test_duplicate_requires_human_authorization_and_merge_protection():
    result = DecisionValidator().validate(
        make_recommendation(
            recommendation=REVIEW_DUPLICATE,
            human_review_required=True,
        )
    )
    assert result.human_authorization_required is True
    assert any("automatic incident merge" in x.lower() for x in result.warnings)


def test_recurrence_does_not_change_priority():
    result = DecisionValidator().validate(
        make_recommendation(recommendation=REVIEW_RECURRENCE)
    )
    assert result.priority_protected is True
    assert any("priority" in x.lower() for x in result.warnings)


def test_critical_is_protected():
    result = DecisionValidator().validate(
        make_recommendation(
            recommendation=REVIEW_RECURRENCE,
            deterministic_priority=CRITICAL,
        )
    )
    assert result.priority_protected is True
    assert any("critical" in x.lower() for x in result.warnings)


def test_responsibility_is_human_authorized():
    result = DecisionValidator().validate(
        make_recommendation(
            recommendation=REVIEW_RESPONSIBILITY,
            human_review_required=True,
        )
    )
    assert result.human_authorization_required is True
    assert result.responsibility_protected is True


def test_confidence_and_priority_are_validated():
    assert DecisionValidator().validate(
        make_recommendation(confidence=0.92, deterministic_priority=HIGH)
    ).confidence == 0.92
    with pytest.raises(ValueError):
        DecisionValidator().validate(make_recommendation(confidence=1.1))
    with pytest.raises(ValueError):
        DecisionValidator().validate(make_recommendation(deterministic_priority="URGENT"))


def test_invalid_input_type_is_rejected():
    with pytest.raises(TypeError):
        DecisionValidator().validate("bad")
