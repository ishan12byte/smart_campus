# AI-Driven Smart Campus Decision Engine

A hybrid **AI + deterministic decision engine** for campus incident operations.

The system is designed around a strict authority boundary:

> **AI recommends → deterministic rules validate → human authorizes → backend applies the final action.**

It combines a hardened deterministic Decision Engine with semantic incident intelligence, recurrence analysis, evidence reasoning, decision fusion, safety validation, human authorization, audit-ready final decisions, and feedback-based evaluation.

---

## 1. System Objective

The Decision Engine supports the complete incident decision workflow:

```text
Report
  ↓
Understand / Classify
  ↓
Detect Related or Recurring Incidents
  ↓
Collect Evidence
  ↓
Evaluate Evidence
  ↓
Fuse Evidence
  ↓
Generate AI Recommendation
  ↓
Validate Against Deterministic Policy
  ↓
Human Authorization
  ↓
Final Decision
  ↓
Feedback / Evaluation
```

The engine is intentionally **hybrid** rather than AI-only. Deterministic policy remains the operational source of truth for priority, responsibility, assignment, and escalation.

---

# 2. Core Architecture

```text
                         INCIDENT REPORT
                               │
                               ▼
                ┌────────────────────────────┐
                │ Hardened Decision Engine   │
                │                            │
                │ • Priority                │
                │ • Responsibility          │
                │ • Recurrence              │
                │ • Assignment              │
                │ • Workload                │
                │ • SLA / Escalation        │
                └─────────────┬──────────────┘
                              │
                              ▼
                ┌────────────────────────────┐
                │ AI Intelligence Layer      │
                │                            │
                │ • Semantic matching        │
                │ • Context scoring          │
                │ • Candidate ranking        │
                │ • Semantic recurrence      │
                └─────────────┬──────────────┘
                              │
                              ▼
                ┌────────────────────────────┐
                │ Evidence Layer             │
                │                            │
                │ • Evidence collection      │
                │ • Evidence evaluation      │
                │ • Evidence fusion          │
                └─────────────┬──────────────┘
                              │
                              ▼
                ┌────────────────────────────┐
                │ Decision Fusion             │
                │                            │
                │ AI recommendation          │
                └─────────────┬──────────────┘
                              │
                              ▼
                ┌────────────────────────────┐
                │ Deterministic Validator    │
                │                            │
                │ Policy / safety boundary   │
                └─────────────┬──────────────┘
                              │
                              ▼
                ┌────────────────────────────┐
                │ Human Authorization        │
                │                            │
                │ APPROVE / MODIFY / REJECT  │
                │ DEFER                      │
                └─────────────┬──────────────┘
                              │
                              ▼
                ┌────────────────────────────┐
                │ Final Decision Contract    │
                │ + audit information        │
                └─────────────┬──────────────┘
                              │
                              ▼
                ┌────────────────────────────┐
                │ Feedback / Error Analysis  │
                └────────────────────────────┘
```

---

# 3. Decision Authority Model

The most important architectural rule is that AI does **not** directly control campus operations.

### Deterministic Decision Engine owns

- Priority
- Responsibility status
- Department assignment
- Workload-aware assignment
- Escalation
- Emergency priority protection
- SLA handling
- Incident lifecycle rules
- Deterministic recurrence policy

### AI provides

- Semantic similarity
- Related-incident candidates
- Semantic recurrence signals
- Evidence signals
- Confidence estimates
- Explainable recommendations
- Error-analysis data

### Human authorization owns

- Approval of AI recommendations
- Modification of recommendations
- Rejection of recommendations
- Final interpretation of ambiguous evidence
- Authorization of sensitive operational changes

The backend/database remains responsible for applying any authorized mutation under its RBAC and audit controls.

---

# 4. Deterministic Decision Engine

Location:

```text
decision_engine/
```

The deterministic core is the hardened Decision Engine v1.0.

## Main modules

