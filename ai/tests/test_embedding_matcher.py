import pytest
from ai.components.embedding_matcher import EmbeddingIncidentMatcher


@pytest.fixture(scope="module")
def matcher():
    return EmbeddingIncidentMatcher(threshold=0.30)


def test_detects_different_wording_same_issue(matcher):
    query = {
        "incident_id": "INC001",
        "description": "The projector is not displaying anything.",
    }

    candidates = [
        {
            "incident_id": "INC002",
            "description": (
                "No image appears on the classroom screen "
                "when the projector is switched on."
            ),
        },
        {
            "incident_id": "INC003",
            "description": (
                "The washroom tap is leaking continuously."
            ),
        },
    ]

    result = matcher.predict({
        "query_incident": query,
        "candidate_incidents": candidates,
    })

    matched_ids = [item.incident_id for item in result.candidates]

    assert "INC002" in matched_ids
    assert "INC003" not in matched_ids


def test_excludes_query_incident_itself(matcher):
    query = {
        "incident_id": "INC001",
        "description": "The classroom projector is broken.",
    }

    candidates = [
        {
            "incident_id": "INC001",
            "description": "The classroom projector is broken.",
        }
    ]

    result = matcher.predict({
        "query_incident": query,
        "candidate_incidents": candidates,
    })

    assert result.candidates == []


def test_empty_candidates_return_empty_result(matcher):
    result = matcher.predict({
        "query_incident": {
            "incident_id": "INC001",
            "description": "The classroom projector is broken.",
        },
        "candidate_incidents": [],
    })

    assert result.candidates == []


def test_rejects_empty_query_description(matcher):
    with pytest.raises(ValueError):
        matcher.predict({
            "query_incident": {
                "incident_id": "INC001",
                "description": "   ",
            },
            "candidate_incidents": [],
        })


def test_results_are_sorted_by_similarity(matcher):
    result = matcher.predict({
        "query_incident": {
            "incident_id": "INC001",
            "description": "The classroom projector is not working.",
        },
        "candidate_incidents": [
            {
                "incident_id": "INC002",
                "description": "A projector has stopped displaying.",
            },
            {
                "incident_id": "INC003",
                "description": (
                    "The classroom projector is not working "
                    "and shows no image."
                ),
            },
        ],
    })

    scores = [item.score for item in result.candidates]

    assert scores == sorted(scores, reverse=True)


def test_does_not_mutate_input(matcher):
    data = {
        "query_incident": {
            "incident_id": "INC001",
            "description": "The classroom projector is broken.",
        },
        "candidate_incidents": [
            {
                "incident_id": "INC002",
                "description": "The projector is not displaying.",
            }
        ],
    }

    original = {
        "query_incident": data["query_incident"].copy(),
        "candidate_incidents": [
            item.copy() for item in data["candidate_incidents"]
        ],
    }

    matcher.predict(data)

    assert data == original
