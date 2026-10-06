
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from ai.base import AIComponent
from ai.schemas import AICandidate, AIResult


class SemanticIncidentMatcher(AIComponent):
    """
    Baseline semantic matcher using TF-IDF and cosine similarity.

    This component only proposes related incidents.
    It does not merge reports, assign responsibility,
    or make final recurrence decisions.
    """

    def __init__(self, threshold: float = 0.25):
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("threshold must be between 0 and 1")

        self.threshold = threshold
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
        )

    @property
    def name(self) -> str:
        return "semantic_incident_matcher"

    @property
    def version(self) -> str:
        return "1.0.0"

    def predict(self, data: dict[str, Any]) -> AIResult:
        query = data.get("query_incident")
        candidates = data.get("candidate_incidents", [])

        if not isinstance(query, dict):
            raise ValueError("query_incident must be a dictionary")

        if not isinstance(candidates, list):
            raise ValueError("candidate_incidents must be a list")

        query_id = query.get("incident_id")
        query_text = str(query.get("description", "")).strip()

        if not query_text:
            raise ValueError("query incident description cannot be empty")

        valid_candidates = []

        for candidate in candidates:
            if not isinstance(candidate, dict):
                continue

            candidate_id = candidate.get("incident_id")
            candidate_text = str(
                candidate.get("description", "")
            ).strip()

            if not candidate_id or not candidate_text:
                continue

            if query_id is not None and candidate_id == query_id:
                continue

            valid_candidates.append(
                (candidate_id, candidate_text)
            )

        if not valid_candidates:
            return AIResult(
                candidates=(),
                recommendations=(),
                model_name=self.name,
                model_version=self.version,
                fallback_used=False,
            )

        texts = [query_text] + [
            text for _, text in valid_candidates
        ]

        matrix = self.vectorizer.fit_transform(texts)

        scores = cosine_similarity(
            matrix[0:1],
            matrix[1:]
        )[0]

        matches = []

        for (candidate_id, candidate_text), score in zip(
            valid_candidates, scores
        ):
            score = float(score)

            if score >= self.threshold:
                matches.append(
                    AICandidate(
                        incident_id=str(candidate_id),
                        score=score,
                        reason=(
                            "Description similarity exceeds "
                            f"threshold {self.threshold:.2f}"
                        ),
                    )
                )

        matches.sort(
            key=lambda item: item.score,
            reverse=True,
        )

        return AIResult(
            candidates=tuple(matches),
            recommendations=(),
            model_name=self.name,
            model_version=self.version,
            fallback_used=False,
        )
