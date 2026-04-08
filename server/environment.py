"""Thin server wrapper exposing BusinessEnv for FastAPI app creation."""

try:
    from ..env import BusinessEnv
except (ImportError, ModuleNotFoundError):
    from businessenv.env import BusinessEnv

__all__ = ["BusinessEnv"]
