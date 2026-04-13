"""Base page class for all Finance Tracker UI pages."""
from abc import ABC, abstractmethod
import gradio as gr


class BasePage(ABC):
    """Abstract base class for all pages.

    Every page must implement:
        - build()  : constructs and returns the Gradio Blocks UI
        - title()  : returns the page title
    """

    @property
    @abstractmethod
    def title(self) -> str:
        """Page title shown in the UI."""
        pass

    @abstractmethod
    def build(self) -> gr.Blocks:
        """Build and return the Gradio UI for this page."""
        pass