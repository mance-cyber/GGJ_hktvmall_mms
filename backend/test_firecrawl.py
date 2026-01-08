#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Firecrawl Scrape Test Script
Direct API testing without backend service
"""

import os
import sys
import io
from dotenv import load_dotenv

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Load environment variables
load_dotenv()

def test_basic_scrape():
    """Test basic scraping"""
    from firecrawl import FirecrawlApp

    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        print("[ERROR] FIRECRAWL_API_KEY not set")
        return False

    print(f"[OK] API Key: {api_key[:10]}...")

    app = FirecrawlApp(api_key=api_key)

    # Test URL - simple page first
    test_url = "https://www.google.com"
    print(f"\n[TEST] Basic scrape: {test_url}")

    try:
        # SDK v4.x uses scrape() with direct parameters
        result = app.scrape(
            test_url,
            formats=["markdown"],
            only_main_content=True
        )
        print(f"[OK] Scrape success!")
        print(f"  - Markdown length: {len(result.markdown or '')}")
        print(f"  - Title: {result.metadata.title if result.metadata else 'N/A'}")
        return True
    except Exception as e:
        print(f"[FAIL] Scrape failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_hktvmall_scrape():
    """Test HKTVmall product page scraping"""
    from firecrawl import FirecrawlApp

    api_key = os.getenv("FIRECRAWL_API_KEY")
    app = FirecrawlApp(api_key=api_key)

    # HKTVmall product page - use a real product URL
    # Format: https://www.hktvmall.com/hktv/zh/main/<Store>/<Category>/p/<ProductID>
    test_url = "https://www.hktvmall.com/hktv/zh/main/%E8%B6%85%E5%B8%82%E7%99%BE%E8%B2%A8/%E9%A3%9F%E5%93%81%E9%A3%B2%E5%93%81/%E5%8D%B3%E9%A3%9F%E9%BA%B5%E7%8E%8B/p/H4455001_S_P00001"
    print(f"\n[TEST] HKTVmall scrape: {test_url}")

    try:
        # SDK v4.x uses scrape() with direct parameters
        result = app.scrape(
            test_url,
            formats=["markdown", "html"],
            only_main_content=True,
            wait_for=3000,
        )

        print(f"[OK] Scrape success!")
        markdown = result.markdown or ''
        print(f"  - Markdown length: {len(markdown)}")
        print(f"  - Title: {result.metadata.title if result.metadata else 'N/A'}")

        if markdown:
            print(f"\n[PREVIEW] First 500 chars:")
            print("-" * 50)
            print(markdown[:500])
            print("-" * 50)

        return True

    except Exception as e:
        print(f"[FAIL] Scrape failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_json_mode():
    """Test JSON Mode structured extraction"""
    from firecrawl import FirecrawlApp
    from pydantic import BaseModel
    from typing import Optional

    api_key = os.getenv("FIRECRAWL_API_KEY")
    app = FirecrawlApp(api_key=api_key)

    class ProductSchema(BaseModel):
        product_name: Optional[str] = None
        current_price: Optional[float] = None
        original_price: Optional[float] = None
        stock_status: Optional[str] = None

    test_url = "https://www.hktvmall.com/hktv/zh/main/%E8%B6%85%E5%B8%82%E7%99%BE%E8%B2%A8/%E9%A3%9F%E5%93%81%E9%A3%B2%E5%93%81/%E5%8D%B3%E9%A3%9F%E9%BA%B5%E7%8E%8B/p/H4455001_S_P00001"
    print(f"\n[TEST] JSON Mode: {test_url}")

    try:
        # SDK v4.x: JSON format with schema
        result = app.scrape(
            test_url,
            formats=[
                {
                    "type": "json",
                    "schema": ProductSchema.model_json_schema()
                },
                "markdown"
            ],
            only_main_content=True,
            wait_for=3000,
        )

        print(f"[OK] JSON Mode success!")
        json_data = result.json if hasattr(result, 'json') else {}
        print(f"  - Extracted data: {json_data}")

        return True

    except Exception as e:
        print(f"[FAIL] JSON Mode failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_with_prompt():
    """Test extraction with prompt (no schema)"""
    from firecrawl import FirecrawlApp

    api_key = os.getenv("FIRECRAWL_API_KEY")
    app = FirecrawlApp(api_key=api_key)

    test_url = "https://www.hktvmall.com/hktv/zh/main/%E8%B6%85%E5%B8%82%E7%99%BE%E8%B2%A8/%E9%A3%9F%E5%93%81%E9%A3%B2%E5%93%81/%E5%8D%B3%E9%A3%9F%E9%BA%B5%E7%8E%8B/p/H4455001_S_P00001"
    print(f"\n[TEST] Prompt extraction: {test_url}")

    try:
        # SDK v4.x: JSON format with prompt
        result = app.scrape(
            test_url,
            formats=[
                {
                    "type": "json",
                    "prompt": "Extract the product name, current price, original price, and stock status from this e-commerce product page. Return in JSON format."
                },
                "markdown"
            ],
            only_main_content=True,
            wait_for=3000,
        )

        print(f"[OK] Prompt extraction success!")
        json_data = result.json if hasattr(result, 'json') else {}
        print(f"  - Extracted: {json_data}")

        return True

    except Exception as e:
        print(f"[FAIL] Prompt extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_map_discover():
    """Test Map feature to discover product URLs"""
    from firecrawl import FirecrawlApp

    api_key = os.getenv("FIRECRAWL_API_KEY")
    app = FirecrawlApp(api_key=api_key)

    base_url = "https://www.hktvmall.com"
    print(f"\n[TEST] Map discover: {base_url}")

    try:
        result = app.map(base_url, search="product", limit=20)
        links = result.links if hasattr(result, 'links') and result.links else []
        print(f"[OK] Map success! Found {len(links)} URLs")

        # Extract URL strings from link objects
        urls = []
        for link in links[:10]:
            # Link might be a string or an object with 'url' attribute
            if isinstance(link, str):
                url = link
            elif hasattr(link, 'url'):
                url = link.url
            else:
                url = str(link)
            urls.append(url)
            print(f"  - {url[:100]}...")

        return urls

    except Exception as e:
        print(f"[FAIL] Map failed: {e}")
        import traceback
        traceback.print_exc()
        return []


def test_real_product(url: str):
    """Test scraping a real product URL"""
    from firecrawl import FirecrawlApp

    api_key = os.getenv("FIRECRAWL_API_KEY")
    app = FirecrawlApp(api_key=api_key)

    print(f"\n[TEST] Real product scrape: {url}")

    try:
        result = app.scrape(
            url,
            formats=[
                {
                    "type": "json",
                    "prompt": "Extract: product name, current price (HKD), original price (HKD), stock status, brand. Return as JSON."
                },
                "markdown"
            ],
            only_main_content=True,
            wait_for=5000,
        )

        print(f"[OK] Scrape success!")
        markdown = result.markdown or ''
        print(f"  - Markdown length: {len(markdown)}")
        print(f"  - Title: {result.metadata.title if result.metadata else 'N/A'}")

        json_data = result.json if hasattr(result, 'json') else {}
        print(f"  - Extracted: {json_data}")

        if markdown:
            print(f"\n[PREVIEW] First 800 chars:")
            print("-" * 50)
            print(markdown[:800])
            print("-" * 50)

        return True

    except Exception as e:
        print(f"[FAIL] Scrape failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Firecrawl Scrape Test")
    print("=" * 60)

    # Test 1: Basic scrape
    if not test_basic_scrape():
        print("\n[WARN] Basic scrape failed, stopping tests")
        sys.exit(1)

    # Test 2: Map to discover product URLs
    product_urls = test_map_discover()

    # Test 3: Scrape a real product if found
    if product_urls:
        # Filter for product pages (containing /p/)
        real_products = [u for u in product_urls if '/p/' in u]
        if real_products:
            test_real_product(real_products[0])
        else:
            print("\n[INFO] No product URLs found in map results")
    else:
        # Fallback: try a known category page
        print("\n[INFO] Map failed, trying category page...")
        test_real_product("https://www.hktvmall.com/hktv/zh/main/home")

    print("\n" + "=" * 60)
    print("Tests completed")
    print("=" * 60)
