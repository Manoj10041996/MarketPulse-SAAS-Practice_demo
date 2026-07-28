import json
from contextvars import ContextVar

from langchain.tools import tool

from app.clients.oxylabs import OxylabsAPIError, get_oxylabs_client
from app.config import get_settings


class _CallCounter:
    """Mutable counter held behind a ContextVar.

    Individual tool calls may run in child asyncio Tasks that each get their
    own copy of the current Context. Rebinding a ContextVar inside a child
    (`.set(n)`) only updates that child's local copy and never propagates
    back. Mutating an attribute on a shared object does propagate, since
    every child holds a reference to the same object — as long as the
    object was already bound in an ancestor context (via reset, below)
    before any child tasks were spawned.
    """

    __slots__ = ("value",)

    def __init__(self) -> None:
        self.value = 0


_search_call_count: ContextVar[_CallCounter] = ContextVar("search_call_count")
_product_lookup_count: ContextVar[_CallCounter] = ContextVar("product_lookup_count")


def reset_request_counters() -> None:
    """Reset per-request tool-call counters. Call once before each agent invocation."""
    _search_call_count.set(_CallCounter())
    _product_lookup_count.set(_CallCounter())


def _get_counter(var: ContextVar[_CallCounter]) -> _CallCounter:
    try:
        return var.get()
    except LookupError:
        counter = _CallCounter()
        var.set(counter)
        return counter


@tool
async def search_amazon_products(query: str, domain: str = "com", max_results: int = 10) -> str:
    """Search Amazon for products matching a keyword or category.

    Use this first for any question about a product category, or to find
    competitors for a described product. Returns a JSON list of matching
    products with asin, title, price, rating, reviews_count, and badges
    like is_prime/best_seller/is_sponsored.
    """
    settings = get_settings()
    counter = _get_counter(_search_call_count)
    if counter.value >= settings.max_search_calls_per_request:
        return (
            f"Search limit reached ({settings.max_search_calls_per_request} per question). "
            "Base the analysis on results already gathered."
        )
    counter.value += 1

    try:
        results = await get_oxylabs_client().search_products(query, domain=domain)
    except OxylabsAPIError as exc:
        return f"Could not search Amazon for '{query}': {exc.message}"

    capped = results[: min(max_results, 15)]
    return json.dumps([r.model_dump() for r in capped])


@tool
async def get_amazon_product_details(asin: str, domain: str = "com") -> str:
    """Get full details for one specific Amazon product by ASIN.

    Use this for a deep-dive on a specific competitor product found via
    search, or when the user names a specific product/ASIN directly.
    This is capped per question — don't call it for every search result,
    only the ones that matter most for the comparison.
    """
    settings = get_settings()
    counter = _get_counter(_product_lookup_count)
    if counter.value >= settings.max_product_detail_lookups:
        return (
            f"Product detail lookup limit reached ({settings.max_product_detail_lookups} "
            "per question). Base the comparison on search data for remaining products."
        )
    counter.value += 1

    try:
        result = await get_oxylabs_client().get_product(asin, domain=domain)
    except OxylabsAPIError as exc:
        return f"Could not fetch details for {asin}: {exc.message}"

    return result.model_dump_json()
