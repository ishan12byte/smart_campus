import csv
from pathlib import Path

from ai.components.recurrence_analyzer import RecurrenceAnalyzer


DATA_DIR = Path(__file__).resolve().parent
INCIDENTS_FILE = DATA_DIR / "incidents.csv"


def load_incidents():
    with open(
        INCIDENTS_FILE,
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as f:
        return list(csv.DictReader(f))


def main():
    print("=" * 70)
    print("RECURRENCE & PATTERN INTELLIGENCE")
    print("=" * 70)

    incidents = load_incidents()

    if not incidents:
        raise ValueError("No incidents found in incidents.csv")

    analyzer = RecurrenceAnalyzer(
        minimum_occurrences=3,
        time_window_days=30,
    )

    print(f"\nLoaded incidents: {len(incidents)}")

    detected = 0

    for query in incidents:
        result = analyzer.analyze(
            query_incident=query,
            historical_incidents=incidents,
        )

        if result.status == "RECURRENCE_DETECTED":
            detected += 1

            print("\n" + "-" * 70)
            print(f"Incident: {result.incident_id}")
            print(f"Status: {result.status}")
            print(f"Occurrences: {result.occurrence_count}")
            print(
                f"Matching incidents: "
                f"{', '.join(result.matching_incident_ids)}"
            )
            print(f"Category: {result.category}")
            print(f"Subcategory: {result.subcategory}")
            print(f"Location: {result.location}")
            print(f"Service cycle: {result.service_cycle_id}")
            print(f"Reason: {result.reason}")

    print("\n" + "=" * 70)
    print(f"Recurring patterns detected: {detected}")
    print("=" * 70)


if __name__ == "__main__":
    main()