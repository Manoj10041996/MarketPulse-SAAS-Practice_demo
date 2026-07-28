import pytest

from app.clients.oxylabs import OxylabsAPIError
from app.schemas.oxylabs import SimplifiedProductDetail, SimplifiedSearchResult
from app.tools import amazon_tools


class _FakeClient:
    def __init__(self, search_results=None, product_result=None, raise_error=False):
        self._search_results = search_results or []
        self._product_result = product_result
        self._raise_error = raise_error

    async def search_products(self, query, domain="com"):
        if self._raise_error:
            raise OxylabsAPIError("boom")
        return self._search_results

    async def get_product(self, asin, domain="com"):
        if self._raise_error:
            raise OxylabsAPIError("boom")
        return self._product_result


@pytest.fixture(autouse=True)
def _reset_counters():
    amazon_tools.reset_request_counters()
    yield
    amazon_tools.reset_request_counters()


@pytest.mark.asyncio
async def test_search_tool_success(monkeypatch):
    fake = _FakeClient(
        search_results=[
            SimplifiedSearchResult(asin="B0X", title="Widget", price=9.99, currency="USD")
        ]
    )
    monkeypatch.setattr(amazon_tools, "get_oxylabs_client", lambda: fake)

    result = await amazon_tools.search_amazon_products.ainvoke(
        {"query": "widget", "domain": "com", "max_results": 10}
    )

    assert "B0X" in result
    assert "Widget" in result


@pytest.mark.asyncio
async def test_search_tool_error_returns_string_not_raise(monkeypatch):
    fake = _FakeClient(raise_error=True)
    monkeypatch.setattr(amazon_tools, "get_oxylabs_client", lambda: fake)

    result = await amazon_tools.search_amazon_products.ainvoke(
        {"query": "widget", "domain": "com", "max_results": 10}
    )

    assert "Could not search Amazon" in result


@pytest.mark.asyncio
async def test_search_tool_hard_cap(monkeypatch):
    fake = _FakeClient(search_results=[])
    monkeypatch.setattr(amazon_tools, "get_oxylabs_client", lambda: fake)
    settings = amazon_tools.get_settings()

    for _ in range(settings.max_search_calls_per_request):
        await amazon_tools.search_amazon_products.ainvoke(
            {"query": "widget", "domain": "com", "max_results": 10}
        )

    result = await amazon_tools.search_amazon_products.ainvoke(
        {"query": "widget", "domain": "com", "max_results": 10}
    )
    assert "limit reached" in result.lower()


@pytest.mark.asyncio
async def test_product_details_success(monkeypatch):
    fake = _FakeClient(
        product_result=SimplifiedProductDetail(asin="B0X", title="Widget", price=9.99)
    )
    monkeypatch.setattr(amazon_tools, "get_oxylabs_client", lambda: fake)

    result = await amazon_tools.get_amazon_product_details.ainvoke(
        {"asin": "B0X", "domain": "com"}
    )
    assert "B0X" in result


@pytest.mark.asyncio
async def test_product_details_error_returns_string_not_raise(monkeypatch):
    fake = _FakeClient(raise_error=True)
    monkeypatch.setattr(amazon_tools, "get_oxylabs_client", lambda: fake)

    result = await amazon_tools.get_amazon_product_details.ainvoke(
        {"asin": "B0X", "domain": "com"}
    )
    assert "Could not fetch details" in result


@pytest.mark.asyncio
async def test_product_details_hard_cap(monkeypatch):
    fake = _FakeClient(product_result=SimplifiedProductDetail(asin="B0X", title="Widget"))
    monkeypatch.setattr(amazon_tools, "get_oxylabs_client", lambda: fake)
    settings = amazon_tools.get_settings()

    for _ in range(settings.max_product_detail_lookups):
        await amazon_tools.get_amazon_product_details.ainvoke({"asin": "B0X", "domain": "com"})

    result = await amazon_tools.get_amazon_product_details.ainvoke(
        {"asin": "B0X", "domain": "com"}
    )
    assert "limit reached" in result.lower()


def test_reset_counters():
    amazon_tools.reset_request_counters()
    amazon_tools._search_call_count.get().value = 3
    amazon_tools._product_lookup_count.get().value = 2
    amazon_tools.reset_request_counters()
    assert amazon_tools._search_call_count.get().value == 0
    assert amazon_tools._product_lookup_count.get().value == 0
