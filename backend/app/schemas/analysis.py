from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    domain: str | None = Field(default=None, pattern=r"^[a-z]{2,3}(\.[a-z]{2,3})?$")


class ComparedProduct(BaseModel):
    asin: str
    title: str
    price: float | None = None
    currency: str | None = None
    rating: float | None = None
    reviews_count: int | None = None
    url: str | None = None
    is_prime: bool = False
    is_sponsored: bool = False
    best_seller: bool = False


class AgentAnalysisResult(BaseModel):
    """Structured output contract the agent itself must fill in (response_format)."""

    summary: str
    products: list[ComparedProduct] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class AnalysisResponse(BaseModel):
    """Public API response contract — kept separate from AgentAnalysisResult so the
    public contract can evolve independently of internal prompt/agent changes."""

    question: str
    domain: str
    summary: str
    products: list[ComparedProduct] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
