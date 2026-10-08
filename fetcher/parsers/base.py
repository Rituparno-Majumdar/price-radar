"""
Base platform parser with tiered extraction:
Tier 1: Schema.org (JSON-LD) Product markup
Tier 2: OpenGraph / Meta tags
Tier 3: Platform-specific DOM / Regex heuristics
"""

import abc
import json
import re
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fetcher.models import NormalizedPrice


class BasePlatformParser(abc.ABC):
    """Abstract parser defining extraction lifecycle and fallback hierarchy."""

    PLATFORM_NAME: str = "unknown"

    @abc.abstractmethod
    def extract_product_id(self, url: str) -> Optional[str]:
        """Extract platform-specific SKU or unique product identifier."""
        pass

    def parse(self, html: str, url: str) -> NormalizedPrice:
        """
        Execute multi-tiered extraction against retrieved HTML.
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        product_id = self.extract_product_id(url)

        # Tier 1: Schema.org JSON-LD
        json_ld = self._extract_json_ld(html)
        if json_ld and json_ld.get("current_price"):
            return NormalizedPrice(
                platform=self.PLATFORM_NAME,
                product_id=product_id,
                title=json_ld.get("title"),
                currency=json_ld.get("currency", "INR"),
                current_price=json_ld.get("current_price"),
                original_price=json_ld.get("original_price"),
                discount_percentage=self._calc_discount(
                    json_ld.get("current_price"), json_ld.get("original_price")
                ),
                in_stock=json_ld.get("in_stock", True),
                source_url=url,
                extraction_method="json_ld",
                timestamp_utc=now_iso,
            )

        # Tier 2: OpenGraph & Product Meta Tags
        og = self._extract_opengraph(html)
        if og and og.get("current_price"):
            return NormalizedPrice(
                platform=self.PLATFORM_NAME,
                product_id=product_id,
                title=og.get("title"),
                currency=og.get("currency", "INR"),
                current_price=og.get("current_price"),
                original_price=None,
                discount_percentage=None,
                in_stock=True,
                source_url=url,
                extraction_method="opengraph",
                timestamp_utc=now_iso,
            )

        # Tier 3: Platform DOM fallback
        dom = self._extract_dom_fallback(html)
        return NormalizedPrice(
            platform=self.PLATFORM_NAME,
            product_id=product_id,
            title=dom.get("title"),
            currency=dom.get("currency", "INR"),
            current_price=dom.get("current_price"),
            original_price=dom.get("original_price"),
            discount_percentage=self._calc_discount(
                dom.get("current_price"), dom.get("original_price")
            ),
            in_stock=dom.get("in_stock", True),
            source_url=url,
            extraction_method="dom_fallback",
            timestamp_utc=now_iso,
        )

    def _extract_json_ld(self, html: str) -> Optional[Dict[str, Any]]:
        pattern = re.compile(
            r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
            re.DOTALL | re.IGNORECASE,
        )
        matches = pattern.findall(html)
        decoder = json.JSONDecoder()
        for match in matches:
            content = match.strip()
            if not content:
                continue
            data = None
            try:
                data = json.loads(content)
            except Exception:
                try:
                    data, _ = decoder.raw_decode(content.lstrip())
                except Exception:
                    continue

            if not data:
                continue

            items = data if isinstance(data, list) else [data]
            for item in items:
                if isinstance(item, dict) and item.get("@type") == "Product":
                    offers = item.get("offers", {})
                    if isinstance(offers, list):
                        offers = offers[0] if offers else {}
                    price = offers.get("price") or offers.get("lowPrice")
                    if price:
                        return {
                            "title": item.get("name"),
                            "currency": offers.get("priceCurrency", "INR"),
                            "current_price": float(str(price).replace(",", "")),
                            "original_price": None,
                            "in_stock": "InStock" in str(offers.get("availability", "")),
                        }
        return None

    def _extract_opengraph(self, html: str) -> Optional[Dict[str, Any]]:
        price_match = re.search(
            r'<meta[^>]+property=["\'](?:product:price:amount|og:price:amount)["\'][^>]+content=["\']([^"\']+)["\']',
            html,
            re.IGNORECASE,
        )
        title_match = re.search(
            r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)["\']',
            html,
            re.IGNORECASE,
        )
        if price_match:
            try:
                return {
                    "title": title_match.group(1).strip() if title_match else None,
                    "currency": "INR",
                    "current_price": float(price_match.group(1).replace(",", "")),
                }
            except ValueError:
                pass
        return None

    @abc.abstractmethod
    def _extract_dom_fallback(self, html: str) -> Dict[str, Any]:
        """Platform-specific regex or DOM fallback logic."""
        pass

    @staticmethod
    def _calc_discount(
        current: Optional[float], original: Optional[float]
    ) -> Optional[float]:
        if current and original and original > current:
            return round(((original - current) / original) * 100, 2)
        return None

    @staticmethod
    def _clean_price(val: Optional[str]) -> Optional[float]:
        if not val:
            return None
        cleaned = re.sub(r"[^\d.]", "", val)
        try:
            return float(cleaned)
        except ValueError:
            return None
