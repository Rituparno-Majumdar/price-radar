"""Unit tests for PriceFetcher core routing and execution."""

import pytest
from fetcher.core import PriceFetcher
from fetcher.transports.base import BaseTransport


class MockTransport(BaseTransport):
    def __init__(self, sample_html: str):
        self.sample_html = sample_html

    def fetch_html(self, url: str) -> str:
        return self.sample_html


def test_price_fetcher_routing():
    mock_html = """
    <html>
      <head>
        <script type="application/ld+json">
        {
          "@context": "https://schema.org",
          "@type": "Product",
          "name": "Test Phone",
          "offers": { "price": "49999", "priceCurrency": "INR" }
        }
        </script>
      </head>
      <body></body>
    </html>
    """
    transport = MockTransport(mock_html)
    fetcher = PriceFetcher(transport=transport)

    res = fetcher.fetch_price("https://www.amazon.in/dp/B0TESTASIN1")
    assert res.platform == "amazon_in"
    assert res.current_price == 49999.0

    res2 = fetcher.fetch_price("https://www.croma.com/test/p/12345")
    assert res2.platform == "croma"
    assert res2.current_price == 49999.0


def test_price_fetcher_unsupported_domain():
    fetcher = PriceFetcher()
    with pytest.raises(ValueError, match="Unsupported domain"):
        fetcher.fetch_price("https://unknown-shop.example.com/product/123")
