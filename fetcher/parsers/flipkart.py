"""
Flipkart parser implementation.
Extracts FSN pid and parses preloaded state and DOM fallbacks.
"""

import json
import re
from typing import Any, Dict, Optional
from fetcher.parsers.base import BasePlatformParser


class FlipkartParser(BasePlatformParser):
    PLATFORM_NAME = "flipkart"

    def extract_product_id(self, url: str) -> Optional[str]:
        # FSN pid query parameter or path segment
        match = re.search(r"pid=([A-Z0-9]{16})", url)
        if not match:
            match = re.search(r"/p/(itm[a-zA-Z0-9]+)", url)
        return match.group(1) if match else None

    def _extract_dom_fallback(self, html: str) -> Dict[str, Any]:
        # Check window.__INITIAL_STATE__
        state_match = re.search(r"window\.__INITIAL_STATE__\s*=\s*({.*?});</script>", html)
        if state_match:
            try:
                state = json.loads(state_match.group(1))
                # If pageData presents pricing, it can be extracted here
            except Exception:
                pass

        price_match = re.search(
            r'<div[^>]+class=["\'][^"\']*(?:Nx9bqj|hl05eU|_30jeq3)[^"\']*["\'][^>]*>₹?([\d,]+)</div>',
            html,
        )
        mrp_match = re.search(
            r'<div[^>]+class=["\'][^"\']*(?:yRaY8j|_3I9_wc)[^"\']*["\'][^>]*>₹?([\d,]+)</div>',
            html,
        )
        title_match = re.search(
            r'<span[^>]+class=["\'][^"\']*(?:VU-ZEz|B_NuCI)[^"\']*["\'][^>]*>(.*?)</span>',
            html,
        )

        return {
            "title": title_match.group(1).strip() if title_match else None,
            "currency": "INR",
            "current_price": self._clean_price(price_match.group(1)) if price_match else None,
            "original_price": self._clean_price(mrp_match.group(1)) if mrp_match else None,
            "in_stock": "Sold Out" not in html and "Currently Out of Stock" not in html,
        }
