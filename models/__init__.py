"""
Domain models shared across every layer.
Every inter-agent message is a typed Pydantic model.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ────────────────────────── Enums ──────────────────────────

class AgentRole(str, Enum):
    PLANNER = "planner"
    RESEARCHER = "researcher"
    REASONER = "reasoner"
    CRITIC = "critic"


class ToolName(str, Enum):
    WEB_SEARCH = "web_search"
    RAG_RETRIEVAL = "rag_retrieval"


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


# ────────────────────────── Planner ──────────────────────────

class SubTask(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:8])
    description: str
    tools_needed: list[ToolName] = []
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[str] = None


class PlannerOutput(BaseModel):
    original_query: str
    rewritten_query: str
    subtasks: list[SubTask]
    reasoning: str


# ────────────────────────── Research ──────────────────────────

class RetrievedChunk(BaseModel):
    content: str
    source: str
    score: float
    metadata: dict = {}


class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str


class ResearchOutput(BaseModel):
    subtask_id: str
    rag_results: list[RetrievedChunk] = []
    web_results: list[SearchResult] = []
    combined_context: str


# ────────────────────────── Reasoning ──────────────────────────

class ReasoningOutput(BaseModel):
    answer: str
    sources: list[str]
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning_trace: str


# ────────────────────────── Critic ──────────────────────────

class CriticEvaluation(BaseModel):
    relevance_score: float = Field(ge=0.0, le=1.0)
    accuracy_score: float = Field(ge=0.0, le=1.0)
    completeness_score: float = Field(ge=0.0, le=1.0)
    overall_score: float = Field(ge=0.0, le=1.0)
    feedback: str
    improvements: list[str]
    approved: bool


# ────────────────────────── Pipeline ──────────────────────────

class PipelineResult(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    query: str
    plan: PlannerOutput
    research: list[ResearchOutput]
    answer: ReasoningOutput
    evaluation: CriticEvaluation
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    duration_ms: float = 0.0


# ────────────────────────── Chat / Memory ──────────────────────────

class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Optional[PipelineResult] = None


class ChatSession(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    messages: list[ChatMessage] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ────────────────────────── API Schemas ──────────────────────────

class QueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    session_id: Optional[str] = None
    use_rag: bool = True
    use_web: bool = True


class QueryResponse(BaseModel):
    session_id: str
    answer: str
    plan: PlannerOutput
    research_summaries: list[dict]
    evaluation: CriticEvaluation
    sources: list[str]
    duration_ms: float


class UploadResponse(BaseModel):
    filename: str
    chunks_created: int
    message: str


class HealthResponse(BaseModel):
    status: str
    documents_indexed: int
    embedding_model: str
    llm_model: str
