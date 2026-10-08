"""
Amazon India parser implementation.
Extracts ASIN and resolves price blocks.
"""

import re
from typing import Any, Dict, Optional
from fetcher.parsers.base import BasePlatformParser


class AmazonParser(BasePlatformParser):
    PLATFORM_NAME = "amazon_in"

    def extract_product_id(self, url: str) -> Optional[str]:
        # ASIN matches 10 alphanumeric chars in /dp/B... or /gp/product/B...
        match = re.search(r"/(?:dp|gp/product)/([A-Z0-9]{10})", url)
        return match.group(1) if match else None

    def _extract_dom_fallback(self, html: str) -> Dict[str, Any]:
        title_match = re.search(
            r'<span[^>]+id=["\']productTitle["\'][^>]*>\s*(.*?)\s*</span>',
            html,
            re.DOTALL,
        )
        price_match = re.search(
            r'<span[^>]+class=["\'][^"\']*a-price-whole[^"\']*["\'][^>]*>([\d,]+)',
            html,
        )
        mrp_match = re.search(
            r'<span[^>]+class=["\'][^"\']*a-text-price[^"\']*["\'][^>]*>.*?<span[^>]+class=["\']a-offscreen["\']>([^<]+)',
            html,
            re.DOTALL,
        )

        current = self._clean_price(price_match.group(1)) if price_match else None
        original = self._clean_price(mrp_match.group(1)) if mrp_match else None
        title = title_match.group(1).strip() if title_match else None
        out_of_stock = "Currently unavailable" in html

        return {
            "title": title,
            "currency": "INR",
            "current_price": current,
            "original_price": original,
            "in_stock": not out_of_stock,
        }
