"""Abstract base router for all Finance Tracker routes."""
import logging
from abc import ABC, abstractmethod
from fastapi import APIRouter


class BaseRouter(ABC):
    """Base class for all route handlers.

    Subclasses must implement register() which wires
    all route handlers to the router and returns it.
    """

    def __init__(self, prefix: str, tags: list):
        """Initialize router with prefix and tags.

        Args:
            prefix: URL prefix for all routes in this router.
            tags  : Swagger UI tags for grouping.
        """
        self.router = APIRouter(prefix=prefix, tags=tags)
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def register(self) -> APIRouter:
        """Register all routes and return the configured router.

        Returns:
            Configured APIRouter instance.
        """
        pass