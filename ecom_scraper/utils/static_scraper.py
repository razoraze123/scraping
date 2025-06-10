import os
import re
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from tqdm import tqdm


class StaticScraper:
    def __init__(self, base_url: str, output_dir: str, fetcher=None):
        """Initialize the scraper.

        Parameters
        ----------
        base_url : str
            URL of the collection page.
        output_dir : str
            Where outputs will be stored.
        fetcher : callable or None
            Optional function used to fetch raw HTML from a URL. It should
            accept a URL and return the HTML string. When not provided,
            ``requests`` will be used.
        """
        self.base_url = base_url
        self.output_dir = output_dir
        self.session = requests.Session()
        self.fetcher = fetcher

    def get_soup(self, url: str) -> BeautifulSoup:
        """Return a BeautifulSoup object for the given URL."""
        if self.fetcher:
            html = self.fetcher(url)
        else:
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()
            html = resp.text
        return BeautifulSoup(html, "html.parser")

    def scrape_collection(self) -> list:
        """Scrape product links from a collection page with basic pagination."""
        products = []
        url = self.base_url
        visited = set()
        while url and url not in visited:
            visited.add(url)
            soup = self.get_soup(url)
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if "/product" in href or "/products" in href:
                    name = a.get_text(strip=True) or os.path.basename(href)
                    link = urljoin(url, href)
                    products.append({"name": name, "link": link})
            next_link = soup.find("a", attrs={"rel": "next"}) or soup.find("a", class_=re.compile("next"))
            if next_link:
                url = urljoin(url, next_link.get("href"))
            else:
                url = None
        return products

    def download_image(self, url: str, folder: str) -> str:
        os.makedirs(folder, exist_ok=True)
        img_name = os.path.basename(url.split("?")[0])
        path = os.path.join(folder, img_name)
        try:
            r = self.session.get(url, timeout=10)
            if r.status_code == 200:
                with open(path, "wb") as f:
                    f.write(r.content)
                return path
        except Exception:
            pass
        return ""

    def scrape_product(self, product_url: str) -> dict:
        soup = self.get_soup(product_url)
        name_tag = soup.find("h1")
        name = name_tag.get_text(strip=True) if name_tag else product_url
        # Description
        desc_div = soup.find("div", class_=re.compile("description", re.I))
        description = desc_div.get_text("\n", strip=True) if desc_div else ""
        desc_path = os.path.join(self.output_dir, "descriptions", f"{self.sanitize(name)}.txt")
        os.makedirs(os.path.dirname(desc_path), exist_ok=True)
        with open(desc_path, "w", encoding="utf-8") as f:
            f.write(description)
        # Images
        image_urls = []
        for img in soup.find_all("img"):
            src = img.get("src")
            if src and src.startswith("http"):
                image_urls.append(src)
        saved_images = []
        folder = os.path.join(self.output_dir, "images", self.sanitize(name))
        for url in tqdm(image_urls, desc=f"Images for {name}"):
            path = self.download_image(url, folder)
            if path:
                saved_images.append(path)
        # Variants
        variants = []
        for select in soup.find_all("select"):
            opts = [opt.get_text(strip=True) for opt in select.find_all("option") if opt.get("value")]
            if opts:
                variants.append(opts)
        product_type = "variable" if variants else "simple"
        return {
            "name": name,
            "link": product_url,
            "type": product_type,
            "variants": variants,
            "images": image_urls,
            "description_path": desc_path,
        }

    @staticmethod
    def sanitize(text: str) -> str:
        return re.sub(r"[^a-zA-Z0-9_-]", "_", text)
