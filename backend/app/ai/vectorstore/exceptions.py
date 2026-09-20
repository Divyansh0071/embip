"""
Normalized Application Exceptions for Vector Database & Qdrant Operations.
"""


class VectorStoreError(Exception):
    """Base exception class for vector store operations."""

    def __init__(self, message: str, provider: str = "qdrant"):
        self.message = message
        self.provider = provider
        super().__init__(self.message)


class VectorStoreConnectionError(VectorStoreError):
    """Raised when connection to Qdrant cluster/server fails."""
    pass


class VectorStoreCollectionError(VectorStoreError):
    """Raised when Qdrant collection creation or configuration fails."""
    pass


class VectorStoreOperationError(VectorStoreError):
    """Raised when vector upsert or search operations fail."""
    pass
