"""Unit tests for transport adapters."""

import pytest
from fetcher.transports.scrape_do import ScrapeDoTransport
from fetcher.transports.smart_proxy import SmartProxyTransport


def test_scrape_do_transport_missing_token():
    transport = ScrapeDoTransport(token="")
    with pytest.raises(ValueError, match="Scrape.do token missing"):
        transport.fetch_html("https://example.com")


def test_smart_proxy_missing_key():
    transport = SmartProxyTransport(provider="zenrows", api_key="")
    with pytest.raises(ValueError, match="API key missing"):
        transport.fetch_html("https://example.com")
