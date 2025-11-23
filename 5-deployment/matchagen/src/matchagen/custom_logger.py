"""Custom logger configuration using loguru."""

import sys

from loguru import logger

# Remove default logger
logger.remove()

# Add custom logger with formatting
logger.add(
    sys.stdout,
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<level>{message}</level>"
    ),
    level="INFO",
)
