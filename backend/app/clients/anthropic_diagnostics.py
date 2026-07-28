from anthropic import AsyncAnthropic, AuthenticationError


async def check_anthropic_key(api_key: str) -> bool:
    """Validates the configured Anthropic key with a cheap, no-completion
    call (models.list()) — confirms auth without spending generation tokens."""
    client = AsyncAnthropic(api_key=api_key)
    try:
        await client.models.list()
        return True
    except AuthenticationError:
        return False
