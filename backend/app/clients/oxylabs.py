import logging
from functools import lru_cache

import httpx
from tenacity import (
    AsyncRetrying,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from app.config import Settings, get_settings
from app.schemas.oxylabs import SimplifiedProductDetail, SimplifiedSearchResult

logger = logging.getLogger(__name__)

_OXYLABS_ENDPOINT = "https://realtime.oxylabs.io/v1/queries"
_RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


class OxylabsAPIError(Exception):
    """Raised when an Oxylabs request fails unrecoverably."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _absolute_url(url: str | None, domain: str) -> str | None:
    """amazon_search returns site-relative URLs (e.g. "/dp/B0X..."); make
    them absolute so they're directly usable/clickable by API consumers."""
    if not url:
        return url
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return f"https://www.amazon.{domain}{url}"


def _is_retryable(exc: BaseException) -> bool:
    if isinstance(exc, (httpx.TimeoutException, httpx.ConnectError)):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in _RETRYABLE_STATUS_CODES
    return False


class OxylabsClient:
    """Thin async wrapper around the Oxylabs Realtime API for Amazon scraping."""

    def __init__(self, username: str, password: str, timeout: float, max_retries: int) -> None:
        self._max_retries = max_retries
        self._http = httpx.AsyncClient(auth=(username, password), timeout=timeout)

    async def aclose(self) -> None:
        await self._http.aclose()

    async def search_products(
        self, query: str, domain: str = "com"
    ) -> list[SimplifiedSearchResult]:
        payload = {
            "source": "amazon_search",
            "domain": domain,
            "query": query,
            "start_page": 1,
            "pages": 1,
            "parse": True,
        }
        data = await self._post(payload)
        return self._simplify_search_results(data, domain)

    async def get_product(self, asin: str, domain: str = "com") -> SimplifiedProductDetail:
        payload = {
            "source": "amazon_product",
            "domain": domain,
            "query": asin,
            "parse": True,
            "context": [{"key": "autoselect_variant", "value": True}],
        }
        data = await self._post(payload)
        return self._simplify_product(data, asin)

    async def _post(self, payload: dict) -> dict:
        retrying = AsyncRetrying(
            stop=stop_after_attempt(self._max_retries),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception(_is_retryable),
            reraise=True,
        )
        try:
            async for attempt in retrying:
                with attempt:
                    response = await self._http.post(_OXYLABS_ENDPOINT, json=payload)
                    response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logger.exception("Oxylabs request failed with HTTP error")
            raise OxylabsAPIError(
                "Oxylabs request failed", status_code=exc.response.status_code
            ) from exc
        except (httpx.TimeoutException, httpx.ConnectError) as exc:
            logger.exception("Oxylabs request failed with network error")
            raise OxylabsAPIError("Oxylabs request timed out or was unreachable") from exc

        try:
            return response.json()
        except ValueError as exc:
            logger.exception("Oxylabs response was not valid JSON")
            raise OxylabsAPIError("Oxylabs returned an unparseable response") from exc

    @staticmethod
    def _simplify_search_results(data: dict, domain: str) -> list[SimplifiedSearchResult]:
        results: list[SimplifiedSearchResult] = []
        try:
            # The result groups are nested one level deeper than the rest of
            # `content`'s fields: content["results"]["organic"], not
            # content["organic"].
            groups = data["results"][0]["content"]["results"]
        except (KeyError, IndexError, TypeError):
            return results

        for group in ("organic", "paid", "amazons_choices"):
            for item in groups.get(group, []) or []:
                asin = item.get("asin")
                title = item.get("title")
                if not asin or not title:
                    continue
                results.append(
                    SimplifiedSearchResult(
                        asin=asin,
                        title=title,
                        price=item.get("price"),
                        price_upper=item.get("price_upper"),
                        price_strikethrough=item.get("price_strikethrough"),
                        currency=item.get("currency"),
                        rating=item.get("rating"),
                        reviews_count=item.get("reviews_count"),
                        url=_absolute_url(item.get("url"), domain),
                        is_sponsored=bool(item.get("is_sponsored", group == "paid")),
                        is_amazons_choice=bool(item.get("is_amazons_choice")),
                        is_prime=bool(item.get("is_prime")),
                        best_seller=bool(item.get("best_seller")),
                        sales_volume=item.get("sales_volume"),
                    )
                )
        return results

    @staticmethod
    def _simplify_product(data: dict, asin: str) -> SimplifiedProductDetail:
        try:
            content = data["results"][0]["content"]
        except (KeyError, IndexError, TypeError):
            content = {}

        # category is a list of "ladder" breadcrumbs, e.g.
        # [{"ladder": [{"name": "Electronics", ...}, {"name": "Headphones", ...}]}]
        category = content.get("category")
        category_str = None
        if isinstance(category, str):
            category_str = category
        elif isinstance(category, list) and category:
            ladder = category[0].get("ladder") if isinstance(category[0], dict) else None
            if isinstance(ladder, list) and ladder and isinstance(ladder[0], dict):
                category_str = ladder[0].get("name")

        merchant = content.get("featured_merchant") or {}
        sales_rank = content.get("sales_rank")
        sales_rank_value = None
        if isinstance(sales_rank, list) and sales_rank:
            sales_rank_value = sales_rank[0].get("rank")
        elif isinstance(sales_rank, int):
            sales_rank_value = sales_rank

        return SimplifiedProductDetail(
            asin=content.get("asin", asin),
            title=content.get("title") or content.get("product_name") or "",
            manufacturer=content.get("manufacturer"),
            price=content.get("price"),
            price_buybox=content.get("price_buybox"),
            currency=content.get("currency"),
            stock=content.get("stock"),
            is_prime_eligible=bool(content.get("is_prime_eligible")),
            rating=content.get("rating"),
            reviews_count=content.get("reviews_count"),
            category=category_str,
            sales_rank=sales_rank_value,
            deal_type=content.get("deal_type"),
            seller_name=merchant.get("name") if isinstance(merchant, dict) else None,
        )


@lru_cache(maxsize=1)
def get_oxylabs_client() -> OxylabsClient:
    settings: Settings = get_settings()
    return OxylabsClient(
        username=settings.oxylabs_username,
        password=settings.oxylabs_password,
        timeout=settings.oxylabs_timeout_seconds,
        max_retries=settings.oxylabs_max_retries,
    )
