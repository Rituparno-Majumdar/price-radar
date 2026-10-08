"""
Reliance Digital parser implementation.
Extracts article code and parses pricing metadata.
"""

import re
from typing import Any, Dict, Optional
from fetcher.parsers.base import BasePlatformParser


class RelianceParser(BasePlatformParser):
    PLATFORM_NAME = "reliance_digital"

    def extract_product_id(self, url: str) -> Optional[str]:
        # Reliance product URLs: /p/<slug>/<article_code> or /product/<slug>-<article_code>
        match = re.search(r"(?:/p/|/product/.*?-?)(\d{6,12})(?:\?|$)", url)
        if not match:
            match = re.search(r"(\d{6,12})(?:\?|$)", url)
        return match.group(1) if match else None

    def _extract_dom_fallback(self, html: str) -> Dict[str, Any]:
        price_match = re.search(
            r'<span[^>]+class=["\'][^"\']*sc-jefHHS[^"\']*["\'][^>]*>₹?([\d,]+)</span>',
            html,
        )
        if not price_match:
            price_match = re.search(
                r'<span[^>]+class=["\'][^"\']*Text__StyledText[^"\']*["\'][^>]*>₹?([\d,]+)</span>',
                html,
            )
        title_match = re.search(r'<h1[^>]*>(.*?)</h1>', html)

        return {
            "title": title_match.group(1).strip() if title_match else None,
            "currency": "INR",
            "current_price": self._clean_price(price_match.group(1)) if price_match else None,
            "original_price": None,
            "in_stock": "Notify Me" not in html,
        }
