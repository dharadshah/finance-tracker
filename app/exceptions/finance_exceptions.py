from fastapi import HTTPException


# --- Base Exception ---

class FinanceBaseException(Exception):
    """Base class for all non-HTTP Finance Tracker exceptions."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


# --- Domain Exceptions ---

class TransactionNotFoundException(HTTPException):
    def __init__(self, transaction_id: int):
        super().__init__(
            status_code = 404,
            detail      = f"Transaction with id {transaction_id} not found"
        )


class CategoryNotFoundException(HTTPException):
    def __init__(self, category_id: int):
        super().__init__(
            status_code = 404,
            detail      = f"Category with id {category_id} not found"
        )


class CategoryAlreadyExistsException(HTTPException):
    def __init__(self, name: str):
        super().__init__(
            status_code = 400,
            detail      = f"Category '{name}' already exists"
        )


class InvalidTransactionException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code = 422,
            detail      = detail
        )


class AIAnalysisException(FinanceBaseException):
    """Raised when AI analysis fails."""
    pass


class DatabaseException(FinanceBaseException):
    """Raised when a database operation fails unexpectedly."""
    pass