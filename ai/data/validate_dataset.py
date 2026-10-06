
import csv
import sys
from pathlib import Path
from collections import Counter

DATA_DIR = Path(__file__).resolve().parent

INCIDENTS_FILE = DATA_DIR / "incidents.csv"
PAIRS_FILE = DATA_DIR / "semantic_pairs.csv"

INCIDENT_REQUIRED = {
    "incident_id",
    "description",
    "category",
    "subcategory",
    "location",
    "reported_at",
    "source_type",
}

PAIR_REQUIRED = {
    "incident_id_a",
    "incident_id_b",
    "match_label",
    "match_type",
    "reviewer_id",
    "review_notes",
}

VALID_LABELS = {"1", "0", "-1"}

VALID_MATCH_TYPES = {
    "SAME_UNDERLYING_ISSUE",
    "MEANINGFUL_CONTINUATION",
    "DIFFERENT_ISSUE",
    "INSUFFICIENT_EVIDENCE",
}

LABEL_TYPE_RULES = {
    "1": {"SAME_UNDERLYING_ISSUE", "MEANINGFUL_CONTINUATION"},
    "0": {"DIFFERENT_ISSUE"},
    "-1": {"INSUFFICIENT_EVIDENCE"},
}


def read_csv(path):
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

    with path.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValueError(f"{path.name} has no header row")

        return reader.fieldnames, list(reader)


def validate_required_columns(filename, headers, required):
    missing = required - set(headers)

    if missing:
        print(f"[ERROR] {filename}: missing columns: {sorted(missing)}")
        return False

    return True


def validate_dataset():
    errors = []
    warnings = []

    print("=" * 60)
    print("SEMANTIC INCIDENT DATASET VALIDATOR")
    print("=" * 60)

    try:
        incident_headers, incidents = read_csv(INCIDENTS_FILE)
        pair_headers, pairs = read_csv(PAIRS_FILE)
    except (FileNotFoundError, ValueError) as exc:
        print(f"[ERROR] {exc}")
        return False

    if not validate_required_columns(
        INCIDENTS_FILE.name, incident_headers, INCIDENT_REQUIRED
    ):
        return False

    if not validate_required_columns(
        PAIRS_FILE.name, pair_headers, PAIR_REQUIRED
    ):
        return False

    # --------------------------------------------------
    # Validate incident records
    # --------------------------------------------------

    incident_ids = set()

    for row_number, row in enumerate(incidents, start=2):
        incident_id = row["incident_id"].strip()

        if not incident_id:
            errors.append(
                f"incidents.csv row {row_number}: missing incident_id"
            )
            continue

        if incident_id in incident_ids:
            errors.append(
                f"incidents.csv row {row_number}: duplicate ID {incident_id}"
            )

        incident_ids.add(incident_id)

        for field in INCIDENT_REQUIRED:
            if not row[field].strip():
                errors.append(
                    f"incidents.csv row {row_number}: "
                    f"missing value for {field}"
                )

        if row["source_type"].strip().lower() not in {
            "synthetic",
            "real",
        }:
            warnings.append(
                f"incidents.csv row {row_number}: "
                f"unrecognized source_type"
            )

    # --------------------------------------------------
    # Validate labeled pairs
    # --------------------------------------------------

    seen_pairs = set()
    label_counts = Counter()

    for row_number, row in enumerate(pairs, start=2):
        id_a = row["incident_id_a"].strip()
        id_b = row["incident_id_b"].strip()
        label = row["match_label"].strip()
        match_type = row["match_type"].strip()

        for field in PAIR_REQUIRED:
            if not row[field].strip():
                errors.append(
                    f"semantic_pairs.csv row {row_number}: "
                    f"missing value for {field}"
                )

        if id_a not in incident_ids:
            errors.append(
                f"semantic_pairs.csv row {row_number}: "
                f"unknown incident_id_a {id_a}"
            )

        if id_b not in incident_ids:
            errors.append(
                f"semantic_pairs.csv row {row_number}: "
                f"unknown incident_id_b {id_b}"
            )

        if id_a == id_b and id_a:
            errors.append(
                f"semantic_pairs.csv row {row_number}: "
                f"self-pair detected ({id_a})"
            )

        # Treat A-B and B-A as the same pair.
        canonical_pair = tuple(sorted((id_a, id_b)))

        if canonical_pair in seen_pairs:
            errors.append(
                f"semantic_pairs.csv row {row_number}: "
                f"duplicate or reversed pair {id_a}, {id_b}"
            )

        seen_pairs.add(canonical_pair)

        if label not in VALID_LABELS:
            errors.append(
                f"semantic_pairs.csv row {row_number}: "
                f"invalid match_label {label}"
            )
            continue

        label_counts[label] += 1

        if match_type not in VALID_MATCH_TYPES:
            errors.append(
                f"semantic_pairs.csv row {row_number}: "
                f"invalid match_type {match_type}"
            )
        elif match_type not in LABEL_TYPE_RULES[label]:
            errors.append(
                f"semantic_pairs.csv row {row_number}: "
                f"label {label} conflicts with match_type {match_type}"
            )

    # --------------------------------------------------
    # Report
    # --------------------------------------------------

    print(f"\nIncident records: {len(incidents)}")
    print(f"Labeled pairs:    {len(pairs)}")

    print("\nLabel distribution:")
    print(f"  MATCH (1):      {label_counts['1']}")
    print(f"  NO_MATCH (0):   {label_counts['0']}")
    print(f"  REVIEW (-1):    {label_counts['-1']}")

    if warnings:
        print("\nWARNINGS:")
        for warning in warnings:
            print(f"  [WARN] {warning}")

    if errors:
        print(f"\nVALIDATION FAILED: {len(errors)} error(s)")
        for error in errors:
            print(f"  [ERROR] {error}")

        return False

    print("\nVALIDATION PASSED")
    print("No structural or labeling errors detected.")

    if label_counts["1"] == 0 or label_counts["0"] == 0:
        print(
            "[WARN] Dataset needs both positive and negative "
            "examples before supervised training."
        )

    if label_counts["-1"] > 0:
        print(
            "[INFO] REVIEW pairs are retained for human review "
            "and must be excluded from supervised training metrics."
        )

    return True


if __name__ == "__main__":
    success = validate_dataset()
    sys.exit(0 if success else 1)