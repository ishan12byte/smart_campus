# Semantic Incident Matching Dataset

## Purpose
Prepare labeled incident pairs for evaluating semantic similarity
and related-incident retrieval.

## Unit of data
One row represents a pair of incidents.

## Labels
1  = MATCH
0  = NO_MATCH
-1 = REVIEW

## Important distinction
Semantic similarity does not automatically establish recurrence,
responsibility, or permission to merge incidents.

## Labeling policy
- Labels must be reviewed by a human.
- Ambiguous pairs remain REVIEW.
- Synthetic examples must be marked as synthetic.
- Personal information must be removed or anonymized.
- Training, validation, and test data must be separated
  before model evaluation.

## Future use
The dataset will support evaluation of semantic incident matching
and may later contribute to a human-confirmed incident history.