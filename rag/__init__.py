"""
RAG Engine — PDF ingestion, chunking, embedding, FAISS indexing & retrieval.

Lifecycle:
  1. ingest_pdf()  → extract text → chunk → embed → add to FAISS
  2. retrieve()    → embed query → FAISS search → re-rank → return chunks
"""

from __future__ import annotations

import asyncio
import pickle
from pathlib import Path
from typing import Optional

import faiss
import numpy as np
from langchain_text_splitters import RecursiveCharacterTextSplitter
from loguru import logger
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

from core.config import get_settings
from models import RetrievedChunk


class RAGEngine:
    """Singleton-style RAG engine with FAISS backend."""

    def __init__(self) -> None:
        self._settings = get_settings()
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=self._settings.chunk_size,
            chunk_overlap=self._settings.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        self._embedder: Optional[SentenceTransformer] = None
        self._index: Optional[faiss.IndexFlatIP] = None
        self._chunks: list[dict] = []  # parallel to FAISS vectors
        self._meta_path = Path(self._settings.faiss_index_path) / "meta.pkl"
        self._index_path = Path(self._settings.faiss_index_path) / "index.faiss"

    # ── lazy init ──

    def _load_embedder(self) -> SentenceTransformer:
        if self._embedder is None:
            logger.info("Loading embedding model: {}", self._settings.embedding_model)
            self._embedder = SentenceTransformer(self._settings.embedding_model)
        return self._embedder

    def _ensure_index(self) -> faiss.IndexFlatIP:
        if self._index is None:
            dim = self._settings.embedding_dimension
            if self._index_path.exists() and self._meta_path.exists():
                logger.info("Loading existing FAISS index")
                self._index = faiss.read_index(str(self._index_path))
                with open(self._meta_path, "rb") as f:
                    self._chunks = pickle.load(f)
            else:
                logger.info("Creating new FAISS index (dim={})", dim)
                self._index = faiss.IndexFlatIP(dim)
                self._chunks = []
        return self._index

    def _save_index(self) -> None:
        index = self._ensure_index()
        self._index_path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(index, str(self._index_path))
        with open(self._meta_path, "wb") as f:
            pickle.dump(self._chunks, f)
        logger.debug("FAISS index saved ({} vectors)", index.ntotal)

    # ── embeddings ──

    def _embed(self, texts: list[str]) -> np.ndarray:
        model = self._load_embedder()
        vecs = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return np.array(vecs, dtype="float32")

    # ── ingestion ──

    def _extract_pdf_text(self, pdf_path: str) -> str:
        reader = PdfReader(pdf_path)
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
        return "\n\n".join(pages)

    async def ingest_pdf(self, pdf_path: str, filename: str) -> int:
        """Extract text from PDF, chunk, embed, add to FAISS. Returns chunk count."""
        logger.info("Ingesting PDF: {}", filename)
        text = await asyncio.to_thread(self._extract_pdf_text, pdf_path)
        if not text.strip():
            logger.warning("No text extracted from {}", filename)
            return 0

        docs = self._splitter.create_documents(
            [text],
            metadatas=[{"source": filename}],
        )
        texts = [d.page_content for d in docs]
        embeddings = await asyncio.to_thread(self._embed, texts)

        index = self._ensure_index()
        index.add(embeddings)
        for i, doc in enumerate(docs):
            self._chunks.append({
                "content": doc.page_content,
                "source": filename,
                "metadata": doc.metadata,
            })

        self._save_index()
        logger.info("Ingested {} chunks from {}", len(docs), filename)
        return len(docs)

    async def ingest_text(self, text: str, source: str = "manual") -> int:
        """Ingest raw text (for testing or non-PDF sources)."""
        docs = self._splitter.create_documents(
            [text],
            metadatas=[{"source": source}],
        )
        texts_list = [d.page_content for d in docs]
        embeddings = await asyncio.to_thread(self._embed, texts_list)

        index = self._ensure_index()
        index.add(embeddings)
        for doc in docs:
            self._chunks.append({
                "content": doc.page_content,
                "source": source,
                "metadata": doc.metadata,
            })
        self._save_index()
        return len(docs)

    # ── retrieval ──

    async def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
    ) -> list[RetrievedChunk]:
        """Embed query, search FAISS, return ranked chunks."""
        index = self._ensure_index()
        if index.ntotal == 0:
            return []

        k = min(top_k or self._settings.top_k_results, index.ntotal)
        q_vec = await asyncio.to_thread(self._embed, [query])
        scores, indices = index.search(q_vec, k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            chunk = self._chunks[idx]
            results.append(
                RetrievedChunk(
                    content=chunk["content"],
                    source=chunk["source"],
                    score=float(score),
                    metadata=chunk.get("metadata", {}),
                )
            )
        # Re-rank: already sorted by inner product (descending)
        return results

    @property
    def document_count(self) -> int:
        idx = self._ensure_index()
        return idx.ntotal


# ── module-level singleton ──
_engine: Optional[RAGEngine] = None


def get_rag_engine() -> RAGEngine:
    global _engine
    if _engine is None:
        _engine = RAGEngine()
    return _engine
