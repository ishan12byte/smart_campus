from typing import Any

from .base import AIComponent
from .schemas import AIResult


class AIIntelligencePipeline:
    """
    Coordinates AI components.

    This class collects AI recommendations.
    It does not replace deterministic Decision Engine logic.
    """

    def __init__(self, components: list[AIComponent] | None = None):
        self.components = components or []

    def add_component(self, component: AIComponent) -> None:
        self.components.append(component)

    def process(self, data: dict[str, Any]) -> AIResult:
        all_candidates = []
        all_recommendations = []

        model_names = []
        model_versions = []
        fallback_used = False

        for component in self.components:
            result = component.predict(data)

            all_candidates.extend(result.candidates)
            all_recommendations.extend(result.recommendations)

            if result.model_name:
                model_names.append(result.model_name)

            if result.model_version:
                model_versions.append(result.model_version)

            fallback_used = fallback_used or result.fallback_used

        return AIResult(
            candidates=tuple(all_candidates),
            recommendations=tuple(all_recommendations),
            model_name=",".join(model_names) if model_names else None,
            model_version=",".join(model_versions) if model_versions else None,
            fallback_used=fallback_used,
        )