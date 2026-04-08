from fastapi import HTTPException


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