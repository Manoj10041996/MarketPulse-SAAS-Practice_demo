class AgentUnavailableError(Exception):
    """Raised when the analysis agent fails to produce a result.

    Carries only a safe, client-facing message — the real cause is logged
    server-side, never included here.
    """

    def __init__(self, message: str = "Analysis service is temporarily unavailable.") -> None:
        super().__init__(message)
        self.message = message
