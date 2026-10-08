"""
Normalized data models for price-radar results.
"""

from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional


@dataclass
class NormalizedPrice:
    platform: str
    product_id: Optional[str]
    title: Optional[str]
    currency: str
    current_price: Optional[float]
    original_price: Optional[float]
    discount_percentage: Optional[float]
    in_stock: bool
    source_url: str
    extraction_method: str  # "json_ld", "opengraph", "dom_fallback"
    timestamp_utc: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert normalized price result to dictionary."""
        return asdict(self)
