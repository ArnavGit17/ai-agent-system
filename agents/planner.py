"""
Planner Agent — analyses the user query, rewrites it for clarity,
and produces a structured list of subtasks with tool assignments.
"""

from __future__ import annotations

from loguru import logger

from agents.base import BaseAgent
from core.llm import generate_json
from models import AgentRole, PlannerOutput, SubTask, ToolName

SYSTEM_PROMPT = """You are the Planner Agent in a multi-agent AI system.
Your job: given a user query, produce a structured execution plan.

Return ONLY valid JSON matching this schema (no markdown, no explanation):
{
  "original_query": "<the user's raw query>",
  "rewritten_query": "<a clearer, more specific version of the query>",
  "reasoning": "<your analysis of what the query needs>",
  "subtasks": [
    {
      "description": "<what this step does>",
      "tools_needed": ["web_search" and/or "rag_retrieval"]
    }
  ]
}

Guidelines:
- Break complex queries into 2-5 subtasks.
- Simple factual queries may need only 1 subtask.
- Assign tools: use "rag_retrieval" when the query is about uploaded documents,
  "web_search" for current or broad knowledge, or both when useful.
- Rewrite the query to remove ambiguity.
"""


class PlannerAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentRole.PLANNER)

    async def execute(self, query: str, has_documents: bool = False) -> PlannerOutput:
        prompt = f"""User query: "{query}"
Documents available in RAG: {has_documents}

Produce the execution plan as JSON."""

        data = await generate_json(prompt, system=SYSTEM_PROMPT)

        subtasks = []
        for st in data.get("subtasks", []):
            tools = []
            for t in st.get("tools_needed", []):
                if t in ("web_search", "rag_retrieval"):
                    tools.append(ToolName(t))
            subtasks.append(
                SubTask(description=st["description"], tools_needed=tools)
            )

        if not subtasks:
            subtasks = [
                SubTask(
                    description=f"Answer: {query}",
                    tools_needed=[ToolName.WEB_SEARCH],
                )
            ]

        plan = PlannerOutput(
            original_query=query,
            rewritten_query=data.get("rewritten_query", query),
            subtasks=subtasks,
            reasoning=data.get("reasoning", ""),
        )
        logger.debug("Plan: {} subtasks", len(plan.subtasks))
        return plan
