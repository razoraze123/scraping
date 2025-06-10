import requests


def detect_cms(url: str) -> str:
    """Detect whether the site uses WooCommerce or Shopify."""
    try:
        resp = requests.get(url, timeout=10)
        html = resp.text.lower()
        if "woocommerce" in html or "wp-content" in html:
            return "woocommerce"
        if "cdn.shopify.com" in html or "shopify" in html:
            return "shopify"
    except Exception:
        pass
    return "unknown"
