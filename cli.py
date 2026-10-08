#!/usr/bin/env python3
"""
CLI entrypoint for price-radar.
Usage:
    python cli.py --url https://www.amazon.in/dp/B0CHX1W1XY
    python cli.py --url <url> --provider zenrows --api-key <key>
"""

import argparse
import json
import logging
import sys

from fetcher.core import PriceFetcher
from fetcher.transports.direct import DirectTransport
from fetcher.transports.smart_proxy import SmartProxyTransport

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("price_radar.cli")


def main():
    parser = argparse.ArgumentParser(
        description="Price-Radar: Resilient price-fetching CLI for Indian e-commerce platforms."
    )
    parser.add_argument(
        "--url",
        required=True,
        help="Product URL (Amazon India, Flipkart, Croma, Reliance Digital)",
    )
    parser.add_argument(
        "--provider",
        choices=["direct", "scrape_do", "zenrows", "scraper_api", "brightdata"],
        default="direct",
        help="Transport provider to use (default: direct)",
    )
    parser.add_argument(
        "--api-key",
        help="API key for smart proxy provider (or SMART_PROXY_API_KEY env var)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        default=True,
        help="Output raw JSON (default: True)",
    )

    args = parser.parse_args()

    from fetcher.transports.scrape_do import ScrapeDoTransport

    # Configure transport
    if args.provider == "direct":
        transport = DirectTransport()
    elif args.provider == "scrape_do":
        transport = ScrapeDoTransport(token=args.api_key)
    else:
        transport = SmartProxyTransport(
            provider=args.provider,
            api_key=args.api_key,
        )

    fetcher = PriceFetcher(transport=transport)

    try:
        result = fetcher.fetch_price(args.url)
        data = result.to_dict()
        print(json.dumps(data, indent=2))
    except Exception as e:
        logger.error(f"Failed to fetch price: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
