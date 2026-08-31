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

    if category is None or not category.strip():
        raise ValueError("Category is required.")

    category = category.upper().strip()

    if external_cause:
        return create_result(
            "EXTERNAL_CAUSE",
            0.90,
            "The incident is attributed to an external cause."
        )

    if user_caused:
        return create_result(
            "USER_CAUSED",
            0.90,
            "Available evidence indicates that the incident was caused by a user."
        )

    if infrastructure_failed:
        return create_result(
            "INFRASTRUCTURE_FAILURE",
            0.90,
            "The incident is associated with a failure of physical or technical infrastructure."
        )

    if resource_constraint:
        return create_result(
            "RESOURCE_CONSTRAINT",
            0.85,
            "The incident is associated with an identified resource constraint."
        )

    if process_failed:
        return create_result(
            "PROCESS_FAILURE",
            0.85,
            "The incident appears to have resulted from a failure in an institutional process."
        )

    if (
        department_expected_to_handle
        and service_was_provided is False
    ):
        return create_result(
            "DEPARTMENT_FAILURE",
            0.85,
            "The responsible department was expected to provide the service, but available evidence indicates that it was not provided."
        )

    return create_result(
        "PENDING_REVIEW",
        0.40,
        "There is insufficient evidence to determine responsibility automatically."
    )