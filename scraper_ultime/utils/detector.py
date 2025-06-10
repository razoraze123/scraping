import requests


CMS_PATTERNS = {
    "woocommerce": ["woocommerce", "wp-content"],
    "shopify": ["cdn.shopify.com", "shopify"],
}


def detect_cms(url: str) -> str:
    try:
        resp = requests.get(url, timeout=10)
        html = resp.text.lower()
        for cms, patterns in CMS_PATTERNS.items():
            if any(p in html for p in patterns):
                return cms
    except Exception:
        pass
    return "unknown"
