import pytest

from ai.components.candidate_ranker import (
    SemanticCandidateRanker,
)


class FakeMatcher:

    class Candidate:

        def __init__(self, incident_id, score):
            self.incident_id = incident_id
            self.score = score

    class Result:

        def __init__(self, candidates):
            self.candidates = candidates

    def predict(self, data):

        candidates = data["candidate_incidents"]

        scores = {
            "INC002": 0.35,
            "INC003": 0.75,
            "INC004": 0.55,
            "INC005": 0.20,
        }

        result = []

        for incident in candidates:

            incident_id = incident["incident_id"]

            if incident_id in scores:
                result.append(
                    self.Candidate(
                        incident_id,
                        scores[incident_id],
                    )
                )

        return self.Result(result)


def make_incident(
    incident_id,
    description,
    category="IT",
    subcategory="PROJECTOR",
    location="Room 204",
    service_cycle_id="PROJ-R204",
):

    return {
        "incident_id": incident_id,
        "description": description,
        "category": category,
        "subcategory": subcategory,
        "location": location,
        "service_cycle_id": service_cycle_id,
    }


def test_candidates_are_ranked_by_context_score():

    ranker = SemanticCandidateRanker(
        matcher=FakeMatcher(),
        top_k=5,
    )

    query = make_incident(
        "INC001",
        "Projector is not working",
    )

    historical = [
        make_incident(
            "INC002",
            "Projector issue",
        ),
        make_incident(
            "INC003",
            "Projector failure",
            location="Room 310",
            service_cycle_id="PROJ-R310",
        ),
        make_incident(
            "INC004",
            "Display problem",
        ),
        make_incident(
            "INC005",
            "Network problem",
        ),
    ]

    results = ranker.rank(
        query,
        historical,
    )

    assert len(results) == 4

    # INC003 has the strongest semantic similarity.
    assert results[0].incident_id == "INC003"

    # However, because it is in a different known location,
    # it must NOT be treated as an automatic duplicate.
    assert results[0].location_conflict is True
    assert results[0].decision == "REVIEW"


def test_top_k_is_respected():

    ranker = SemanticCandidateRanker(
        matcher=FakeMatcher(),
        top_k=2,
    )

    query = make_incident(
        "INC001",
        "Projector is not working",
    )

    historical = [
        make_incident("INC002", "Projector issue"),
        make_incident("INC003", "Projector failure"),
        make_incident("INC004", "Display problem"),
        make_incident("INC005", "Network problem"),
    ]

    results = ranker.rank(
        query,
        historical,
    )

    assert len(results) == 2


def test_query_incident_is_excluded():

    ranker = SemanticCandidateRanker(
        matcher=FakeMatcher(),
        top_k=5,
    )

    query = make_incident(
        "INC001",
        "Projector is not working",
    )

    historical = [
        make_incident(
            "INC001",
            "Projector is not working",
        ),
        make_incident(
            "INC002",
            "Projector issue",
        ),
        make_incident(
            "INC003",
            "Projector failure",
        ),
    ]

    results = ranker.rank(
        query,
        historical,
    )

    returned_ids = [
        result.incident_id
        for result in results
    ]

    assert "INC001" not in returned_ids


def test_location_conflict_requires_review():

    ranker = SemanticCandidateRanker(
        matcher=FakeMatcher(),
        top_k=5,
    )

    query = make_incident(
        "INC001",
        "Projector is not working",
        location="Room 204",
    )

    historical = [
        make_incident(
            "INC003",
            "Projector failure",
            location="Room 310",
            service_cycle_id="PROJ-R310",
        ),
    ]

    results = ranker.rank(
        query,
        historical,
    )

    assert len(results) == 1

    result = results[0]

    assert result.location_conflict is True
    assert result.decision == "REVIEW"


def test_same_location_can_be_likely_duplicate():

    ranker = SemanticCandidateRanker(
        matcher=FakeMatcher(),
        top_k=5,
    )

    query = make_incident(
        "INC001",
        "Projector is not working",
        location="Room 204",
    )

    historical = [
        make_incident(
            "INC002",
            "Projector issue",
            location="Room 204",
        ),
    ]

    results = ranker.rank(
        query,
        historical,
    )

    assert len(results) == 1

    result = results[0]

    assert result.location_conflict is False
    assert result.decision == "LIKELY_DUPLICATE"


def test_empty_history_returns_empty_list():

    ranker = SemanticCandidateRanker(
        matcher=FakeMatcher(),
    )

    query = make_incident(
        "INC001",
        "Projector is not working",
    )

    assert ranker.rank(query, []) == []


def test_missing_query_id_is_rejected():

    ranker = SemanticCandidateRanker(
        matcher=FakeMatcher(),
    )

    query = {
        "description": "Projector is not working"
    }

    with pytest.raises(ValueError):
        ranker.rank(query, [])


def test_missing_query_description_is_rejected():

    ranker = SemanticCandidateRanker(
        matcher=FakeMatcher(),
    )

    query = {
        "incident_id": "INC001"
    }

    with pytest.raises(ValueError):
        ranker.rank(query, [])


def test_invalid_top_k_is_rejected():

    with pytest.raises(ValueError):
        SemanticCandidateRanker(
            matcher=FakeMatcher(),
            top_k=0,
        )