"""
HKTVmall Stock Probe v3 — 雙法並用
=====================================
方法 A（首選）：產品頁 SSR HTML parse
  - 唔需要 session / cookie
  - 直接讀 stockLevel JSON
  - 快（無購物車操作）

方法 B（備用）：購物車探測法
  - 加入 99 件 → quantityAdded = 實際庫存上限
  - 需要 config/hktvmall-cookie.json
  - Fallback when product page has no SSR data

Usage:
  python scripts/hktvmall_stock_probe.py H0888001_S_10161559
  python scripts/hktvmall_stock_probe.py SKU1 SKU2 SKU3
  python scripts/hktvmall_stock_probe.py --file skus.txt
  python scripts/hktvmall_stock_probe.py --file skus.txt --json --output results.json
  python scripts/hktvmall_stock_probe.py H0888001_S_10161559 --method cart
  python scripts/hktvmall_stock_probe.py H0888001_S_10161559 --method page
"""

import sys
import json
import time
import re
import argparse
import requests
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).parent.parent
CONFIG_FILE = BASE_DIR / "config" / "hktvmall-cookie.json"
BASE_URL = "https://www.hktvmall.com"
PROBE_QTY = 99

HEADERS_HTML = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
}
HEADERS_JSON = {
    **HEADERS_HTML,
    "Accept": "application/json, text/plain, */*",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": f"{BASE_URL}/hktv/zh/main",
}


# ─────────────────────────────────────────────
# Method A: Product Page HTML Parse
# ─────────────────────────────────────────────

def build_product_url(sku: str) -> str:
    """Build product URL from SKU."""
    parts = sku.split("_S_")
    store = parts[0] if len(parts) == 2 else sku
    return f"{BASE_URL}/hktv/zh/main/search/s/{store}/p/{sku}"


def parse_product_page(html: str) -> dict:
    """Parse stock data from product page SSR HTML."""
    result = {"stock_level": None, "stock_status": None, "name": None, "price": None, "method": "page"}

    # stockLevel (numeric) — take first occurrence
    levels = re.findall(r'"stockLevel"\s*:\s*(\d+)', html)
    if levels:
        result["stock_level"] = int(levels[0])

    # stockLevelStatus
    statuses = re.findall(r'"stockLevelStatus"\s*:\s*\{[^}]*"code"\s*:\s*"(\w+)"', html)
    if statuses:
        result["stock_status"] = statuses[0]  # "inStock", "outOfStock", "lowStock"
    else:
        statuses2 = re.findall(r'"stockLevelStatus"\s*:\s*"(\w+)"', html)
        if statuses2:
            result["stock_status"] = statuses2[0]

    # Product name: page <title> (more reliable than og:title in this app)
    title_m = re.search(r'<title>([^<]+)</title>', html)
    if title_m:
        name = title_m.group(1)
        # Strip " | HKTVmall 香港最大網購平台" and similar suffixes
        name = re.sub(r'\s*\|\s*HKTVmall.*$', '', name).strip()
        if name:
            result["name"] = name

    # Price — "$value" pattern, last unique value = sale price
    # e.g. ["64.90", "64.90", "46.70"] → sale price = 46.70
    prices = re.findall(r'"\$\s*([\d,]+\.?\d*)"', html)
    if not prices:
        # fallback: "value": 46.70 pattern
        prices = re.findall(r'"value"\s*:\s*([\d]+(?:\.\d+)?)', html)
    if prices:
        # Remove commas, convert to float, take the LAST distinct value (sale price)
        floats = []
        seen_p = set()
        for p in prices:
            v = float(p.replace(",", ""))
            if v not in seen_p:
                seen_p.add(v)
                floats.append(v)
        if floats:
            result["price"] = floats[-1]  # Last unique = lowest/sale price

    return result


