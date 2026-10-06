# Decision Engine v1.0 Hardening — Implementation Notes

This version applies only the high-value changes required before moving to the AI layer. It intentionally does not add ML/LLM logic, dashboards, deployment infrastructure, automatic timetable detection, or advanced resource optimization.

## 1. Lifecycle + recurrence

**Files changed:** `decision_engine/recurrence.py`, `decision_engine/lifecycle.py`

- Recurrence matching keeps the existing category/subcategory/location plus PERSISTENT/SESSION/SERVICE_CYCLE rules.
- `VERIFICATION_PENDING` remains an active match state.
- A new matching report in `VERIFICATION_PENDING` is attached to the existing incident and returns `needs_reopen_review=True`.
- The recurrence layer does **not** silently reopen the incident. Reopening remains an explicit lifecycle action through `reopen_incident()`.
- Lifecycle status strings are centralized as constants for the main transitions.
- Resolution clears any stale verification timestamp.
- Reopening clears verification and increments `reopened_count`.

## 2. Domain/input validation

**Files changed:** `decision_engine/categories.py`, `decision_engine/models.py`, `decision_engine/workload.py`, `decision_engine/engine.py`, `decision_engine/responsibility.py`

- Added category/subcategory validation helpers.
- `Report` validates required IDs, description, location, timestamp, category and subcategory.
- `Incident` validates IDs, timestamps, status, report IDs and reopen count.
- `Resource` validates identifiers/text and rejects negative assigned hours. Zero/negative capacity is still checked when workload is calculated so the existing API behavior remains compatible.
- `DecisionInput` validates its top-level types, positive incident ID, positive required hours, and collection contents.
- Responsibility now validates the category against the defined campus categories.

## 3. Stable decision output / backend contract

**File changed:** `decision_engine/engine.py`

- `DecisionInput` remains the preferred structured entry point.
- `DecisionResult` now exposes:
  - `incident`
  - `is_new_incident`
  - `priority`
  - `responsibility`
  - `assignment`
  - `escalation`
  - `recurrence`
  - `sla_violated`
  - `explanation`
- Added `DecisionResult.to_dict()` using dataclass conversion so the backend has a predictable serialization boundary.
- The old `process_incident(...)` wrapper remains only for backward compatibility.

## 4. Workload + assignment integration

**Files changed:** `decision_engine/workload.py`, `decision_engine/assignment.py`

- Assignment policy remains intentionally simple: eligible department -> enough remaining capacity -> lowest workload ratio.
- No automatic mutation of `assigned_hours` was added; the backend/database remains the source of truth for current assignments.
- `AssignmentResult` now exposes required hours, selected workload ratio, workload status and remaining capacity when an assignment succeeds.
- Failed assignments still produce a clear reason for escalation.

## 5. SLA + escalation

**File changed:** `decision_engine/escalation.py`

- SLA violation is calculated from `sla_deadline` plus a resolution/reference timestamp rather than being the primary source of truth.
- Current-time fallback respects the timezone awareness of the deadline.
- Mixed aware/naive timestamps are rejected instead of being compared unpredictably.
- Existing escalation policy is preserved: CRITICAL -> SUPER_ADMIN; failed assignment/resource constraints/repeated reopening/SLA violation -> DEPARTMENT_HEAD.

## 6. Integration tests

**File added:** `decision_engine/tests/test_hardening.py`

New tests cover:
- verification-pending recurrence requiring reopen review without auto-reopening
- explicit reopening behavior
- category/subcategory/model validation
- negative resource workload input
- zero-capacity workload handling
- assignment workload metadata
- timezone-safe SLA comparisons
- stable structured decision output and explanation

## Deliberately not added

The engine does not yet include semantic duplicate detection, NLP classification, evidence extraction, ML responsibility prediction, LLM orchestration, advanced capability matching, analytics, deployment infrastructure, timetable auto-detection, mobile/CCTV/IoT integrations, or performance optimization.

Those belong after this deterministic core is frozen and tested.

## Verification

Test command:

```bash
pytest -q
```

Result for this package: **119 passed**.
