"""
Research Agent — executes each subtask by calling the appropriate tools
(web search and/or RAG retrieval), then merges the results.
"""

from __future__ import annotations

import asyncio

from loguru import logger

from agents.base import BaseAgent
from models import (
    AgentRole,
    ResearchOutput,
    SubTask,
    TaskStatus,
    ToolName,
)
from tools.retrieval import rag_retrieve
from tools.search import web_search


class ResearchAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentRole.RESEARCHER)

    async def execute(
        self,
        subtasks: list[SubTask],
        use_rag: bool = True,
        use_web: bool = True,
    ) -> list[ResearchOutput]:
        results: list[ResearchOutput] = []

        for task in subtasks:
            task.status = TaskStatus.IN_PROGRESS
            logger.info("Researching subtask: {}", task.description[:60])

            rag_results = []
            web_results = []

            coros = []
            if ToolName.RAG_RETRIEVAL in task.tools_needed and use_rag:
                coros.append(("rag", rag_retrieve(task.description)))
            if ToolName.WEB_SEARCH in task.tools_needed and use_web:
                coros.append(("web", web_search(task.description)))

            # Run tools concurrently
            if coros:
                gathered = await asyncio.gather(
                    *[c[1] for c in coros], return_exceptions=True
                )
                for (label, _), result in zip(coros, gathered):
                    if isinstance(result, Exception):
                        logger.warning("Tool {} failed: {}", label, result)
                        continue
                    if label == "rag":
                        rag_results = result
                    elif label == "web":
                        web_results = result

            # Build combined context
            context_parts = []
            for r in rag_results:
                context_parts.append(f"[DOC: {r.source}] {r.content}")
            for r in web_results:
                context_parts.append(f"[WEB: {r.title}] {r.snippet}")

            combined = "\n\n".join(context_parts) if context_parts else "No results found."

            task.status = TaskStatus.COMPLETED
            task.result = combined[:500]

            results.append(
                ResearchOutput(
                    subtask_id=task.id,
                    rag_results=rag_results,
                    web_results=web_results,
                    combined_context=combined,
                )
            )

        return results