| Module | Responsibility |
|---|---|
| `engine.py` | Main decision pipeline and structured API |
| `models.py` | Report, Incident, DecisionInput and domain models |
| `priority.py` | Priority calculation and emergency handling |
| `responsibility.py` | Responsibility-status rules |
| `assignment.py` | Capability/capacity-aware assignment |
| `workload.py` | Resource workload calculations |
| `recurrence.py` | Deterministic incident recurrence handling |
| `matching_policy.py` | Incident matching policy |
| `escalation.py` | SLA and escalation rules |
| `lifecycle.py` | Incident lifecycle transitions |
| `categories.py` | Campus category/subcategory validation |

## Structured entry point

Use:

```python
from decision_engine.engine import DecisionInput, process_decision
```

`DecisionInput` is the preferred API.

The older `process_incident(...)` function remains for backward compatibility.

## Decision result

`DecisionResult` exposes:

```text
incident
is_new_incident
priority
responsibility
assignment
escalation
recurrence
sla_violated
explanation
```

It also provides `to_dict()` for a backend/API serialization boundary.

---

# 5. Priority Model

Priority uses five deterministic dimensions:

```text
Impact       0.30
Urgency      0.25
Safety       0.25
Deadline     0.10
Recurrence   0.10
```

Each dimension is scored from 1–5.

Priority thresholds:

```text
>= 4.0       CRITICAL
>= 3.0       HIGH
>= 2.0       MEDIUM
<  2.0       LOW
```

Emergency incident types receive the defined CRITICAL override.

Recurrence is deliberately **not allowed to become severity by itself**.

---

# 6. Responsibility Model

A report is not automatically a department failure.

Supported responsibility states include:

```text
PENDING_REVIEW
DEPARTMENT_FAILURE
USER_CAUSED
INFRASTRUCTURE_FAILURE
EXTERNAL_CAUSE
RESOURCE_CONSTRAINT
PROCESS_FAILURE
SHARED_RESPONSIBILITY
NOT_APPLICABLE
```

Responsibility-related AI evidence is advisory and remains subject to human authorization.

---

# 7. Workload and Assignment

Assignment considers:

- Department/capability eligibility
- Required workload
- Available capacity
- Current workload ratio
- Priority context

The prototype workload interpretation is:

```text
0–70%       Normal
70–90%      High
90–100%     Very High
>100%       Overloaded
```

Workload affects assignment and escalation; it does **not** determine incident seriousness.

The engine does not silently mutate resource assignment hours. The backend/database remains the source of truth.

---

# 8. Escalation

Escalation levels:

```text
NONE
DEPARTMENT_HEAD
SUPER_ADMIN
```

Examples of escalation triggers include:

- CRITICAL priority
- No eligible resource
- Assignment/resource constraint
- Repeated reopening
- SLA violation

The engine does not automatically contact external emergency services.

---

# 9. AI Intelligence Layer

Location:

```text
ai/
```

## AI components

### Semantic matching

`semantic_matcher.py`

TF-IDF baseline for transparent lexical similarity.

### Embedding matching

`embedding_matcher.py`

Uses:

```text
sentence-transformers/all-MiniLM-L6-v2
```

for semantic incident similarity.

### Context scoring

`context_scorer.py`

Combines semantic similarity with:

- category
- subcategory
- service cycle
- location evidence

Location mismatch is treated as a **review signal**, not an automatic contradiction. This allows common building-wide or infrastructure events to remain discoverable.

### Candidate ranking

`candidate_ranker.py`

Ranks historical incidents using semantic and contextual evidence.

### Semantic decision

`semantic_decision.py`

Classifies candidates as:

```text
NO_MATCH
REVIEW
LIKELY_DUPLICATE
```

### Recurrence

Two recurrence mechanisms are available:

- `recurrence_analyzer.py` — deterministic recurrence analysis
- `semantic_recurrence.py` — semantic recurrence analysis

Category compatibility is treated as an operational constraint for semantic recurrence; location is retained as evidence rather than an absolute exclusion.

---

# 10. Evidence Layer

The evidence layer contains three stages.

```text
Evidence Collection
       ↓
Evidence Evaluation
       ↓
Evidence Fusion
```

## Evidence types

