from dataclasses import dataclass
from datetime import datetime

from decision_engine.engine import DecisionInput, PriorityInput, ResponsibilityInput
from decision_engine.models import Report
from decision_engine.workload import Resource

from ai.orchestrator import AIOrchestrationInput, CampusAIOrchestrator
from ai.components.human_authorization import APPROVE


@dataclass
class Candidate:
    incident_id: str
    semantic_score: float
    context_score: float
    category_match: float = 1.0
    subcategory_match: float = 1.0
    location_match: float = 1.0
    service_cycle_match: float = 1.0
    location_conflict: bool = False
    decision: str = "LIKELY_DUPLICATE"
    reason: str = "candidate"


@dataclass
class Recurrence:
    incident_id: str
    status: str = "NO_RECURRENCE"
    occurrence_count: int = 1
    matching_incident_ids: tuple[str, ...] = ()
    reason: str = "none"
    candidates: tuple = ()


class FakeRanker:
    def rank(self, query, history):
        assert query["description"]
        assert history
        return [Candidate("INC-H1", .90, .88)]


class FakeRecurrence:
    def analyze(self, query, history, time_window_days=30):
        return Recurrence(incident_id=query["incident_id"])


def make_input():
    report = Report(
        id=10,
        description="Projector display is black after power-on.",
        category="IT",
        subcategory="PROJECTOR",
        location="Room 204",
        reported_at=datetime(2026, 10, 6, 10, 0),
        reporter_id=100,
        service_cycle_id="PROJ-R204-2026-10",
    )
    return AIOrchestrationInput(
        decision_input=DecisionInput(
            report=report,
            incidents=[],
            resources=[Resource(1, "IT-1", "IT", 8, 2)],
            new_incident_id=99,
            priority=PriorityInput(3, 3, 1, 2, 1),
            responsibility=ResponsibilityInput(),
            required_hours=1,
        ),
        historical_incidents=[
            {
                "incident_id": "INC-H1",
                "description": "No image from projector in Room 204.",
                "category": "IT",
                "subcategory": "PROJECTOR",
                "location": "Room 204",
                "service_cycle_id": "PROJ-R204-2026-10",
                "reported_at": "2026-10-05T10:00:00",
            }
        ],
        service_records=("Projector inspection was logged.",),
        image_evidence=("Photo shows black projector output.",),
    )


def test_orchestrator_completes_end_to_end_without_auto_authorization():
    orchestrator = CampusAIOrchestrator(
        ranker=FakeRanker(),
        recurrence_analyzer=FakeRecurrence(),
    )
    trace = orchestrator.run(make_input())

    assert trace.deterministic_decision.incident.id == 99
    assert len(trace.ranked_candidates) == 1
    assert trace.recommendation.recommendation == "REVIEW_DUPLICATE"
    assert trace.validation.allowed is True
    assert trace.final_decision.final_status == "PENDING_AUTHORIZATION"
    assert trace.final_decision.human_authorized is False
    assert trace.fused_evidence.evidence_count >= 3


def test_orchestrator_can_complete_with_explicit_human_authorization():
    orchestrator = CampusAIOrchestrator(
        ranker=FakeRanker(),
        recurrence_analyzer=FakeRecurrence(),
    )
    trace = orchestrator.run(
        make_input(),
        authorization={
            "reviewer_id": "staff-10",
            "reviewer_role": "DEPARTMENT_HEAD",
            "action": APPROVE,
            "reason": "Reviewed the evidence and approved the recommendation.",
        },
    )

    assert trace.final_decision.final_status == "AUTHORIZED"
    assert trace.final_decision.human_authorized is True
    assert trace.final_decision.human_authorization is not None


def test_existing_human_review_and_feedback_path_is_integrated():
    orchestrator = CampusAIOrchestrator()
    record = orchestrator.record_candidate_review(
        incident_id="99",
        candidate_incident_id="INC-H1",
        ai_decision="REVIEW",
        ai_score=.88,
        outcome="CONFIRM_DUPLICATE",
        reviewer_id="staff-10",
        reviewer_reason="Same room and same service cycle.",
    )
    assert record.human_outcome == "CONFIRM_DUPLICATE"
    assert orchestrator.feedback_store.count() == 1
