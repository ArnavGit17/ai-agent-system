"""Structured logging with loguru."""

import sys
from pathlib import Path

from loguru import logger
from core.config import get_settings


def setup_logging() -> None:
    settings = get_settings()
    logger.remove()
    fmt = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    logger.add(sys.stderr, format=fmt, level=settings.log_level, colorize=True)

    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    logger.add(
        str(log_dir / "agent_system.log"),
        rotation="10 MB",
        retention="7 days",
        format=fmt,
        level="DEBUG",
    )
    logger.info("Logging initialised at level={}", settings.log_level)
