"""
Async wrapper around Google Gemini generative AI.
Provides both blocking and streaming generation,
with retry logic and structured JSON extraction.
"""

from __future__ import annotations

import asyncio
import json
import re
from typing import AsyncIterator

import google.generativeai as genai
from loguru import logger

from core.config import get_settings

_configured = False


def _ensure_configured() -> None:
    global _configured
    if not _configured:
        settings = get_settings()
        genai.configure(api_key=settings.gemini_api_key)
        _configured = True


def _get_model() -> genai.GenerativeModel:
    _ensure_configured()
    settings = get_settings()
    return genai.GenerativeModel(
        settings.gemini_model,
        generation_config=genai.GenerationConfig(
            temperature=settings.gemini_temperature,
            max_output_tokens=settings.gemini_max_tokens,
        ),
    )


async def generate(prompt: str, system: str = "") -> str:
    """Single-shot generation. Returns full text."""
    model = _get_model()
    full_prompt = f"{system}\n\n{prompt}" if system else prompt
    try:
        response = await asyncio.to_thread(
            model.generate_content, full_prompt
        )
        return response.text
    except Exception as e:
        logger.error("Gemini generation failed: {}", e)
        raise


async def generate_json(prompt: str, system: str = "") -> dict:
    """Generate and parse JSON from the response."""
    raw = await generate(prompt, system)
    # Extract JSON from markdown code fences if present
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw)
    text = match.group(1).strip() if match else raw.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        logger.warning("JSON parse failed, attempting repair")
        # Try to find the first { ... } or [ ... ]
        brace = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", text)
        if brace:
            return json.loads(brace.group(1))
        raise


async def generate_stream(prompt: str, system: str = "") -> AsyncIterator[str]:
    """Streaming token generation.

    Gemini's stream is a sync iterator, so we consume it in a background
    thread and bridge chunks to the async world via an asyncio.Queue.
    """
    model = _get_model()
    full_prompt = f"{system}\n\n{prompt}" if system else prompt
    queue: asyncio.Queue[str | None] = asyncio.Queue()

    def _produce() -> None:
        try:
            response = model.generate_content(full_prompt, stream=True)
            for chunk in response:
                if chunk.text:
                    queue.put_nowait(chunk.text)
        except Exception as exc:
            logger.error("Gemini stream failed: {}", exc)
            queue.put_nowait(exc)  # type: ignore[arg-type]
        finally:
            queue.put_nowait(None)  # sentinel

    loop = asyncio.get_running_loop()
    loop.run_in_executor(None, _produce)

    while True:
        item = await queue.get()
        if item is None:
            break
        if isinstance(item, Exception):
            raise item
        yield item
