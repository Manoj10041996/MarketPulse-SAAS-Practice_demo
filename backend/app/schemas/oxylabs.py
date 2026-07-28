from pydantic import BaseModel


class SimplifiedSearchResult(BaseModel):
    """Projection of one amazon_search result item down to comparison-relevant fields."""

    asin: str
    title: str
    price: float | None = None
    price_upper: float | None = None
    price_strikethrough: float | None = None
    currency: str | None = None
    rating: float | None = None
    reviews_count: int | None = None
    url: str | None = None
    is_sponsored: bool = False
    is_amazons_choice: bool = False
    is_prime: bool = False
    best_seller: bool = False
    sales_volume: str | None = None


class SimplifiedProductDetail(BaseModel):
    """Projection of one amazon_product response down to comparison-relevant fields."""

    asin: str
    title: str
    manufacturer: str | None = None
    price: float | None = None
    price_buybox: float | None = None
    currency: str | None = None
    stock: str | None = None
    is_prime_eligible: bool = False
    rating: float | None = None
    reviews_count: int | None = None
    category: str | None = None
    sales_rank: int | None = None
    deal_type: str | None = None
    seller_name: str | None = None
