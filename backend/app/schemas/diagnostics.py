from pydantic import BaseModel


class AnthropicKeyCheckResponse(BaseModel):
    valid: bool
