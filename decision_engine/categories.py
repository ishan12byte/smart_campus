CATEGORIES = {
    "EXAMINATION": {
        "name": "Examination",
        "subcategories": [
            "HALL_ALLOCATION",
            "TIMETABLE_ISSUE",
            "INVIGILATOR_UNAVAILABLE",
            "SEATING_ISSUE",
            "EXAM_RESOURCE_ISSUE",
        ],
    },
    "ACADEMIC_ADMINISTRATION": {
        "name": "Academic Administration",
        "subcategories": [
            "NO_TEACHER_ASSIGNED",
            "NO_SUBSTITUTE",
            "CLASS_CONFLICT",
            "FACULTY_TIMETABLE_ISSUE",
            "OTHER_ACADEMIC_ISSUE",
        ],
    },
    "MAINTENANCE": {
        "name": "Maintenance",
        "subcategories": [
            "ELECTRICAL",
            "PLUMBING",
            "FURNITURE",
            "CLASSROOM_EQUIPMENT",
            "INFRASTRUCTURE_DAMAGE",
        ],
    },
    "SANITATION": {
        "name": "Sanitation",
        "subcategories": [
            "CLEANING",
            "WASTE",
            "WASHROOM",
            "WATER_SANITATION",
        ],
    },
    "IT": {
        "name": "IT",
        "subcategories": [
            "NETWORK",
            "COMPUTER",
            "PROJECTOR",
            "SMART_CLASSROOM",
            "OTHER_IT_ISSUE",
        ],
    },
    "SECURITY": {
        "name": "Security",
        "subcategories": [
            "SUSPICIOUS_ACTIVITY",
            "UNAUTHORIZED_ACCESS",
            "SAFETY_HAZARD",
            "SECURITY_EQUIPMENT",
        ],
    },
    "ADMINISTRATION": {
        "name": "Administration",
        "subcategories": [
            "ADMINISTRATIVE_SERVICE",
            "FACILITY_RESOURCE",
            "OTHER_ADMINISTRATIVE_ISSUE",
        ],
    },
}


def normalize(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required.")
    return value.strip().upper()


def validate_category(category: str) -> str:
    normalized = normalize(category, "Category")
    if normalized not in CATEGORIES:
        raise ValueError(f"Invalid category: {category}")
    return normalized


def validate_subcategory(category: str, subcategory: str) -> str:
    normalized_category = validate_category(category)
    normalized_subcategory = normalize(subcategory, "Subcategory")
    if normalized_subcategory not in CATEGORIES[normalized_category]["subcategories"]:
        raise ValueError(
            f"Invalid subcategory '{subcategory}' for category '{category}'."
        )
    return normalized_subcategory