def probe_via_page(session: requests.Session, sku: str) -> dict:
    """Probe stock using product page HTML parsing."""
    result = {
        "sku": sku, "stock_level": None, "in_stock": None,
        "name": None, "price": None, "method": "page",
        "error": None, "probed_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        url = build_product_url(sku)
        resp = session.get(url, headers=HEADERS_HTML, timeout=15, allow_redirects=True)
        if resp.status_code == 404:
            result["error"] = "404 Not Found"
            return result
        resp.raise_for_status()

        parsed = parse_product_page(resp.text)

        if parsed["stock_level"] is not None:
            result["stock_level"] = parsed["stock_level"]
            result["in_stock"] = parsed["stock_level"] > 0
        elif parsed["stock_status"]:
            result["in_stock"] = parsed["stock_status"].lower() == "instock"
            result["stock_level"] = -1 if result["in_stock"] else 0
        else:
            # No SSR data — product page is likely client-rendered
            result["error"] = "no_ssr_data"

        result["name"] = parsed["name"]
        result["price"] = parsed["price"]
    except Exception as e:
        result["error"] = str(e)
    return result


# ─────────────────────────────────────────────
# Method B: Shopping Cart Probe
# ─────────────────────────────────────────────

def load_cookies() -> dict:
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"Cookie file not found: {CONFIG_FILE}")
    return json.loads(CONFIG_FILE.read_text(encoding="utf-8")).get("cookies", {})


def get_csrf(session: requests.Session) -> str:
    resp = session.get(f"{BASE_URL}/hktv/zh/main", headers=HEADERS_JSON, timeout=15)
    m = re.search(r'CSRFToken[^0-9a-f]*([0-9a-f-]{36})', resp.text, re.IGNORECASE)
    if not m:
        raise ValueError("CSRF token not found")
    return m.group(1)


def cart_add(session: requests.Session, sku: str, qty: int, csrf: str) -> dict:
    resp = session.post(
        f"{BASE_URL}/hktv/zh/cart/add",
        headers={**HEADERS_JSON, "Content-Type": "application/x-www-form-urlencoded"},
        data=f"productCodePost={sku}&qty={qty}&CSRFToken={csrf}",
        timeout=15,
    )
    if resp.status_code == 403:
        raise PermissionError("Auth expired (403)")
    resp.raise_for_status()
    return resp.json()


def cart_remove(session: requests.Session, sku: str):
    """Remove all qty of a SKU from cart."""
    try:
        session.post(
            f"{BASE_URL}/zh/hktvfrontend/v1/cart/express/remove_item_from_cart",
            headers={**HEADERS_JSON, "Content-Type": "application/json"},
            json={"sku": sku},
            timeout=10,
        )
    except Exception:
        pass


