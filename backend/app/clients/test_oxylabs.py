import httpx
import pytest
import respx

from app.clients.oxylabs import OxylabsAPIError, OxylabsClient

_ENDPOINT = "https://realtime.oxylabs.io/v1/queries"


def _client() -> OxylabsClient:
    return OxylabsClient(username="u", password="p", timeout=1.0, max_retries=3)


@pytest.mark.asyncio
async def test_search_products_success():
    payload = {
        "results": [
            {
                "content": {
                    "results": {
                        "organic": [
                            {
                                "asin": "B0EXAMPLE1",
                                "title": "Wireless Earbuds",
                                "price": 29.99,
                                "currency": "USD",
                                "rating": 4.5,
                                "reviews_count": 1200,
                                "url": "/dp/B0EXAMPLE1",
                                "is_prime": True,
                            }
                        ],
                        "paid": [],
                        "amazons_choices": [],
                    }
                }
            }
        ]
    }
    with respx.mock:
        respx.post(_ENDPOINT).mock(return_value=httpx.Response(200, json=payload))
        client = _client()
        results = await client.search_products("wireless earbuds")

    assert len(results) == 1
    assert results[0].asin == "B0EXAMPLE1"
    assert results[0].price == 29.99
    assert results[0].is_prime is True
    assert results[0].url == "https://www.amazon.com/dp/B0EXAMPLE1"


@pytest.mark.asyncio
async def test_get_product_success():
    payload = {
        "results": [
            {
                "content": {
                    "asin": "B0EXAMPLE1",
                    "title": "Wireless Earbuds",
                    "price": 29.99,
                    "currency": "USD",
                    "rating": 4.5,
                    "reviews_count": 1200,
                    "stock": "In Stock",
                    "featured_merchant": {"name": "Acme Co"},
                    "category": [{"ladder": [{"name": "Electronics"}]}],
                    "sales_rank": [{"rank": 42}],
                }
            }
        ]
    }
    with respx.mock:
        respx.post(_ENDPOINT).mock(return_value=httpx.Response(200, json=payload))
        client = _client()
        result = await client.get_product("B0EXAMPLE1")

    assert result.asin == "B0EXAMPLE1"
    assert result.seller_name == "Acme Co"
    assert result.category == "Electronics"
    assert result.sales_rank == 42


@pytest.mark.asyncio
async def test_retries_then_succeeds_on_429():
    payload = {
        "results": [
            {"content": {"results": {"organic": [], "paid": [], "amazons_choices": []}}}
        ]
    }
    with respx.mock:
        respx.post(_ENDPOINT).mock(
            side_effect=[httpx.Response(429), httpx.Response(200, json=payload)]
        )
        client = _client()
        results = await client.search_products("test")

    assert results == []


@pytest.mark.asyncio
async def test_exhausts_retries_on_persistent_500():
    with respx.mock:
        route = respx.post(_ENDPOINT).mock(return_value=httpx.Response(500))
        client = _client()
        with pytest.raises(OxylabsAPIError):
            await client.search_products("test")
        assert route.call_count == 3


@pytest.mark.asyncio
async def test_no_retry_on_400():
    with respx.mock:
        route = respx.post(_ENDPOINT).mock(return_value=httpx.Response(400))
        client = _client()
        with pytest.raises(OxylabsAPIError):
            await client.search_products("test")
        assert route.call_count == 1


@pytest.mark.asyncio
async def test_malformed_json_raises_oxylabs_error():
    with respx.mock:
        respx.post(_ENDPOINT).mock(
            return_value=httpx.Response(200, content=b"not json", headers={"content-type": "application/json"})
        )
        client = _client()
        with pytest.raises(OxylabsAPIError):
            await client.search_products("test")


@pytest.mark.asyncio
async def test_timeout_raises_oxylabs_error():
    with respx.mock:
        respx.post(_ENDPOINT).mock(side_effect=httpx.TimeoutException("timed out"))
        client = _client()
        with pytest.raises(OxylabsAPIError):
            await client.search_products("test")
