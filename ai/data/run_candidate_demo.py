import csv
from pathlib import Path

from ai.components.candidate_ranker import SemanticCandidateRanker


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


def print_incident(incident):
    print(f"ID:          {incident['incident_id']}")
    print(f"Description: {incident['description']}")

    if incident.get("category"):
        print(f"Category:     {incident['category']}")

    if incident.get("subcategory"):
        print(f"Subcategory:  {incident['subcategory']}")

    if incident.get("location"):
        print(f"Location:     {incident['location']}")


def main():
    print("=" * 70)
    print("SEMANTIC INCIDENT CANDIDATE SEARCH")
    print("=" * 70)

    incidents = load_incidents()

    if not incidents:
        raise ValueError("No incidents found in incidents.csv")

    # Use the first incident as the demonstration query.
    query = incidents[0]

    ranker = SemanticCandidateRanker(
        top_k=5,
    )

    results = ranker.rank(
        query_incident=query,
        historical_incidents=incidents,
    )

    print("\nQUERY INCIDENT")
    print("-" * 70)

    print_incident(query)

    print("\nTOP CANDIDATES")
    print("-" * 70)

    if not results:
        print("No candidate incidents found.")
        return

    for index, candidate in enumerate(results, start=1):

        print(f"\n#{index} {candidate.incident_id}")

        print(
            f"Semantic similarity: {candidate.semantic_score:.4f}"
        )

        print(
            f"Context score:       {candidate.context_score:.4f}"
        )

        print(
            f"Category match:      {candidate.category_match}"
        )

        print(
            f"Subcategory match:   {candidate.subcategory_match}"
        )

        print(
            f"Location match:      {candidate.location_match}"
        )

        print(
            f"Service cycle match: {candidate.service_cycle_match}"
        )

        print(
            f"Location conflict:   {candidate.location_conflict}"
        )

        print(
            f"Decision:            {candidate.decision}"
        )

        print(
            f"Reason:              {candidate.reason}"
        )

    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()