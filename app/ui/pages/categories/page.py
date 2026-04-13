"""Categories page UI for Finance Tracker."""
import gradio as gr
import logging
from app.ui.pages import BasePage
from app.ui.state.session import SessionState

logger = logging.getLogger(__name__)


class CategoriesPage(BasePage):
    """Categories management page."""

    def __init__(self, session: SessionState):
        self.session = session

    @property
    def title(self) -> str:
        return "Categories"

    def build(self) -> gr.Blocks:
        with gr.Blocks(title="Finance Tracker - Categories") as categories_ui:
            gr.Markdown("# Categories")
            gr.Markdown("Manage your transaction categories here.")

            # placeholder - will be built out in next step
            gr.Markdown("Coming soon - full categories UI")

        return categories_ui