"""M8 - Lightweight evaluation and error analysis for human-reviewed matches."""

from dataclasses import dataclass
from typing import Iterable, List

from ai.components.human_review import (
    CONFIRM_DUPLICATE,
    FALSE_MATCH,
    RELATED_EVENT,
    SEPARATE_INCIDENT,
    ReviewDecision,
)
from ai.components.feedback_store import FeedbackRecord


@dataclass(frozen=True)
class ErrorCase:
    incident_id: str
    candidate_incident_id: str
    ai_decision: str
    ai_score: float
    human_outcome: str
    reviewer_reason: str | None


@dataclass(frozen=True)
class FeedbackEvaluation:
    total_records: int
    evaluated_records: int
    excluded_related_events: int
    true_positive: int
    false_positive: int
    true_negative: int
    false_negative: int
    precision: float
    recall: float
    f1: float
    accuracy: float
    errors: tuple[ErrorCase, ...]


class FeedbackEvaluator:
    """Evaluate the duplicate-candidate boundary against human outcomes."""

    POSITIVE_AI_DECISIONS = {"LIKELY_DUPLICATE", "REVIEW"}
    POSITIVE_HUMAN_OUTCOMES = {CONFIRM_DUPLICATE}
    NEGATIVE_HUMAN_OUTCOMES = {SEPARATE_INCIDENT, FALSE_MATCH}

    def evaluate(
        self,
        records: Iterable[FeedbackRecord | ReviewDecision],
    ) -> FeedbackEvaluation:
        materialized = list(records)
        tp = fp = tn = fn = 0
        excluded = 0
        errors: List[ErrorCase] = []

        for record in materialized:
            human_outcome = record.human_outcome if isinstance(record, FeedbackRecord) else record.outcome
            reviewer_reason = record.reviewer_reason
            ai_decision = record.ai_decision
            ai_score = record.ai_score
            incident_id = record.incident_id
            candidate_id = record.candidate_incident_id

            if human_outcome == RELATED_EVENT:
                excluded += 1
                continue

            if human_outcome not in (
                self.POSITIVE_HUMAN_OUTCOMES
                | self.NEGATIVE_HUMAN_OUTCOMES
            ):
                continue

            predicted_positive = ai_decision in self.POSITIVE_AI_DECISIONS
            actual_positive = human_outcome in self.POSITIVE_HUMAN_OUTCOMES

            if predicted_positive and actual_positive:
                tp += 1
            elif predicted_positive and not actual_positive:
                fp += 1
                errors.append(
                    ErrorCase(
                        incident_id=incident_id,
                        candidate_incident_id=candidate_id,
                        ai_decision=ai_decision,
                        ai_score=ai_score,
                        human_outcome=human_outcome,
                        reviewer_reason=reviewer_reason,
                    )
                )
            elif not predicted_positive and actual_positive:
                fn += 1
                errors.append(
                    ErrorCase(
                        incident_id=incident_id,
                        candidate_incident_id=candidate_id,
                        ai_decision=ai_decision,
                        ai_score=ai_score,
                        human_outcome=human_outcome,
                        reviewer_reason=reviewer_reason,
                    )
                )
            else:
                tn += 1

        evaluated = tp + fp + tn + fn
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = (
            2 * precision * recall / (precision + recall)
            if precision + recall
            else 0.0
        )
        accuracy = (tp + tn) / evaluated if evaluated else 0.0

        return FeedbackEvaluation(
            total_records=len(materialized),
            evaluated_records=evaluated,
            excluded_related_events=excluded,
            true_positive=tp,
            false_positive=fp,
            true_negative=tn,
            false_negative=fn,
            precision=round(precision, 4),
            recall=round(recall, 4),
            f1=round(f1, 4),
            accuracy=round(accuracy, 4),
            errors=tuple(errors),
        )
