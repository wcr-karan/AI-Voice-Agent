"""
Structured logging configuration.
"""

import logging
import sys
from app.config import settings


def setup_logger(name: str = "voice_agent") -> logging.Logger:
    """
    Create and configure a structured logger.

    Args:
        name: Logger name (default: "voice_agent").

    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logger.level)

    formatter = logging.Formatter(
        fmt="%(levelname)s - %(message)s",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Prevent log propagation to root logger
    logger.propagate = False

    return logger


# Default application logger
logger = setup_logger()
