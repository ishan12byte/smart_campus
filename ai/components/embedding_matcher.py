
from typing import Any

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from ai.base import AIComponent
from ai.schemas import AICandidate, AIResult


class EmbeddingIncidentMatcher(AIComponent):
    """
    Semantic incident matcher using sentence embeddings.

    Responsibilities:
    - Encode incident descriptions into dense vectors.
    - Compare semantic similarity using cosine similarity.
    - Return candidate incidents above a configurable threshold.

    This component does NOT:
    - Merge incidents.
    - Determine responsibility.
    - Assign departments.
    - Make final operational decisions.
    """

    def __init__(
        self,
        threshold: float = 0.50,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    ):
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("threshold must be between 0.0 and 1.0")

        self.threshold = threshold
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    @property
    def name(self) -> str:
        return "embedding_incident_matcher"

    @property
    def version(self) -> str:
        return "1.0.0"

    def predict(self, data: dict[str, Any]) -> AIResult:
        query = data.get("query_incident")
        candidates = data.get("candidate_incidents", [])

        if not isinstance(query, dict):
            raise ValueError("query_incident must be a dictionary")

        query_id = query.get("incident_id")
        query_description = str(query.get("description", "")).strip()

        if not query_description:
            raise ValueError("query incident description cannot be empty")

        if not isinstance(candidates, list):
            raise ValueError("candidate_incidents must be a list")

        valid_candidates = []

        for candidate in candidates:
            if not isinstance(candidate, dict):
                continue

            candidate_id = candidate.get("incident_id")
            description = str(candidate.get("description", "")).strip()

            if not candidate_id or candidate_id == query_id:
                continue

            if not description:
                continue

            valid_candidates.append((candidate, description))

        if not valid_candidates:
            return AIResult(
                candidates=[],
                recommendations=[],
                model_name=self.model_name,
                model_version=self.version,
                fallback_used=False,
            )

        descriptions = [query_description]
        descriptions.extend(
            description for _, description in valid_candidates
        )

        embeddings = self.model.encode(
            descriptions,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        query_embedding = embeddings[0].reshape(1, -1)
        candidate_embeddings = embeddings[1:]

        scores = cosine_similarity(
            query_embedding,
            candidate_embeddings,
        )[0]

        results = []

        for (candidate, description), score in zip(
            valid_candidates, scores
        ):
            score = float(score)

            if score < self.threshold:
                continue

            results.append(
                AICandidate(
                    incident_id=str(candidate["incident_id"]),
                    score=score,
                    reason=(
                        "Semantically similar incident description "
                        "identified using sentence embeddings."
                    ),
                )
            )

        results.sort(key=lambda item: item.score, reverse=True)

        return AIResult(
            candidates=results,
            recommendations=[],
            model_name=self.model_name,
            model_version=self.version,
            fallback_used=False,
        )
