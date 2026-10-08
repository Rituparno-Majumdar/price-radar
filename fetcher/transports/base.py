"""
Base interface for HTTP transport adapters.
"""

import abc


class BaseTransport(abc.ABC):
    """Abstract base class for fetching HTML payloads."""

    @abc.abstractmethod
    def fetch_html(self, url: str) -> str:
        """
        Fetch HTML content from a given target URL.

        Args:
            url: Fully-qualified product URL.

        Returns:
            Rendered raw HTML string.

        Raises:
            Exception: If network error or unrecoverable block occurs.
        """
        pass
