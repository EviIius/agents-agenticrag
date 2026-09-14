class AgenticRAGError(Exception):
    """Base error for expected application failures."""


class ConfigurationError(AgenticRAGError):
    """Configuration is missing, unsafe, or internally inconsistent."""


class ProviderError(AgenticRAGError):
    """A configured model provider failed or returned an invalid response."""


class IngestionError(AgenticRAGError):
    """A source could not be parsed, chunked, or published."""


class StorageError(AgenticRAGError):
    """A configured durable store failed at its application boundary."""


class WorkflowError(AgenticRAGError):
    """A workflow failed a contract or validation boundary."""


class AuthorizationError(AgenticRAGError):
    """The current scope is not authorized to access a resource."""
