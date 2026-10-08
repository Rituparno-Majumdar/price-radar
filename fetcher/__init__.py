"""
Price-Radar: Resilient Indian E-commerce Price Scraper.
"""

from fetcher.core import PriceFetcher
from fetcher.models import NormalizedPrice

__all__ = ["PriceFetcher", "NormalizedPrice"]
