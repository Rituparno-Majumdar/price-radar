"""
Smart Proxy and Web Unlocker transport adapter.
Supports ZenRows, BrightData Web Unlocker, ScraperAPI, and generic rotating proxies.
"""

import os
import requests
from typing import Optional
from urllib.parse import urlencode

from fetcher.transports.base import BaseTransport


class SmartProxyTransport(BaseTransport):
    """
    Proxy adapter routing requests through managed Web Unlockers
    (ZenRows, BrightData, ScraperAPI) to bypass Akamai/AWS WAF/Cloudflare.
    """

    def __init__(
        self,
        provider: str = "zenrows",
        api_key: Optional[str] = None,
        timeout: int = 30,
        js_render: bool = True,
        premium_proxy: bool = True,
    ):
        self.provider = provider.lower()
        self.api_key = api_key or os.getenv("SMART_PROXY_API_KEY") or os.getenv("ZENROWS_API_KEY")
        self.timeout = timeout
        self.js_render = js_render
        self.premium_proxy = premium_proxy

    def fetch_html(self, url: str) -> str:
        if not self.api_key:
            raise ValueError(
                f"API key missing for provider '{self.provider}'. "
                "Set SMART_PROXY_API_KEY in environment or pass api_key to constructor."
            )

        if self.provider == "zenrows":
            return self._fetch_zenrows(url)
        elif self.provider == "scraper_api":
            return self._fetch_scraper_api(url)
        elif self.provider == "brightdata":
            return self._fetch_brightdata(url)
        else:
            raise ValueError(f"Unsupported proxy provider: {self.provider}")

    def _fetch_zenrows(self, url: str) -> str:
        params = {
            "apikey": self.api_key,
            "url": url,
            "js_render": "true" if self.js_render else "false",
            "premium_proxy": "true" if self.premium_proxy else "false",
        }
        endpoint = f"https://api.zenrows.com/v1/?{urlencode(params)}"
        resp = requests.get(endpoint, timeout=self.timeout)
        resp.raise_for_status()
        return resp.text

    def _fetch_scraper_api(self, url: str) -> str:
        params = {
            "api_key": self.api_key,
            "url": url,
            "render": "true" if self.js_render else "false",
            "country_code": "in",
        }
        endpoint = f"https://api.scraperapi.com/?{urlencode(params)}"
        resp = requests.get(endpoint, timeout=self.timeout)
        resp.raise_for_status()
        return resp.text

    def _fetch_brightdata(self, url: str) -> str:
        # BrightData Web Unlocker via HTTP CONNECT proxy format
        proxy_url = f"http://{self.api_key}@brd.superproxy.io:22225"
        proxies = {"http": proxy_url, "https": proxy_url}
        resp = requests.get(url, proxies=proxies, timeout=self.timeout, verify=False)
        resp.raise_for_status()
        return resp.text
