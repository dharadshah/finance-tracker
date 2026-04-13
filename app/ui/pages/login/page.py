"""Login page UI for Finance Tracker."""
import gradio as gr
import logging
from app.ui.pages import BasePage
from app.ui.pages.login.handler import AuthHandler
from app.ui.state.session import SessionState

logger = logging.getLogger(__name__)


class LoginPage(BasePage):
    """Login page - entry point for the Finance Tracker UI."""

    def __init__(self, session: SessionState, auth_handler: AuthHandler):
        self.session      = session
        self.auth_handler = auth_handler

    @property
    def title(self) -> str:
        return "Login"

    def build(self) -> gr.Blocks:
        with gr.Blocks(title="Finance Tracker - Login") as login_ui:
            gr.Markdown("# Personal Finance Tracker")
            gr.Markdown("### Please login to continue")

            with gr.Row():
                with gr.Column(scale=1):
                    pass
                with gr.Column(scale=2):
                    username    = gr.Textbox(
                        label       = "Username",
                        placeholder = "Enter your username"
                    )
                    password    = gr.Textbox(
                        label       = "Password",
                        placeholder = "Enter your password",
                        type        = "password"
                    )
                    login_btn   = gr.Button("Login", variant="primary")
                    message     = gr.Textbox(label="Status", interactive=False)
                with gr.Column(scale=1):
                    pass

            def handle_login(username: str, password: str):
                success, msg = self.auth_handler.login(username, password)
                if success:
                    self.session.login(username)
                return msg

            login_btn.click(
                fn      = handle_login,
                inputs  = [username, password],
                outputs = message
            )

        return login_ui