The current evidence model supports:

```text
INCIDENT_DESCRIPTION
RELATED_INCIDENT
RECURRENCE_PATTERN
SERVICE_RECORD
HUMAN_FEEDBACK
LOCATION_CONTEXT
IMAGE_EVIDENCE
```

## Important evidence limitations

### Image evidence

Image evidence is supporting evidence only.

It does not independently prove:

- responsibility
- causation
- blame
- resolution

### Service records

A service record proves that activity was recorded. It does not prove that the intervention was effective.

### Human feedback

Human feedback is recorded as evidence, while the human authorization path remains authoritative for the actual decision.

---

# 11. Decision Fusion

Location:

```text
ai/components/decision_fusion.py
```

Decision Fusion converts fused evidence into an AI recommendation.

Supported recommendation types include:

```text
NO_RECOMMENDATION
REVIEW_DUPLICATE
REVIEW_RECURRENCE
REVIEW_RESPONSIBILITY
REVIEW_EVIDENCE
SUPPORTING_EVIDENCE
```

These are **recommendations**, not executable campus actions.

---

# 12. Deterministic Validation

Location:

```text
ai/components/decision_validator.py
```

This is the safety boundary between AI output and operational decision-making.

The validator protects:

- CRITICAL priority
- existing responsibility status
- department assignment
- escalation
- no automatic duplicate merging
- no automatic blame attribution
- recurrence ≠ severity escalation

All currently supported AI recommendations remain advisory and can be routed to human authorization.

---

# 13. Human Authorization

Location:

```text
ai/components/human_authorization.py
```

The human authorization gateway supports explicit human decisions such as:

```text
APPROVE
MODIFY
REJECT
DEFER
```

Authorization records include the information required to audit the decision, including reviewer identity, role, reason, original recommendation, validation context, modification information, timestamp, and final authorized action.

The gateway records authorization. It does not directly perform database mutations.

---

# 14. Final Decision Contract

Location:

```text
ai/components/final_decision.py
```

The final decision object combines:

```text
Deterministic decision
        +
AI recommendation
        +
Validation result
        +
Human authorization
        +
Audit metadata
```

This creates the backend-facing contract for the final decision state.

It can be serialized with `to_dict()` for API integration.

---

# 15. End-to-End Orchestrator

Location:

```text
ai/orchestrator.py
```

The main integration boundary is:

```python
from ai.orchestrator import (
    AIOrchestrationInput,
    CampusAIOrchestrator,
)
```

The orchestrator coordinates:

1. Deterministic decision processing
2. Semantic candidate ranking
3. Semantic recurrence detection
4. Evidence collection
5. Evidence evaluation
6. Evidence fusion
7. Decision fusion
8. Deterministic validation
9. Optional human authorization
10. Final decision construction
11. Candidate-review feedback storage

### Important behavior

The orchestrator **does not silently mutate**:

- incidents
- priority
- responsibility
- assignment
- resources
- escalation

based on AI output.

The backend remains responsible for applying an authorized final mutation.

---

# 16. Example Orchestration Flow

Conceptually:

```python
from ai.orchestrator import AIOrchestrationInput, CampusAIOrchestrator

orchestrator = CampusAIOrchestrator()

inputs = AIOrchestrationInput(
    decision_input=decision_input,
    historical_incidents=historical_incidents,
    service_records=service_records,
    image_evidence=image_evidence,
    human_feedback=human_feedback,
)

trace = orchestrator.run(inputs)

final_decision = trace.final_decision
```

If authorization is required, the caller can provide the authorization payload through the orchestrator's `authorization=` argument.

The exact database transaction that applies the authorized action should remain in the backend/API layer.

---

# 17. Human Candidate Review and Feedback

The orchestrator exposes the existing review path through:

```python
orchestrator.record_candidate_review(...)
```

The flow is:

```text
AI candidate
     ↓
HumanReviewService
     ↓
ReviewDecision
     ↓
FeedbackStore
     ↓
Evaluation / future model improvement
```

Supported review outcomes include:

