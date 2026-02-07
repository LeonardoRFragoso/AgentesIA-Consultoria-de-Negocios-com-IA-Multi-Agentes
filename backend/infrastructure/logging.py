"""
Logging compatibility layer.
Re-exports from observability module for backward compatibility.
"""
from .observability import (
    setup_logging as configure_logging,
    get_logger,
    setup_logging,
)

__all__ = [
    "configure_logging",
    "get_logger",
    "setup_logging",
]
