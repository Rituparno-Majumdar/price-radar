"""
Direct HTTP transport with headers and user-agent rotation.
Suitable for testing and low-friction endpoints.
"""

import random
import requests
from typing import Optional

from fetcher.transports.base import BaseTransport

DEFAULT_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
]


class DirectTransport(BaseTransport):
    """Direct HTTP transport utilizing standard requests with browser headers."""

    def __init__(self, timeout: int = 15, user_agents: Optional[list] = None):
        self.timeout = timeout
        self.user_agents = user_agents or DEFAULT_USER_AGENTS

    def fetch_html(self, url: str) -> str:
        headers = {
            "User-Agent": random.choice(self.user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-IN,en;q=0.9",
            "Upgrade-Insecure-Requests": "1",
        }
        resp = requests.get(url, headers=headers, timeout=self.timeout)
        resp.raise_for_status()
        return resp.text
