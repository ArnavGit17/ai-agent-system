"""
FastAPI application — REST endpoints for the multi-agent system.

Endpoints:
  POST /query          → full pipeline execution
  POST /query/stream   → SSE streaming response
  POST /upload         → PDF document ingestion
  GET  /history        → chat session history
  GET  /history/{id}   → single session
  GET  /health         → system health check
"""

from __future__ import annotations

import shutil
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from loguru import logger

from api.pipeline import (
    all_sessions,
    get_session,
    run_pipeline,
    stream_answer,
)
from core import get_settings, setup_logging
from models import (
    HealthResponse,
    QueryRequest,
    QueryResponse,
    UploadResponse,
)
from rag import get_rag_engine

# ─── App init ───

setup_logging()
settings = get_settings()

app = FastAPI(
    title="Autonomous AI Agent System",
    version="1.0.0",
    description="Multi-agent pipeline: Planner → Researcher → Reasoner → Critic",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Routes ───


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    engine = get_rag_engine()
    return HealthResponse(
        status="ok",
        documents_indexed=engine.document_count,
        embedding_model=settings.embedding_model,
        llm_model=settings.gemini_model,
    )


@app.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest) -> QueryResponse:
    """Run the full multi-agent pipeline and return structured results."""
    try:
        result, session = await run_pipeline(req)

        research_summaries = []
        for r in result.research:
            research_summaries.append({
                "subtask_id": r.subtask_id,
                "rag_count": len(r.rag_results),
                "web_count": len(r.web_results),
                "context_preview": r.combined_context[:300],
            })

        return QueryResponse(
            session_id=session.id,
            answer=result.answer.answer,
            plan=result.plan,
            research_summaries=research_summaries,
            evaluation=result.evaluation,
            sources=result.answer.sources,
            duration_ms=result.duration_ms,
        )
    except Exception as e:
        logger.exception("Pipeline error")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query/stream")
async def query_stream(req: QueryRequest):
    """Run pipeline then stream the final answer via SSE."""
    import json

    try:
        result, session = await run_pipeline(req)

        async def event_generator():
            meta = {
                "type": "metadata",
                "session_id": session.id,
                "plan": result.plan.model_dump(),
                "evaluation": result.evaluation.model_dump(),
                "sources": result.answer.sources,
                "duration_ms": result.duration_ms,
            }
            yield f"data: {json.dumps(meta)}\n\n"

            # Then stream answer tokens
            async for token in stream_answer(result):
                payload = json.dumps({"type": "token", "content": token})
                yield f"data: {payload}\n\n"

            yield "data: {\"type\": \"done\"}\n\n"

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    except Exception as e:
        logger.exception("Stream pipeline error")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)) -> UploadResponse:
    """Upload a PDF document for RAG ingestion."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    dest = upload_dir / file.filename

    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    engine = get_rag_engine()
    chunks = await engine.ingest_pdf(str(dest), file.filename)

    return UploadResponse(
        filename=file.filename,
        chunks_created=chunks,
        message=f"Successfully ingested {chunks} chunks from {file.filename}",
    )


@app.get("/history")
async def get_history():
    """Return all chat sessions."""
    sessions = all_sessions()
    return [
        {
            "id": s.id,
            "message_count": len(s.messages),
            "created_at": s.created_at.isoformat(),
            "preview": s.messages[0].content[:100] if s.messages else "",
        }
        for s in sessions
    ]


@app.get("/history/{session_id}")
async def get_session_history(session_id: str):
    """Return messages for a specific session."""
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "id": session.id,
        "created_at": session.created_at.isoformat(),
        "messages": [
            {
                "role": m.role,
                "content": m.content,
                "timestamp": m.timestamp.isoformat(),
            }
            for m in session.messages
        ],
    }
