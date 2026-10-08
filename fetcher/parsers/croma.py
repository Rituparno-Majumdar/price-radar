"""
Croma parser implementation.
Extracts numeric SKU ID and DOM/OpenGraph pricing.
"""

import re
from typing import Any, Dict, Optional
from fetcher.parsers.base import BasePlatformParser


class CromaParser(BasePlatformParser):
    PLATFORM_NAME = "croma"

    def extract_product_id(self, url: str) -> Optional[str]:
        # Croma product URLs terminate with /p/<id>
        match = re.search(r"/p/(\d+)", url)
        return match.group(1) if match else None

    def _extract_dom_fallback(self, html: str) -> Dict[str, Any]:
        price_match = re.search(r'data-testid=["\']new-price["\'][^>]*>₹?([\d,]+)', html)
        if not price_match:
            price_match = re.search(r'<span[^>]+class=["\'][^"\']*amount[^"\']*["\'][^>]*>₹?([\d,]+)</span>', html)
        title_match = re.search(r'<h1[^>]+class=["\'][^"\']*pd-title[^"\']*["\'][^>]*>(.*?)</h1>', html)

        return {
            "title": title_match.group(1).strip() if title_match else None,
            "currency": "INR",
            "current_price": self._clean_price(price_match.group(1)) if price_match else None,
            "original_price": None,
            "in_stock": "OUT OF STOCK" not in html.upper(),
        }
