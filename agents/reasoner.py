"""
Reasoning Agent — synthesises a coherent answer from all research outputs,
performs multi-document reasoning, and reports confidence.
"""

from __future__ import annotations

from loguru import logger

from agents.base import BaseAgent
from core.llm import generate_json
from models import (
    AgentRole,
    ChatMessage,
    PlannerOutput,
    ReasoningOutput,
    ResearchOutput,
)

SYSTEM_PROMPT = """You are the Reasoning Agent in a multi-agent AI system.
You receive:
  1. The user's original (and rewritten) query.
  2. A plan with subtasks.
  3. Research results gathered from documents and web search.
  4. Recent conversation history for context.

Your job: synthesize a thorough, accurate, well-structured answer.

Return ONLY valid JSON:
{
  "answer": "<your detailed answer in markdown>",
  "sources": ["<source1>", "<source2>"],
  "confidence": 0.0-1.0,
  "reasoning_trace": "<brief explanation of your reasoning process>"
}

Guidelines:
- Cite sources inline when possible.
- If evidence conflicts, acknowledge it.
- Rate your confidence based on evidence quality and coverage.
- Be comprehensive but concise.
"""


class ReasoningAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentRole.REASONER)

    async def execute(
        self,
        plan: PlannerOutput,
        research: list[ResearchOutput],
        history: list[ChatMessage] | None = None,
    ) -> ReasoningOutput:
        # Build context block
        research_text = ""
        all_sources: set[str] = set()
        for r in research:
            research_text += f"\n--- Subtask {r.subtask_id} ---\n{r.combined_context}\n"
            for c in r.rag_results:
                all_sources.add(c.source)
            for w in r.web_results:
                all_sources.add(w.url)

        history_text = ""
        if history:
            recent = history[-6:]  # last 3 exchanges
            for msg in recent:
                history_text += f"\n{msg.role}: {msg.content[:300]}"

        prompt = f"""Original query: {plan.original_query}
Rewritten query: {plan.rewritten_query}
Plan reasoning: {plan.reasoning}

Subtask breakdown:
{chr(10).join(f"- {st.description}" for st in plan.subtasks)}

Research results:
{research_text}

Conversation history:
{history_text if history_text else "None"}

Now synthesize the final answer as JSON."""

        data = await generate_json(prompt, system=SYSTEM_PROMPT)

        return ReasoningOutput(
            answer=data.get("answer", "I could not generate an answer."),
            sources=data.get("sources", list(all_sources)),
            confidence=min(max(float(data.get("confidence", 0.5)), 0.0), 1.0),
            reasoning_trace=data.get("reasoning_trace", ""),
        )
