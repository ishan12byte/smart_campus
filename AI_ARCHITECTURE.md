# Campus Operations AI + Deterministic Decision Architecture

## End-to-end flow

Incident report
→ deterministic decision core
→ semantic candidate matching / semantic recurrence
→ evidence collection
→ evidence evaluation
→ evidence fusion
→ decision fusion
→ deterministic validation
→ human authorization
→ final decision contract
→ human feedback store
→ evaluation/error analysis

## Authority boundaries

- The deterministic Decision Engine remains the source of truth for priority, responsibility, assignment, and escalation.
- AI produces evidence and recommendations; it does not directly mutate operational records.
- Duplicate/related-incident recommendations require human review before any consolidation.
- Recurrence is an analytical pattern and does not automatically increase severity.
- Responsibility recommendations remain reviewable and human-authorized.
- CRITICAL priority is protected from AI downgrade.
- Existing department assignment and escalation are protected from AI removal/downgrade.
- Image evidence supports investigation but does not prove causation or responsibility by itself.
- Service records prove recorded activity, not effectiveness.
- The human authorization gateway records the decision; a backend transaction remains responsible for applying any authorized database mutation under RBAC/audit controls.

## Components added in M7-M9

- `ai/components/decision_validator.py` — M7.2 policy/safety gate.
- `ai/components/human_authorization.py` — M7.3 explicit human-in-the-loop authorization record.
- `ai/components/final_decision.py` — M7.4 backend-facing final decision/audit contract.
- `ai/evaluation.py` — M8 feedback-based metrics and error cases.
- `ai/orchestrator.py` — M9 end-to-end integration boundary.

## Compatibility hardening

- `ai/components/__init__.py` now uses lazy imports so optional model dependencies do not break unrelated deterministic/evidence tests.
- `SemanticRecurrenceAnalyzer` now passes `candidate_incidents` to `EmbeddingIncidentMatcher`, matching the matcher's actual API.
- The hardened Decision Engine v1.0 is used as the deterministic core.

## Verification

- Hardened deterministic Decision Engine: 119 tests passed.
- AI core/new tests that do not require the external sentence-transformer runtime: 113 tests passed in the build environment.
- The embedding-dependent tests should be run in the user's environment where `sentence-transformers` is installed.
