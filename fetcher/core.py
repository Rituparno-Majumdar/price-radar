"""
Core PriceFetcher orchestrator engine.
Binds URL routing, transport execution, and platform parsing into a unified pipeline.
"""

import logging
from typing import Dict, Optional
from urllib.parse import urlparse

from fetcher.models import NormalizedPrice
from fetcher.parsers import (
    AmazonParser,
    BasePlatformParser,
    CromaParser,
    FlipkartParser,
    RelianceParser,
)
from fetcher.transports.base import BaseTransport
from fetcher.transports.direct import DirectTransport
from fetcher.transports.smart_proxy import SmartProxyTransport

logger = logging.getLogger("price_radar.fetcher")


class PriceFetcher:
    """
    Unified price-fetching engine.
    Dispatches URLs to appropriate platform parser and executes HTML fetch via configured transport.
    """

    PARSER_REGISTRY: Dict[str, BasePlatformParser] = {
        "amazon.in": AmazonParser(),
        "flipkart.com": FlipkartParser(),
        "croma.com": CromaParser(),
        "reliancedigital.in": RelianceParser(),
    }

    def __init__(
        self,
        transport: Optional[BaseTransport] = None,
        smart_proxy_provider: Optional[str] = None,
        smart_proxy_api_key: Optional[str] = None,
    ):
        if transport:
            self.transport = transport
        elif smart_proxy_provider or smart_proxy_api_key:
            self.transport = SmartProxyTransport(
                provider=smart_proxy_provider or "zenrows",
                api_key=smart_proxy_api_key,
            )
        else:
            self.transport = DirectTransport()

    def resolve_parser(self, url: str) -> BasePlatformParser:
        domain = urlparse(url).netloc.lower()
        # Clean www. prefix if present
        if domain.startswith("www."):
            domain = domain[4:]

        for key, parser in self.PARSER_REGISTRY.items():
            if key in domain:
                return parser

        raise ValueError(
            f"Unsupported domain: '{domain}'. Supported domains: {list(self.PARSER_REGISTRY.keys())}"
        )

    def fetch_price(self, url: str) -> NormalizedPrice:
        """
        Fetch and parse product price for a given URL.

        Args:
            url: Target product URL.

        Returns:
            NormalizedPrice object.
        """
        parser = self.resolve_parser(url)
        logger.info(f"Resolved parser '{parser.PLATFORM_NAME}' for URL: {url}")

        html = self.transport.fetch_html(url)
        return parser.parse(html, url)
