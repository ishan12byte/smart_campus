import pytest

from ai.components.semantic_decision import (
    SemanticDecisionEngine,
)


def test_high_similarity_is_likely_duplicate():
    engine = SemanticDecisionEngine(
        review_threshold=0.40,
        duplicate_threshold=0.50,
    )

    result = engine.decide(0.75)

    assert result.decision == "LIKELY_DUPLICATE"
    assert result.score == 0.75


def test_medium_similarity_requires_review():
    engine = SemanticDecisionEngine(
        review_threshold=0.40,
        duplicate_threshold=0.50,
    )

    result = engine.decide(0.45)

    assert result.decision == "REVIEW"


def test_low_similarity_is_no_match():
    engine = SemanticDecisionEngine(
        review_threshold=0.40,
        duplicate_threshold=0.50,
    )

    result = engine.decide(0.25)

    assert result.decision == "NO_MATCH"


def test_duplicate_threshold_boundary():
    engine = SemanticDecisionEngine(
        review_threshold=0.40,
        duplicate_threshold=0.50,
    )

    result = engine.decide(0.50)

    assert result.decision == "LIKELY_DUPLICATE"


def test_review_threshold_boundary():
    engine = SemanticDecisionEngine(
        review_threshold=0.40,
        duplicate_threshold=0.50,
    )

    result = engine.decide(0.40)

    assert result.decision == "REVIEW"


def test_invalid_score_is_rejected():
    engine = SemanticDecisionEngine()

    with pytest.raises(ValueError):
        engine.decide(1.5)


def test_negative_score_is_rejected():
    engine = SemanticDecisionEngine()

    with pytest.raises(ValueError):
        engine.decide(-0.1)


def test_invalid_threshold_order_is_rejected():
    with pytest.raises(ValueError):
        SemanticDecisionEngine(
            review_threshold=0.60,
            duplicate_threshold=0.50,
        )