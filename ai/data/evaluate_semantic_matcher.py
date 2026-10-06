
import csv
from pathlib import Path

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)

from ai.components.semantic_matcher import SemanticIncidentMatcher


DATA_DIR = Path(__file__).resolve().parent

INCIDENTS_FILE = DATA_DIR / "incidents.csv"
PAIRS_FILE = DATA_DIR / "semantic_pairs.csv"
OUTPUT_FILE = DATA_DIR / "evaluation_results.csv"

# Test a range of thresholds instead of assuming one is optimal.
THRESHOLDS = [
    0.05,
    0.10,
    0.15,
    0.20,
    0.25,
    0.30,
    0.35,
    0.40,
    0.50,
    0.60,
    0.70,
    0.80,
    0.90,
]


def load_csv(path):
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

    with path.open("r", newline="", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


def load_data():
    incidents = load_csv(INCIDENTS_FILE)
    pairs = load_csv(PAIRS_FILE)

    incident_map = {
        row["incident_id"].strip(): row
        for row in incidents
    }

    return incident_map, pairs


def get_similarity_scores(incident_map, pairs):
    """
    Obtain the raw similarity score for each labeled pair.

    A zero-threshold matcher returns all valid candidates,
    allowing us to evaluate different thresholds afterward.
    """

    matcher = SemanticIncidentMatcher(threshold=0.0)

    scores = []
    labels = []
    evaluated_pairs = []

    for row in pairs:
        label = int(row["match_label"])

        # REVIEW examples are not ground-truth labels.
        if label == -1:
            continue

        id_a = row["incident_id_a"].strip()
        id_b = row["incident_id_b"].strip()

        if id_a not in incident_map or id_b not in incident_map:
            raise ValueError(
                f"Unknown incident reference: {id_a}, {id_b}"
            )

        incident_a = incident_map[id_a]
        incident_b = incident_map[id_b]

        result = matcher.predict({
            "query_incident": incident_a,
            "candidate_incidents": [incident_b],
        })

        if result.candidates:
            score = result.candidates[0].score
        else:
            score = 0.0

        scores.append(float(score))
        labels.append(label)
        evaluated_pairs.append((id_a, id_b, label, float(score)))

    return scores, labels, evaluated_pairs


def evaluate_threshold(threshold, scores, labels):
    predictions = [
        1 if score >= threshold else 0
        for score in scores
    ]

    precision = precision_score(
        labels, predictions, zero_division=0
    )

    recall = recall_score(
        labels, predictions, zero_division=0
    )

    f1 = f1_score(
        labels, predictions, zero_division=0
    )

    accuracy = accuracy_score(labels, predictions)

    tn, fp, fn, tp = confusion_matrix(
        labels,
        predictions,
        labels=[0, 1],
    ).ravel()

    return {
        "threshold": threshold,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "accuracy": accuracy,
        "true_positives": int(tp),
        "false_positives": int(fp),
        "true_negatives": int(tn),
        "false_negatives": int(fn),
    }


def main():
    print("=" * 70)
    print("SEMANTIC INCIDENT MATCHER — EVALUATION")
    print("=" * 70)

    incident_map, pairs = load_data()

    scores, labels, evaluated_pairs = get_similarity_scores(
        incident_map, pairs
    )

    if not labels:
        raise ValueError("No labeled pairs available for evaluation.")

    positive_count = sum(labels)
    negative_count = len(labels) - positive_count

    print(f"\nTotal incident records: {len(incident_map)}")
    print(f"Total labeled pairs:    {len(pairs)}")
    print(f"Evaluated pairs:        {len(labels)}")
    print(f"Excluded REVIEW pairs:  {len(pairs) - len(labels)}")
    print(f"Positive examples:      {positive_count}")
    print(f"Negative examples:      {negative_count}")

    if positive_count == 0 or negative_count == 0:
        raise ValueError(
            "Evaluation requires both positive and negative examples."
        )

    results = [
        evaluate_threshold(threshold, scores, labels)
        for threshold in THRESHOLDS
    ]

    print("\nTHRESHOLD COMPARISON")
    print("-" * 90)

    print(
        f"{'Threshold':>10} "
        f"{'Precision':>11} "
        f"{'Recall':>10} "
        f"{'F1':>10} "
        f"{'Accuracy':>11} "
        f"{'FP':>6} "
        f"{'FN':>6}"
    )

    for result in results:
        print(
            f"{result['threshold']:>10.2f} "
            f"{result['precision']:>11.3f} "
            f"{result['recall']:>10.3f} "
            f"{result['f1']:>10.3f} "
            f"{result['accuracy']:>11.3f} "
            f"{result['false_positives']:>6} "
            f"{result['false_negatives']:>6}"
        )

    # Select the threshold with the highest F1.
    # Ties are resolved in favor of higher precision.
    best = max(
        results,
        key=lambda item: (
            item["f1"],
            item["precision"],
            item["threshold"],
        ),
    )

    print("\nBEST THRESHOLD BY F1")
    print("-" * 40)
    print(f"Threshold:       {best['threshold']:.2f}")
    print(f"Precision:       {best['precision']:.3f}")
    print(f"Recall:          {best['recall']:.3f}")
    print(f"F1-score:        {best['f1']:.3f}")
    print(f"Accuracy:        {best['accuracy']:.3f}")
    print(f"False positives: {best['false_positives']}")
    print(f"False negatives: {best['false_negatives']}")

    # Save all threshold results for later comparison.
    fieldnames = list(results[0].keys())

    with OUTPUT_FILE.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"\nResults saved to: {OUTPUT_FILE}")

    print(
        "\nNOTE: These are development metrics on a small, "
        "synthetic dataset. They are not evidence of real-world "
        "campus performance."
    )


if __name__ == "__main__":
    main()
