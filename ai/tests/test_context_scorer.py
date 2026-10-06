from ai.components.context_scorer import (
    ContextAwareScorer,
)


def incident(
    category="IT",
    subcategory="PROJECTOR",
    location="Room 204",
    service_cycle_id="PROJ-R204",
):
    return {
        "category": category,
        "subcategory": subcategory,
        "location": location,
        "service_cycle_id": service_cycle_id,
    }


def test_exact_context_produces_expected_score():

    scorer = ContextAwareScorer()

    query = incident()
    candidate = incident()

    result = scorer.score(
        query,
        candidate,
        semantic_score=0.50,
    )

    assert result.category_match == 1.0
    assert result.subcategory_match == 1.0
    assert result.location_match == 1.0
    assert result.service_cycle_match == 1.0

    assert result.location_conflict is False

    expected = (
        0.70 * 0.50
        + 0.10
        + 0.10
        + 0.10
    )

    assert abs(result.final_score - expected) < 1e-9


def test_different_location_is_context_difference():

    scorer = ContextAwareScorer()

    query = incident(
        location="Room 204",
        service_cycle_id="PROJ-R204",
    )

    candidate = incident(
        location="Room 310",
        service_cycle_id="PROJ-R310",
    )

    result = scorer.score(
        query,
        candidate,
        semantic_score=0.6728,
    )

    assert result.location_match == 0.0
    assert result.service_cycle_match == 0.0

    # Different location is recorded but does NOT
    # zero out the semantic/context score.
    assert result.location_conflict is True

    expected = 0.70 * 0.6728 + 0.10 + 0.10

    assert abs(result.final_score - expected) < 1e-9


def test_same_location_is_not_a_conflict():

    scorer = ContextAwareScorer()

    query = incident(location="Room 204")
    candidate = incident(location="Room 204")

    result = scorer.score(
        query,
        candidate,
        semantic_score=0.60,
    )

    assert result.location_match == 1.0
    assert result.location_conflict is False


def test_missing_location_is_not_a_conflict():

    scorer = ContextAwareScorer()

    query = incident(location="")
    candidate = incident(location="Room 310")

    result = scorer.score(
        query,
        candidate,
        semantic_score=0.60,
    )

    assert result.location_conflict is False


def test_category_mismatch_is_penalized():

    scorer = ContextAwareScorer()

    query = incident(category="IT")
    candidate = incident(category="MAINTENANCE")

    result = scorer.score(
        query,
        candidate,
        semantic_score=0.60,
    )

    assert result.category_match == 0.0


def test_semantic_score_is_validated():

    scorer = ContextAwareScorer()

    query = incident()
    candidate = incident()

    try:
        scorer.score(
            query,
            candidate,
            semantic_score=1.2,
        )

        assert False, "Expected ValueError"

    except ValueError:
        pass