from decision_engine.responsibility import determine_responsibility


def test_user_caused():
    result = determine_responsibility(
        category="SANITATION",
        user_caused=True,
    )

    assert result["status"] == "USER_CAUSED"


def test_external_cause():
    result = determine_responsibility(
        category="IT",
        external_cause=True,
    )

    assert result["status"] == "EXTERNAL_CAUSE"


def test_infrastructure_failure():
    result = determine_responsibility(
        category="MAINTENANCE",
        infrastructure_failed=True,
    )

    assert result["status"] == "INFRASTRUCTURE_FAILURE"


def test_resource_constraint():
    result = determine_responsibility(
        category="ACADEMIC_ADMINISTRATION",
        resource_constraint=True,
    )

    assert result["status"] == "RESOURCE_CONSTRAINT"


def test_process_failure():
    result = determine_responsibility(
        category="EXAMINATION",
        process_failed=True,
    )

    assert result["status"] == "PROCESS_FAILURE"


def test_department_failure():
    result = determine_responsibility(
        category="SANITATION",
        service_was_provided=False,
    )

    assert result["status"] == "DEPARTMENT_FAILURE"


def test_pending_review():
    result = determine_responsibility(
        category="SANITATION",
    )

    assert result["status"] == "PENDING_REVIEW"