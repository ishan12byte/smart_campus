from abc import ABC, abstractmethod
from typing import Any

from .schemas import AIResult


class AIComponent(ABC):
    """
    Base interface for AI components.

    AI components generate recommendations/candidates only.
    They must not directly mutate Decision Engine state.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the component name."""
        raise NotImplementedError

    @property
    @abstractmethod
    def version(self) -> str:
        """Return the component version."""
        raise NotImplementedError

    @abstractmethod
    def predict(self, data: dict[str, Any]) -> AIResult:
        """
        Generate an AI result from input data.

        Implementations must not mutate the incident,
        database, or deterministic Decision Engine state.
        """
        raise NotImplementedError