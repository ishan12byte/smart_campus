RESPONSIBILITY_STATUSES = {
    "PENDING_REVIEW",
    "DEPARTMENT_FAILURE",
    "USER_CAUSED",
    "INFRASTRUCTURE_FAILURE",
    "EXTERNAL_CAUSE",
    "RESOURCE_CONSTRAINT",
    "PROCESS_FAILURE",
    "SHARED_RESPONSIBILITY",
    "NOT_APPLICABLE",
}


def create_result(status: str, confidence: float, reason: str) -> dict:
    if status not in RESPONSIBILITY_STATUSES:
        raise ValueError(f"Invalid responsibility status: {status}")

    if not 0.0 <= confidence <= 1.0:
        raise ValueError("Confidence must be between 0 and 1.")

    return {
        "status": status,
        "confidence": confidence,
        "reason": reason,
    }


def determine_responsibility(
    category: str,
    evidence_available: bool = False,
    department_expected_to_handle: bool = True,
    service_was_provided: bool | None = None,
    user_caused: bool = False,
    infrastructure_failed: bool = False,
    external_cause: bool = False,
    resource_constraint: bool = False,
    process_failed: bool = False,
) -> dict:
    if category is None or not isinstance(category, str) or not category.strip():
        raise ValueError("Category is required.")

    category = category.upper().strip()

    signals: list[str] = []

    if external_cause:
        signals.append("EXTERNAL_CAUSE")

    if user_caused:
        signals.append("USER_CAUSED")

    if infrastructure_failed:
        signals.append("INFRASTRUCTURE_FAILURE")

    if resource_constraint:
        signals.append("RESOURCE_CONSTRAINT")

    if process_failed:
        signals.append("PROCESS_FAILURE")

    if department_expected_to_handle and service_was_provided is False:
        signals.append("DEPARTMENT_FAILURE")

    if len(signals) > 1:
        return create_result(
            "SHARED_RESPONSIBILITY",
            0.60,
            "Multiple responsibility signals require human review.",
        )

    if len(signals) == 1:
        status = signals[0]

        if status == "EXTERNAL_CAUSE":
            confidence = 0.90
            reason = "The incident is attributed to an external cause."
        elif status == "USER_CAUSED":
            confidence = 0.90
            reason = "Available evidence indicates that the incident was caused by a user."
        elif status == "INFRASTRUCTURE_FAILURE":
            confidence = 0.90
            reason = "The incident is associated with a failure of physical or technical infrastructure."
        elif status == "RESOURCE_CONSTRAINT":
            confidence = 0.85
            reason = "The incident is associated with an identified resource constraint."
        elif status == "PROCESS_FAILURE":
            confidence = 0.85
            reason = "The incident appears to have resulted from a failure in an institutional process."
        else:
            confidence = 0.85
            reason = (
                "The responsible department was expected to provide the service, "
                "but available evidence indicates that it was not provided."
            )

        return create_result(status, confidence, reason)

    if not evidence_available:
        return create_result(
            "PENDING_REVIEW",
            0.40,
            "There is insufficient evidence to determine responsibility automatically.",
        )

    return create_result(
        "PENDING_REVIEW",
        0.40,
        "Evidence is available, but no responsibility signal was identified automatically.",
    )
