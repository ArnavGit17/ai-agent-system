"""
Centralized configuration via pydantic-settings.
All env vars are loaded once and validated at startup.
"""

from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── LLM ──
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    gemini_temperature: float = 0.4
    gemini_max_tokens: int = 4096

    # ── Embeddings ──
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384

    # ── FAISS / RAG ──
    faiss_index_path: str = "./data/faiss_index"
    chunk_size: int = 512
    chunk_overlap: int = 64
    top_k_results: int = 5

    # ── Server ──
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    # ── Search ──
    serpapi_key: str = ""
    search_mode: str = "mock"  # "mock" | "serpapi"

    # ── Paths ──
    upload_dir: str = "./data/uploads"
    data_dir: str = "./data"

    def ensure_dirs(self) -> None:
        for d in [self.upload_dir, self.data_dir, self.faiss_index_path]:
            Path(d).mkdir(parents=True, exist_ok=True)


@lru_cache()
def get_settings() -> Settings:
    s = Settings()
    s.ensure_dirs()
    return s
