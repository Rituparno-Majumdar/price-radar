"""Unit tests for platform parsers using mock HTML fixtures."""

from fetcher.parsers import AmazonParser, FlipkartParser, CromaParser, RelianceParser


def test_amazon_parser_json_ld():
    html = """
    <html>
      <head>
        <script type="application/ld+json">
        {
          "@context": "https://schema.org",
          "@type": "Product",
          "name": "Apple iPhone 15 (128 GB) - Black",
          "offers": {
            "@type": "Offer",
            "price": "69999.00",
            "priceCurrency": "INR",
            "availability": "https://schema.org/InStock"
          }
        }
        </script>
      </head>
      <body></body>
    </html>
    """
    parser = AmazonParser()
    url = "https://www.amazon.in/dp/B0CHX1W1XY"
    res = parser.parse(html, url)

    assert res.platform == "amazon_in"
    assert res.product_id == "B0CHX1W1XY"
    assert res.current_price == 69999.0
    assert res.currency == "INR"
    assert res.extraction_method == "json_ld"
    assert res.in_stock is True


def test_amazon_parser_dom_fallback():
    html = """
    <html>
      <body>
        <span id="productTitle">Samsung Galaxy S24</span>
        <span class="a-price-whole">74,999</span>
        <span class="a-text-price"><span class="a-offscreen">₹89,999</span></span>
      </body>
    </html>
    """
    parser = AmazonParser()
    url = "https://www.amazon.in/dp/B0CX2198ZQ"
    res = parser.parse(html, url)

    assert res.platform == "amazon_in"
    assert res.product_id == "B0CX2198ZQ"
    assert res.current_price == 74999.0
    assert res.original_price == 89999.0
    assert res.discount_percentage == 16.67
    assert res.extraction_method == "dom_fallback"


def test_flipkart_parser_dom():
    html = """
    <html>
      <body>
        <span class="VU-ZEz">Apple iPhone 15 (Blue, 128 GB)</span>
        <div class="Nx9bqj">₹68,999</div>
        <div class="yRaY8j">₹79,900</div>
      </body>
    </html>
    """
    parser = FlipkartParser()
    url = "https://www.flipkart.com/apple-iphone-15/p/itmbf5553733dec9?pid=MOBGTAGPAQNVFZZY"
    res = parser.parse(html, url)

    assert res.platform == "flipkart"
    assert res.product_id == "MOBGTAGPAQNVFZZY"
    assert res.current_price == 68999.0
    assert res.original_price == 79900.0
    assert res.discount_percentage == 13.64
    assert res.extraction_method == "dom_fallback"


def test_croma_parser_opengraph():
    html = """
    <html>
      <head>
        <meta property="product:price:amount" content="69490" />
        <meta property="og:title" content="Apple iPhone 15 (128GB, Black)" />
      </head>
      <body></body>
    </html>
    """
    parser = CromaParser()
    url = "https://www.croma.com/apple-iphone-15-128gb-black-/p/300652"
    res = parser.parse(html, url)

    assert res.platform == "croma"
    assert res.product_id == "300652"
    assert res.current_price == 69490.0
    assert res.extraction_method == "opengraph"


def test_reliance_parser_json_ld():
    html = """
    <html>
      <head>
        <script type="application/ld+json">
        {
          "@context": "https://schema.org",
          "@type": "Product",
          "name": "Apple iPhone 15 128 GB",
          "offers": {
            "@type": "Offer",
            "price": "69900",
            "priceCurrency": "INR",
            "availability": "https://schema.org/InStock"
          }
        }
        </script>
      </head>
      <body></body>
    </html>
    """
    parser = RelianceParser()
    url = "https://www.reliancedigital.in/apple-iphone-15-128-gb/p/493839294"
    res = parser.parse(html, url)

    assert res.platform == "reliance_digital"
    assert res.product_id == "493839294"
    assert res.current_price == 69900.0
    assert res.extraction_method == "json_ld"
