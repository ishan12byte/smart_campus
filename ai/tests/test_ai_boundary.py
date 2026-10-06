from ai.base import AIComponent
from ai.pipeline import AIIntelligencePipeline
from ai.schemas import (
    AICandidate,
    AIRecommendation,
    AIResult,
)


class DummyAI(AIComponent):

    @property
    def name(self) -> str:
        return "dummy"

    @property
    def version(self) -> str:
        return "1.0"

    def predict(self, data):
        return AIResult(
            candidates=(
                AICandidate(
                    incident_id=10,
                    score=0.91,
                    reason="Semantically similar",
                ),
            ),
            recommendations=(
                AIRecommendation(
                    recommendation_type="RELATED_INCIDENT",
                    confidence=0.91,
                    reason="High semantic similarity",
                ),
            ),
            model_name=self.name,
            model_version=self.version,
        )


def test_ai_component_returns_structured_result():
    component = DummyAI()

    result = component.predict({
        "description": "Projector is not working"
    })

    assert isinstance(result, AIResult)
    assert len(result.candidates) == 1
    assert result.candidates[0].incident_id == 10
    assert result.candidates[0].score == 0.91


def test_ai_pipeline_collects_component_results():
    pipeline = AIIntelligencePipeline([
        DummyAI()
    ])

    result = pipeline.process({
        "description": "Projector is not working"
    })

    assert len(result.candidates) == 1
    assert len(result.recommendations) == 1
    assert result.model_name == "dummy"
    assert result.model_version == "1.0"


def test_ai_pipeline_does_not_modify_input():
    data = {
        "description": "Projector is not working"
    }

    original = data.copy()

    pipeline = AIIntelligencePipeline([
        DummyAI()
    ])

    pipeline.process(data)

    assert data == original