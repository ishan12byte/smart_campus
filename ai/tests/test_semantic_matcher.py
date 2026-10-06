
from ai.components.semantic_matcher import SemanticIncidentMatcher


def test_matcher_finds_similar_incident():
    matcher = SemanticIncidentMatcher(threshold=0.10)

    result = matcher.predict({
        "query_incident": {
            "incident_id": "INC001",
            "description": "Projector displays a black screen",
        },
        "candidate_incidents": [
            {
                "incident_id": "INC002",
                "description": "No image appears from the projector",
            },
            {
                "incident_id": "INC003",
                "description": "Washroom tap has no running water",
            },
        ],
    })

    assert result.model_name == "semantic_incident_matcher"
    assert len(result.candidates) >= 1
    assert result.candidates[0].incident_id == "INC002"


def test_matcher_excludes_query_incident():
    matcher = SemanticIncidentMatcher(threshold=0.10)

    result = matcher.predict({
        "query_incident": {
            "incident_id": "INC001",
            "description": "Projector not working",
        },
        "candidate_incidents": [
            {
                "incident_id": "INC001",
                "description": "Projector not working",
            },
        ],
    })

    assert len(result.candidates) == 0


def test_matcher_handles_empty_candidates():
    matcher = SemanticIncidentMatcher()

    result = matcher.predict({
        "query_incident": {
            "incident_id": "INC001",
            "description": "Projector not working",
        },
        "candidate_incidents": [],
    })

    assert result.candidates == ()


def test_matcher_rejects_empty_description():
    matcher = SemanticIncidentMatcher()

    try:
        matcher.predict({
            "query_incident": {
                "incident_id": "INC001",
                "description": "",
            },
            "candidate_incidents": [],
        })
    except ValueError:
        return

    raise AssertionError("Expected ValueError for empty description")
