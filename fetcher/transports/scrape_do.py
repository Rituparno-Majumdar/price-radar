"""
Scrape.do HTTP transport adapter.
Delivers high-speed proxy rotation and residential unblocking.
"""

import os
import requests
from typing import Optional
from urllib.parse import urlencode

from fetcher.transports.base import BaseTransport


class ScrapeDoTransport(BaseTransport):
    """
    Scrape.do REST API transport adapter.
    Fastest response times across Amazon India, Croma, and Reliance Digital.
    """

    def __init__(
        self,
        token: Optional[str] = None,
        timeout: int = 30,
        render: bool = False,
        super_proxy: bool = False,
        geo_code: Optional[str] = None,
    ):
        self.token = token or os.getenv("SCRAPEDO_API_KEY") or os.getenv("SCRAPE_DO_TOKEN")
        self.timeout = timeout
        self.render = render
        self.super_proxy = super_proxy
        self.geo_code = geo_code

    def fetch_html(self, url: str) -> str:
        if not self.token:
            raise ValueError(
                "Scrape.do token missing. Pass token to constructor or set SCRAPEDO_API_KEY."
            )

        params = {
            "token": self.token,
            "url": url,
        }
        if self.render:
            params["render"] = "true"
        if self.super_proxy:
            params["super"] = "true"
        if self.geo_code:
            params["geoCode"] = self.geo_code

        endpoint = f"http://api.scrape.do/?{urlencode(params)}"
        resp = requests.get(endpoint, timeout=self.timeout)
        resp.raise_for_status()
        return resp.text
