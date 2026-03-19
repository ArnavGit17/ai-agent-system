"""Basic smoke tests for models and RAG engine."""

import pytest
from models import (
    SubTask,
    PlannerOutput,
    CriticEvaluation,
    ToolName,
    QueryRequest,
)


def test_subtask_defaults():
    st = SubTask(description="test")
    assert st.status.value == "pending"
    assert st.tools_needed == []
    assert len(st.id) == 8


def test_planner_output():
    plan = PlannerOutput(
        original_query="What is AI?",
        rewritten_query="Explain artificial intelligence",
        subtasks=[SubTask(description="Define AI", tools_needed=[ToolName.WEB_SEARCH])],
        reasoning="Simple factual query",
    )
    assert len(plan.subtasks) == 1
    assert plan.subtasks[0].tools_needed[0] == ToolName.WEB_SEARCH


def test_critic_scores_clamped():
    ev = CriticEvaluation(
        relevance_score=0.9,
        accuracy_score=0.8,
        completeness_score=0.7,
        overall_score=0.8,
        feedback="Good",
        improvements=[],
        approved=True,
    )
    assert 0 <= ev.overall_score <= 1


def test_query_request_validation():
    req = QueryRequest(query="hello")
    assert req.use_rag is True
    assert req.use_web is True

    with pytest.raises(Exception):
        QueryRequest(query="")
