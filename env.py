"""
Core environment entrypoint for businessenv.

This module exposes `BusinessEnv` as the primary environment class while
keeping compatibility with the existing server implementation.
"""

try:
    from .server.businessenv_environment import BusinessEnvironment
except (ImportError, ModuleNotFoundError):
    from businessenv.server.businessenv_environment import BusinessEnvironment


class BusinessEnv(BusinessEnvironment):
    """Primary environment class exposed by the package."""


__all__ = ["BusinessEnv", "BusinessEnvironment"]
