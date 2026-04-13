"""Session state management for Finance Tracker UI."""


class SessionState:
    """Manages user session state across pages."""

    def __init__(self):
        self.is_authenticated : bool = False
        self.username         : str  = ""
        self.token            : str  = ""

    def login(self, username: str, token: str = "mock-token"):
        self.is_authenticated = True
        self.username         = username
        self.token            = token

    def logout(self):
        self.is_authenticated = False
        self.username         = ""
        self.token            = ""

    def is_logged_in(self) -> bool:
        return self.is_authenticated