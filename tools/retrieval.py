"""
RAG retrieval as a callable tool for agents.
"""

from __future__ import annotations

from loguru import logger

from models import RetrievedChunk
from rag import get_rag_engine


async def rag_retrieve(query: str, top_k: int = 5) -> list[RetrievedChunk]:
    """Retrieve relevant chunks from the vector store."""
    engine = get_rag_engine()
    logger.info("RAG retrieval for: '{}'", query[:80])
    return await engine.retrieve(query, top_k=top_k)
