from datetime import datetime, timezone
from ai.components.feedback_store import FeedbackRecord
from ai.evaluation import FeedbackEvaluator
from ai.components.human_review import (
    CONFIRM_DUPLICATE, FALSE_MATCH, RELATED_EVENT, SEPARATE_INCIDENT,
)


def rec(aid, score, outcome):
    return FeedbackRecord(
        incident_id="A", candidate_incident_id=aid, ai_decision=outcome[0], ai_score=score,
        human_outcome=outcome[1], reviewer_id="r", reviewer_reason="test",
        recorded_at=datetime.now(timezone.utc),
    )


def test_feedback_metrics_and_errors():
    records = [
        rec("B1", .9, ("LIKELY_DUPLICATE", CONFIRM_DUPLICATE)),
        rec("B2", .9, ("REVIEW", SEPARATE_INCIDENT)),
        rec("B3", .1, ("NO_MATCH", CONFIRM_DUPLICATE)),
        rec("B4", .1, ("NO_MATCH", FALSE_MATCH)),
        rec("B5", .8, ("REVIEW", RELATED_EVENT)),
    ]
    m = FeedbackEvaluator().evaluate(records)
    assert m.total_records == 5
    assert m.evaluated_records == 4
    assert m.excluded_related_events == 1
    assert (m.true_positive, m.false_positive, m.true_negative, m.false_negative) == (1, 1, 1, 1)
    assert m.precision == .5
    assert m.recall == .5
    assert m.f1 == .5
    assert m.accuracy == .5
    assert len(m.errors) == 2
