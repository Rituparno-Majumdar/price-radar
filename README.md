# price-radar

Resilient price-scraping engine and CLI for major Indian e-commerce platforms (**Amazon India**, **Flipkart**, **Croma**, and **Reliance Digital**).

## Overview

Scraping Indian e-commerce sites reliably at scale presents distinct defensive hurdles:
- **Amazon India:** Aggressive AWS WAF, JA3/JA4 TLS fingerprint filtering, and dynamic CAPTCHAs.
- **Flipkart:** Protected by Akamai Bot Manager (Shield), requiring residential IP pools and client telemetry.
- **Croma:** Edge-blocked by AkamaiGHost and Cloudflare challenges on datacenter IPs.
- **Reliance Digital:** Client-side JavaScript challenge and SPA hydration.

`price-radar` solves these challenges by combining a **pluggable transport abstraction** (Direct HTTP vs Managed Web Unlockers such as ZenRows, BrightData, and ScraperAPI) with a **3-tier semantic extraction pipeline** that prioritizes structured SEO schemas (`schema.org/Product` JSON-LD) over volatile CSS selectors.

---

## Extraction Hierarchy

1. **Tier 1 - Schema.org JSON-LD:**
   Extracts semantic `<script type="application/ld+json">` product records. Because platforms maintain JSON-LD for Google Rich Results and SEO indexing, this layer is virtually immune to frontend redesigns and CSS class churn.
2. **Tier 2 - OpenGraph & Product Metadata:**
   Extracts `product:price:amount` and `og:title` metadata tags rendered in the document head.
3. **Tier 3 - Platform DOM Fallback:**
   Applies platform-specific regex and preloaded state extractors (`window.__INITIAL_STATE__`) when structured schemas are omitted.

---

## Directory Structure

- `fetcher/`: Core library package.
  - `models.py`: Normalized data schema (`NormalizedPrice`).
  - `core.py`: URL parser router and `PriceFetcher` orchestrator.
  - `transports/`: Pluggable transport adapters (`BaseTransport`, `DirectTransport`, `SmartProxyTransport`).
  - `parsers/`: Modular platform parsers for Amazon, Flipkart, Croma, and Reliance Digital.
- `cli.py`: Standalone command-line interface.
- `tests/`: Comprehensive unit test suite with mock fixtures.
- `pyproject.toml`: Modern packaging specification.

---

## Installation

```bash
git clone https://github.com/Rituparno-Majumdar/price-radar.git
cd price-radar
pip install -e .
```

---

## Usage

### Command Line Interface

Fetch using direct HTTP transport (for friendly/cached routes):
```bash
python cli.py --url "https://www.amazon.in/dp/B0CHX1W1XY"
```

Fetch using ZenRows Web Unlocker (recommended for Akamai/AWS WAF bypass):
```bash
export SMART_PROXY_API_KEY="your_zenrows_api_key"
python cli.py --url "https://www.amazon.in/dp/B0CHX1W1XY" --provider zenrows
```

### Python SDK

```python
from fetcher import PriceFetcher
from fetcher.transports import SmartProxyTransport, DirectTransport

# 1. Direct Transport
fetcher = PriceFetcher(transport=DirectTransport())
result = fetcher.fetch_price("https://www.amazon.in/dp/B0CHX1W1XY")
print(result.to_dict())

# 2. Smart Proxy Unlocker Transport (ZenRows / BrightData)
proxy_transport = SmartProxyTransport(
    provider="zenrows",
    api_key="your_api_key",
    js_render=True
)
fetcher = PriceFetcher(transport=proxy_transport)
result = fetcher.fetch_price("https://www.flipkart.com/apple-iphone-15/p/itmbf5553733dec9?pid=MOBGTAGPAQNVFZZY")
print(result.to_dict())
```

---

## Normalized Output Schema

```json
{
  "platform": "amazon_in",
  "product_id": "B0CHX1W1XY",
  "title": "Apple iPhone 15 (128 GB) - Black",
  "currency": "INR",
  "current_price": 69999.0,
  "original_price": 79900.0,
  "discount_percentage": 12.39,
  "in_stock": true,
  "source_url": "https://www.amazon.in/dp/B0CHX1W1XY",
  "extraction_method": "json_ld",
  "timestamp_utc": "2026-10-08T06:12:00.000000+00:00"
}
```

---

## Running Tests

Execute the unit test suite:
```bash
pytest -v tests/
```

---

## License

MIT License. Authored by Rituparno Majumdar.
