"""
Abstract base for every agent in the pipeline.
Provides common logging, timing, and LLM access.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any

from loguru import logger

from models import AgentRole


class BaseAgent(ABC):
    role: AgentRole

    def __init__(self, role: AgentRole) -> None:
        self.role = role

    async def run(self, *args: Any, **kwargs: Any) -> Any:
        logger.info("[{}] Starting execution", self.role.value.upper())
        t0 = time.perf_counter()
        try:
            result = await self.execute(*args, **kwargs)
            elapsed = (time.perf_counter() - t0) * 1000
            logger.info("[{}] Done in {:.0f}ms", self.role.value.upper(), elapsed)
            return result
        except Exception as e:
            logger.error("[{}] Failed: {}", self.role.value.upper(), e)
            raise

    @abstractmethod
    async def execute(self, *args: Any, **kwargs: Any) -> Any:
        ...
