"""Unit tests for NormalizedPrice data model."""

from fetcher.models import NormalizedPrice


def test_normalized_price_to_dict():
    price = NormalizedPrice(
        platform="amazon_in",
        product_id="B0CHX1W1XY",
        title="Apple iPhone 15",
        currency="INR",
        current_price=69999.0,
        original_price=79900.0,
        discount_percentage=12.39,
        in_stock=True,
        source_url="https://www.amazon.in/dp/B0CHX1W1XY",
        extraction_method="json_ld",
        timestamp_utc="2026-10-08T06:00:00Z",
    )
    d = price.to_dict()
    assert d["platform"] == "amazon_in"
    assert d["product_id"] == "B0CHX1W1XY"
    assert d["current_price"] == 69999.0
    assert d["discount_percentage"] == 12.39
    assert d["in_stock"] is True
    assert d["extraction_method"] == "json_ld"