```text
CONFIRM_DUPLICATE
RELATED_EVENT
SEPARATE_INCIDENT
FALSE_MATCH
```

Ambiguous cases should remain reviewable rather than being forced into binary labels.

---

# 18. Evaluation

Location:

```text
ai/evaluation.py
```

The evaluation layer uses human-confirmed feedback to calculate classification-style metrics and expose error cases.

Supported metrics include:

- True positives
- False positives
- True negatives
- False negatives
- Precision
- Recall
- F1
- Accuracy

`RELATED_EVENT` is not silently treated as either duplicate or non-duplicate for binary duplicate metrics.

The included semantic dataset is synthetic and exploratory. Its metrics must **not** be presented as production accuracy.

---

# 19. Dataset

Location:

```text
ai/data/
```

Included files include:

```text
incidents.csv
semantic_pairs.csv
matcher_comparison.csv
pair_analysis.csv
evaluation_results.csv
```

The semantic pair labels are:

```text
1   MATCH
0   NO_MATCH
-1  REVIEW
```

The dataset documentation is in:

```text
ai/data/README.md
```

Important: synthetic data is for development/evaluation of the pipeline. Production evaluation requires human-reviewed campus incident data with appropriate privacy controls.

---

# 20. Installation

Recommended environment:

```text
Python 3.12+
```

The development environment used during construction also included Python 3.13 for test execution.

From the project root:

```bash
python -m pip install --upgrade pip
python -m pip install pytest scikit-learn sentence-transformers
```

If your environment already provides these dependencies, no additional installation is required.

The deterministic Decision Engine itself uses Python standard-library functionality and does not require the embedding model.

---

# 21. Running Tests

Always prefer:

```bash
python -m pytest -q
```

over calling a potentially different `pytest` executable directly.

## Deterministic engine tests

```bash
python -m pytest -q decision_engine/tests
```

The hardened package was verified with:

```text
119 passed
```

## AI tests

```bash
python -m pytest -q ai/tests
```

Some AI tests load the Sentence Transformer model and therefore require the external `sentence-transformers` dependency and its model runtime.

## Full regression suite

```bash
python -m pytest -q
```

Run this after integration changes before treating the package as a release candidate.

---

# 22. Demonstrations

Candidate-ranking demonstration:

```bash
python ai/data/run_candidate_demo.py
```

Recurrence demonstration:

```bash
python ai/data/run_recurrence_demo.py
```

Semantic matcher evaluation:

```bash
python ai/data/evaluate_semantic_matcher.py
```

Matcher comparison:

```bash
python ai/data/compare_matchers.py
```

Dataset validation:

```bash
python ai/data/validate_dataset.py
```

---

# 23. Safety and Governance Rules

The following rules are architectural constraints, not optional recommendations.

### 1. AI does not determine blame

Responsibility evidence can trigger review, but the system does not automatically label a department or person as at fault.

### 2. Recurrence does not equal severity

Repeated incidents can surface a pattern without automatically increasing priority.

### 3. Workload does not equal seriousness

Workload affects assignment and escalation, not incident severity.

### 4. Location is evidence

Different rooms/locations do not automatically mean different root causes. Shared infrastructure events may affect multiple locations.

### 5. Duplicate merging requires human review

The AI may identify likely duplicates but never silently merges or deletes incidents.

### 6. CRITICAL decisions are protected

AI cannot downgrade a deterministic CRITICAL priority.

### 7. Human authorization is explicit

Sensitive AI recommendations must pass through the authorization layer before backend action.

### 8. External emergency calls are not automated

The decision engine does not independently call police, medical services, fire services, or other external emergency responders.

### 9. Images are supporting evidence

Image evidence does not independently establish causation or responsibility.

### 10. Auditability matters

The system retains the chain from deterministic decision → AI recommendation → validation → human authorization → final decision.

---

# 24. Current Scope

## Included

- Campus incident decisioning
- Deterministic priority
- Responsibility framework
- Workload-aware assignment
- Escalation
- SLA handling
- Incident recurrence
- Semantic incident matching
- Context-aware similarity
- Semantic recurrence
- Evidence reasoning
- Human review
- Human authorization
- Feedback storage
- Error analysis
- End-to-end orchestration
- Backend-facing final decision contract

