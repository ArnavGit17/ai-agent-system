"""
Pipeline Orchestrator — wires the four agents together into
a single async pipeline that processes a user query end-to-end.
"""

from __future__ import annotations

import time
from typing import AsyncIterator

from loguru import logger

from agents import CriticAgent, PlannerAgent, ReasoningAgent, ResearchAgent
from core.llm import generate_stream
from models import (
    ChatMessage,
    ChatSession,
    PipelineResult,
    QueryRequest,
)
from rag import get_rag_engine


# ─── In-memory chat sessions ───

_sessions: dict[str, ChatSession] = {}


def get_or_create_session(session_id: str | None) -> ChatSession:
    if session_id and session_id in _sessions:
        return _sessions[session_id]
    session = ChatSession()
    _sessions[session.id] = session
    return session


def get_session(session_id: str) -> ChatSession | None:
    return _sessions.get(session_id)


def all_sessions() -> list[ChatSession]:
    return list(_sessions.values())


# ─── Pipeline ───

async def run_pipeline(request: QueryRequest) -> tuple[PipelineResult, ChatSession]:
    """Execute the full multi-agent pipeline. Returns (result, session)."""
    t0 = time.perf_counter()
    session = get_or_create_session(request.session_id)
    # Stamp the session_id back onto the request so callers can use it
    request.session_id = session.id
    session.messages.append(ChatMessage(role="user", content=request.query))

    rag_engine = get_rag_engine()
    has_docs = rag_engine.document_count > 0

    # 1 — Plan
    planner = PlannerAgent()
    plan = await planner.run(request.query, has_documents=has_docs)

    # 2 — Research
    researcher = ResearchAgent()
    research = await researcher.run(
        plan.subtasks,
        use_rag=request.use_rag and has_docs,
        use_web=request.use_web,
    )

    # 3 — Reason
    reasoner = ReasoningAgent()
    answer = await reasoner.run(plan, research, history=session.messages)

    # 4 — Critique
    critic = CriticAgent()
    evaluation = await critic.run(request.query, plan, research, answer)

    elapsed = (time.perf_counter() - t0) * 1000

    result = PipelineResult(
        query=request.query,
        plan=plan,
        research=research,
        answer=answer,
        evaluation=evaluation,
        duration_ms=elapsed,
    )

    # Store in memory
    session.messages.append(
        ChatMessage(role="assistant", content=answer.answer, metadata=result)
    )

    logger.info(
        "Pipeline complete in {:.0f}ms — score={:.2f} approved={}",
        elapsed,
        evaluation.overall_score,
        evaluation.approved,
    )
    return result, session


async def stream_answer(result: PipelineResult) -> AsyncIterator[str]:
    """Re-stream the answer token by token via LLM for a polished delivery."""
    prompt = f"""Restate the following answer clearly and fluently. Output ONLY the answer text.

{result.answer.answer}"""
    async for chunk in generate_stream(prompt):
        yield chunk
