
import csv
import time
from pathlib import Path

from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from ai.components.semantic_matcher import SemanticIncidentMatcher
from ai.components.embedding_matcher import EmbeddingIncidentMatcher


DATA_DIR = Path(__file__).resolve().parent

INCIDENTS_FILE = DATA_DIR / "incidents.csv"
PAIRS_FILE = DATA_DIR / "semantic_pairs.csv"

SUMMARY_FILE = DATA_DIR / "matcher_comparison.csv"
DETAIL_FILE = DATA_DIR / "pair_analysis.csv"

THRESHOLDS = [
    0.05, 0.10, 0.15, 0.20, 0.25,
    0.30, 0.35, 0.40, 0.45, 0.50,
    0.55, 0.60, 0.65, 0.70, 0.75,
    0.80, 0.85, 0.90,
]


def normalize_label(value):
    value = str(value).strip().upper()

    if value in {"MATCH", "1", "TRUE", "YES", "DUPLICATE"}:
        return 1

    if value in {"NO_MATCH", "NO MATCH", "0", "FALSE", "NO", "DISTINCT"}:
        return 0

    if value in {"REVIEW", "-1", "UNCERTAIN"}:
        return None

    raise ValueError(f"Unknown pair label: {value}")


def load_data():
    incidents = {}

    with open(
        INCIDENTS_FILE,
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as f:
        for row in csv.DictReader(f):
            incident_id = row["incident_id"]

            if incident_id in incidents:
                raise ValueError(
                    f"Duplicate incident ID: {incident_id}"
                )

            incidents[incident_id] = row

    pairs = []
    seen_pairs = set()
    excluded_review = 0

    with open(
        PAIRS_FILE,
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as f:
        for row in csv.DictReader(f):

            label = normalize_label(row["match_label"])

            # Exclude REVIEW examples from quantitative evaluation.
            if label is None:
                excluded_review += 1
                continue

            incident_a_id = row["incident_id_a"]
            incident_b_id = row["incident_id_b"]

            if incident_a_id not in incidents:
                raise ValueError(
                    f"Unknown incident ID: {incident_a_id}"
                )

            if incident_b_id not in incidents:
                raise ValueError(
                    f"Unknown incident ID: {incident_b_id}"
                )

            # Detect duplicate and reversed pairs.
            pair_key = tuple(
                sorted([incident_a_id, incident_b_id])
            )

            if pair_key in seen_pairs:
                raise ValueError(
                    f"Duplicate or reversed pair found: "
                    f"{incident_a_id}, {incident_b_id}"
                )

            seen_pairs.add(pair_key)

            pairs.append({
                "incident_a_id": incident_a_id,
                "incident_b_id": incident_b_id,
                "incident_a": incidents[incident_a_id],
                "incident_b": incidents[incident_b_id],
                "true_label": label,
            })

    print(f"Excluded REVIEW pairs: {excluded_review}")

    return incidents, pairs


def get_pair_score(matcher, incident_a, incident_b):
    """
    Run one incident pair through a matcher.

    A zero threshold allows nonnegative similarity scores to be
    returned. Scores below zero are treated as zero for this
    threshold-based evaluation.
    """

    result = matcher.predict({
        "query_incident": incident_a,
        "candidate_incidents": [incident_b],
    })

    for candidate in result.candidates:
        if candidate.incident_id == incident_b["incident_id"]:
            return float(candidate.score)

    return 0.0


def collect_scores(pairs):
    """
    Compute scores once per pair for each model.

    Model initialization and embedding inference are excluded from
    per-pair latency measurements.
    """

    tfidf = SemanticIncidentMatcher(threshold=0.0)
    embedding = EmbeddingIncidentMatcher(threshold=0.0)

    records = []

    print("\nScoring labeled pairs...")

    for index, pair in enumerate(pairs, start=1):

        a = pair["incident_a"]
        b = pair["incident_b"]

        start = time.perf_counter()
        tfidf_score = get_pair_score(tfidf, a, b)
        tfidf_ms = (time.perf_counter() - start) * 1000

        start = time.perf_counter()
        embedding_score = get_pair_score(embedding, a, b)
        embedding_ms = (time.perf_counter() - start) * 1000

        records.append({
            "incident_a_id": pair["incident_a_id"],
            "incident_b_id": pair["incident_b_id"],
            "true_label": pair["true_label"],
            "tfidf_score": tfidf_score,
            "embedding_score": embedding_score,
            "tfidf_latency_ms": tfidf_ms,
            "embedding_latency_ms": embedding_ms,
        })

        print(
            f"[{index}/{len(pairs)}] "
            f"{pair['incident_a_id']} vs "
            f"{pair['incident_b_id']} "
            f"| TF-IDF={tfidf_score:.4f} "
            f"| Embedding={embedding_score:.4f}"
        )

    return records


def calculate_metrics(y_true, scores, threshold):

    y_pred = [
        1 if score >= threshold else 0
        for score in scores
    ]

    tn, fp, fn, tp = confusion_matrix(
        y_true,
        y_pred,
        labels=[0, 1],
    ).ravel()

    return {
        "threshold": threshold,
        "precision": precision_score(
            y_true,
            y_pred,
            zero_division=0,
        ),
        "recall": recall_score(
            y_true,
            y_pred,
            zero_division=0,
        ),
        "f1": f1_score(
            y_true,
            y_pred,
            zero_division=0,
        ),
        "accuracy": accuracy_score(y_true, y_pred),
        "true_positives": int(tp),
        "false_positives": int(fp),
        "true_negatives": int(tn),
        "false_negatives": int(fn),
    }


def write_csv(path, rows):

    if not rows:
        print(f"Warning: no rows to write to {path}")
        return

    with open(
        path,
        "w",
        encoding="utf-8",
        newline="",
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=list(rows[0].keys()),
        )

        writer.writeheader()
        writer.writerows(rows)


def main():

    print("=" * 75)
    print("TF-IDF VS SENTENCE TRANSFORMER — COMPARATIVE EVALUATION")
    print("=" * 75)

    incidents, pairs = load_data()

    y_true = [pair["true_label"] for pair in pairs]

    if not pairs:
        raise ValueError(
            "No evaluable pairs found. Check semantic_pairs.csv."
        )

    if any(label not in (0, 1) for label in y_true):
        raise ValueError(
            "Evaluation labels must contain only 0 and 1."
        )

    print(f"\nIncident records: {len(incidents)}")
    print(f"Evaluated pairs:  {len(pairs)}")
    print(f"Positive pairs:   {sum(y_true)}")
    print(f"Negative pairs:   {len(y_true) - sum(y_true)}")

    records = collect_scores(pairs)

    model_scores = {
        "TF-IDF": [
            record["tfidf_score"]
            for record in records
        ],
        "Sentence Transformer": [
            record["embedding_score"]
            for record in records
        ],
    }

    summary_rows = []

    for model_name, scores in model_scores.items():

        for threshold in THRESHOLDS:

            metrics = calculate_metrics(
                y_true,
                scores,
                threshold,
            )

            summary_rows.append({
                "model": model_name,
                **metrics,
            })

    # Find best F1 threshold for each model.
    best_thresholds = {}

    for model_name in model_scores:

        model_rows = [
            row
            for row in summary_rows
            if row["model"] == model_name
        ]

        best = max(
            model_rows,
            key=lambda row: (
                row["f1"],
                row["precision"],
                row["threshold"],
            ),
        )

        best_thresholds[model_name] = best["threshold"]

    # Generate pair-level predictions at best F1 thresholds.
    detailed_rows = []

    for record in records:

        row = dict(record)

        for model_name, score_key in [
            ("TF-IDF", "tfidf_score"),
            ("Sentence Transformer", "embedding_score"),
        ]:

            threshold = best_thresholds[model_name]
            score = record[score_key]

            predicted = int(score >= threshold)
            actual = record["true_label"]

            if actual == 1 and predicted == 1:
                error_type = "TP"

            elif actual == 0 and predicted == 1:
                error_type = "FP"

            elif actual == 0 and predicted == 0:
                error_type = "TN"

            else:
                error_type = "FN"

            prefix = (
                "tfidf"
                if model_name == "TF-IDF"
                else "embedding"
            )

            row[f"{prefix}_threshold"] = threshold
            row[f"{prefix}_predicted"] = predicted
            row[f"{prefix}_error_type"] = error_type

        detailed_rows.append(row)

    write_csv(SUMMARY_FILE, summary_rows)
    write_csv(DETAIL_FILE, detailed_rows)

    print("\nBEST THRESHOLD BY F1")
    print("-" * 75)

    for model_name in model_scores:

        best = max(
            [
                row
                for row in summary_rows
                if row["model"] == model_name
            ],
            key=lambda row: (
                row["f1"],
                row["precision"],
                row["threshold"],
            ),
        )

        print(f"\n{model_name}")
        print(f"Threshold:       {best['threshold']:.2f}")
        print(f"Precision:       {best['precision']:.3f}")
        print(f"Recall:          {best['recall']:.3f}")
        print(f"F1:              {best['f1']:.3f}")
        print(f"Accuracy:        {best['accuracy']:.3f}")
        print(f"True positives:  {best['true_positives']}")
        print(f"False positives: {best['false_positives']}")
        print(f"True negatives:  {best['true_negatives']}")
        print(f"False negatives: {best['false_negatives']}")

    print("\nFILES GENERATED")
    print(f"Summary: {SUMMARY_FILE}")
    print(f"Details: {DETAIL_FILE}")

    print(
        "\nNOTE: Results use a small synthetic dataset. "
        "Thresholds are exploratory, not production settings."
    )


if __name__ == "__main__":
    main()