## Deliberately not included

- Automatic timetable conflict detection
- CCTV surveillance
- Face recognition
- Automatic external emergency calls
- Mobile application
- IoT sensor integration
- Custom computer vision training
- LLM-based autonomous decision making
- Automatic blame attribution
- Automatic incident merging
- Multi-campus orchestration
- Advanced resource optimization
- Production deployment infrastructure

These can be future integrations, but they are outside the current decision-engine scope.

---

# 25. Project Structure

```text
smart_campus/
│
├── decision_engine/
│   ├── engine.py
│   ├── models.py
│   ├── priority.py
│   ├── responsibility.py
│   ├── recurrence.py
│   ├── assignment.py
│   ├── workload.py
│   ├── escalation.py
│   ├── lifecycle.py
│   ├── matching_policy.py
│   ├── categories.py
│   └── tests/
│
├── ai/
│   ├── orchestrator.py
│   ├── evaluation.py
│   ├── pipeline.py
│   ├── schemas.py
│   ├── base.py
│   │
│   ├── components/
│   │   ├── semantic_matcher.py
│   │   ├── embedding_matcher.py
│   │   ├── context_scorer.py
│   │   ├── semantic_decision.py
│   │   ├── candidate_ranker.py
│   │   ├── recurrence_analyzer.py
│   │   ├── semantic_recurrence.py
│   │   ├── evidence.py
│   │   ├── evidence_evaluator.py
│   │   ├── evidence_fusion.py
│   │   ├── decision_fusion.py
│   │   ├── decision_validator.py
│   │   ├── human_review.py
│   │   ├── human_authorization.py
│   │   ├── feedback_store.py
│   │   └── final_decision.py
│   │
│   ├── data/
│   │   ├── incidents.csv
│   │   ├── semantic_pairs.csv
│   │   ├── matcher_comparison.csv
│   │   ├── pair_analysis.csv
│   │   ├── evaluation_results.csv
│   │   └── validation/evaluation scripts
│   │
│   └── tests/
│
├── AI_ARCHITECTURE.md
├── IMPLEMENTATION_NOTES.md
├── LICENSE
└── README.md
```

---

# 26. Verification Status

The supplied hardened deterministic Decision Engine has been verified with:

```text
119 deterministic tests passed
```

The AI package contains unit/integration tests covering the AI components, decision fusion, validation, authorization, final decision contract, orchestration, evaluation, recurrence, evidence, and semantic matching.

The build notes record **113 AI core/new tests passing without requiring the external Sentence Transformer runtime**. The complete AI suite should be executed locally with `sentence-transformers` installed before release.

The repository currently contains 155 AI test functions and 119 deterministic-engine test functions; the exact final pass count should be established by running the full suite in the target environment.

---

# 27. Production Integration Boundary

This package is the **decision/intelligence layer**, not the complete campus web application.

A production backend should provide:

```text
Authentication / RBAC
        ↓
Incident API
        ↓
Decision Engine + AI Orchestrator
        ↓
Human Review / Authorization UI
        ↓
Database Transaction
        ↓
Audit Log / Notifications
```

The AI package intentionally stops before direct database mutation. This keeps operational state changes behind authenticated backend transactions and makes the AI layer testable and auditable.

---

# 28. Development Principle

Do not add AI complexity unless it improves a measurable decision capability.

The current architecture intentionally favors:

```text
Transparent rules
       +
Targeted NLP/semantic intelligence
       +
Evidence-based recommendations
       +
Deterministic safety validation
       +
Human authorization
       +
Auditable feedback
```

over an opaque autonomous AI decision-maker.

---

# 29. Status

**Decision Engine:** Complete for the current defined scope.

**AI orchestration layer:** Complete for the current defined scope.

**Next engineering stage:** end-to-end regression testing, backend/API integration, persistent human-review storage, RBAC enforcement at the API boundary, and evaluation using real human-reviewed campus data.