def probe_via_cart(session: requests.Session, sku: str, csrf: str) -> dict:
    """Probe stock by adding 99 items and reading quantityAdded."""
    result = {
        "sku": sku, "stock_level": None, "in_stock": None,
        "name": None, "price": None, "method": "cart",
        "error": None, "probed_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        add_resp = cart_add(session, sku, PROBE_QTY, csrf)
        status = add_resp.get("statusCode", "")

        if status == "success":
            qty_raw = add_resp.get("quantityAdded", "")
            qty = int(qty_raw) if str(qty_raw).strip().isdigit() else None
            result["stock_level"] = qty if qty is not None else -1
            result["in_stock"] = (qty or 1) > 0  # -1 means "has stock, exact unknown"
        else:
            result["stock_level"] = 0
            result["in_stock"] = False
            result["error"] = f"cart_status={status}"
    except PermissionError as e:
        result["error"] = f"auth: {e}"
    except Exception as e:
        result["error"] = str(e)
    finally:
        cart_remove(session, sku)
    return result


# ─────────────────────────────────────────────
# Main Probe Logic
# ─────────────────────────────────────────────

def probe_sku(sku: str, page_session: requests.Session,
              cart_session: requests.Session | None, csrf: str | None,
              method: str = "auto") -> dict:
    """
    Probe a single SKU.
    method: "auto" | "page" | "cart"
    auto = try page first, fallback to cart if no SSR data
    """
    if method == "cart" and cart_session and csrf:
        return probe_via_cart(cart_session, sku, csrf)

    if method in ("page", "auto"):
        r = probe_via_page(page_session, sku)
        if method == "page" or r.get("error") != "no_ssr_data":
            return r
        # Fallback to cart
        if cart_session and csrf:
            r2 = probe_via_cart(cart_session, sku, csrf)
            r2["method"] = "cart_fallback"
            return r2
        return r  # Return page result even with no_ssr_data error

    return probe_via_page(page_session, sku)


def probe_batch(skus: list[str], method: str = "auto", verbose: bool = True) -> list[dict]:
    """Probe a batch of SKUs."""
    page_session = requests.Session()
    cart_session = None
    csrf = None

    # Init cart session if needed
    if method in ("cart", "auto"):
        try:
            cookies = load_cookies()
            cart_session = requests.Session()
            cart_session.cookies.update(cookies)
            csrf = get_csrf(cart_session)
            if verbose:
                print(f"Cart session ready (CSRF: {csrf[:8]}...)")
        except Exception as e:
            if method == "cart":
                raise
            if verbose:
                print(f"Cart session unavailable ({e}), using page method only")

    results = []
    for i, sku in enumerate(skus):
        if verbose:
            print(f"[{i+1}/{len(skus)}] {sku} ", end="", flush=True)

        r = probe_sku(sku, page_session, cart_session, csrf, method)
        results.append(r)

        if verbose:
            if r["error"] and r["error"] != "no_ssr_data":
                print(f"ERR: {r['error']}")
            elif r["in_stock"] is True:
                lvl = f"{r['stock_level']}" if r["stock_level"] and r["stock_level"] > 0 else ">=1"
                name = (r["name"] or "")[:35]
                print(f"IN STOCK x{lvl} | ${r['price'] or '?'} | {name} [{r['method']}]")
            elif r["in_stock"] is False:
                print(f"OUT OF STOCK [{r['method']}]")
            else:
                print(f"UNKNOWN [{r['method']}] {r.get('error','')}")

        if i < len(skus) - 1:
            time.sleep(1.0)

    return results


def main():
    parser = argparse.ArgumentParser(description="HKTVmall Stock Probe v3")
    parser.add_argument("skus", nargs="*", help="SKU(s) to probe")
    parser.add_argument("--file", "-f", help="File with one SKU per line")
    parser.add_argument("--method", choices=["auto", "page", "cart"], default="auto",
                        help="Probe method (default: auto)")
    parser.add_argument("--json", action="store_true", help="Output JSON only")
    parser.add_argument("--output", "-o", help="Save results to JSON file")
    args = parser.parse_args()

    skus = list(args.skus)
    if args.file:
        p = Path(args.file)
        if p.exists():
            skus += [l.strip() for l in p.read_text(encoding="utf-8").splitlines()
                     if l.strip() and not l.startswith("#")]

    if not skus:
        parser.print_help()
        print("\nExample: python scripts/hktvmall_stock_probe.py H0888001_S_10161559")
        sys.exit(1)

    verbose = not args.json
    results = probe_batch(skus, method=args.method, verbose=verbose)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(
            json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        if verbose:
            print(f"\nSaved {len(results)} results to {args.output}")

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    elif verbose:
        print("\n" + "=" * 55)
        ok = [r for r in results if r["in_stock"]]
        no = [r for r in results if r["in_stock"] is False]
        err = [r for r in results if r["error"] and r["error"] != "no_ssr_data"]
        page_m = [r for r in results if "page" in r.get("method", "")]
        cart_m = [r for r in results if "cart" in r.get("method", "")]
        print(f"Summary: {len(ok)} in-stock | {len(no)} out-of-stock | {len(err)} errors")
        print(f"Methods: {len(page_m)} page | {len(cart_m)} cart")


if __name__ == "__main__":
    main()
