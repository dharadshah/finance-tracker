"""Main entry point for Finance Tracker Gradio UI."""
import gradio as gr
import logging
from app.ui.state.session import SessionState
from app.ui.pages.login.handler import AuthHandler
from app.ui.pages.login.page import LoginPage
from app.ui.pages.transactions.page import TransactionsPage
from app.ui.pages.categories.page import CategoriesPage

logging.basicConfig(
    level  = logging.INFO,
    format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)

logger = logging.getLogger("app.models.transaction")


class FinanceTrackerApp:
    """Main application class that wires all pages together."""

    def __init__(self):
        self.session      = SessionState()
        self.auth_handler = AuthHandler()

        self.login_page        = LoginPage(self.session, self.auth_handler)
        self.transactions_page = TransactionsPage(self.session)
        self.categories_page   = CategoriesPage(self.session)

    def build(self) -> gr.TabbedInterface:
        login_ui        = self.login_page.build()
        transactions_ui = self.transactions_page.build()
        categories_ui   = self.categories_page.build()

        app = gr.TabbedInterface(
            interface_list = [login_ui, transactions_ui, categories_ui],
            tab_names      = [
                self.login_page.title,
                self.transactions_page.title,
                self.categories_page.title
            ],
            title = "Personal Finance Tracker"
        )
        return app

    def launch(self):
        logger.info("Starting Finance Tracker UI")
        app = self.build()
        app.launch(server_port=7860)


if __name__ == "__main__":
    finance_app = FinanceTrackerApp()
    finance_app.launch()