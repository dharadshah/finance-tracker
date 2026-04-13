"""Authentication handler - mock implementation."""
import logging

logger = logging.getLogger("app.models.transaction")

# Mock credentials - will be replaced with real API call later
MOCK_USERS = {
    "admin" : "admin123",
    "dhara" : "password123"
}


class AuthHandler:
    """Handles authentication logic for the UI."""

    def login(self, username: str, password: str) -> tuple[bool, str]:
        """Attempt to authenticate a user.

        Args:
            username: The username entered by the user.
            password: The password entered by the user.

        Returns:
            Tuple of (success, message)
        """
        if not username or not password:
            logger.warning("Login attempted with empty credentials")
            return False, "Username and password are required."

        if username not in MOCK_USERS:
            logger.warning(f"Login failed - unknown user: {username}")
            return False, "Invalid username or password."

        if MOCK_USERS[username] != password:
            logger.warning(f"Login failed - wrong password for: {username}")
            return False, "Invalid username or password."

        logger.info(f"Login successful: {username}")
        return True, f"Welcome, {username}!"

    def logout(self) -> tuple[bool, str]:
        """Log out the current user.

        Returns:
            Tuple of (success, message)
        """
        return True, "Logged out successfully."