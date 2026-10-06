"""AI component package with lazy optional-model imports."""

_LAZY_EXPORTS = {
    "EmbeddingIncidentMatcher": ("ai.components.embedding_matcher", "EmbeddingIncidentMatcher"),
    "SemanticIncidentMatcher": ("ai.components.semantic_matcher", "SemanticIncidentMatcher"),
    "SemanticCandidateRanker": ("ai.components.candidate_ranker", "SemanticCandidateRanker"),
    "RankedCandidate": ("ai.components.candidate_ranker", "RankedCandidate"),
    "SemanticRecurrenceAnalyzer": ("ai.components.semantic_recurrence", "SemanticRecurrenceAnalyzer"),
    "EvidenceCollector": ("ai.components.evidence", "EvidenceCollector"),
    "EvidenceCollection": ("ai.components.evidence", "EvidenceCollection"),
    "EvidenceItem": ("ai.components.evidence", "EvidenceItem"),
    "EvidenceEvaluator": ("ai.components.evidence_evaluator", "EvidenceEvaluator"),
    "EvidenceAssessment": ("ai.components.evidence_evaluator", "EvidenceAssessment"),
    "EvidenceFusion": ("ai.components.evidence_fusion", "EvidenceFusion"),
    "FusedEvidenceResult": ("ai.components.evidence_fusion", "FusedEvidenceResult"),
    "DecisionFusion": ("ai.components.decision_fusion", "DecisionFusion"),
    "DecisionContext": ("ai.components.decision_fusion", "DecisionContext"),
    "DecisionRecommendation": ("ai.components.decision_fusion", "DecisionRecommendation"),
    "DecisionValidator": ("ai.components.decision_validator", "DecisionValidator"),
    "ValidationResult": ("ai.components.decision_validator", "ValidationResult"),
    "HumanAuthorizationGateway": ("ai.components.human_authorization", "HumanAuthorizationGateway"),
    "HumanAuthorization": ("ai.components.human_authorization", "HumanAuthorization"),
    "FinalDecision": ("ai.components.final_decision", "FinalDecision"),
    "build_final_decision": ("ai.components.final_decision", "build_final_decision"),
}

__all__ = sorted(_LAZY_EXPORTS)


def __getattr__(name):
    if name not in _LAZY_EXPORTS:
        raise AttributeError(name)
    module_name, attr_name = _LAZY_EXPORTS[name]
    from importlib import import_module
    value = getattr(import_module(module_name), attr_name)
    globals()[name] = value
    return value
