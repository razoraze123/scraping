from __future__ import annotations

import os
import time
from typing import Callable, Dict, List, Optional

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from requests import exceptions as req_exc
from tqdm import tqdm

from .logger import setup_logger


class StaticScraper:
    def __init__(
        self,
        base_url: str,
        selectors: Dict[str, str],
        output_dir: str,
        max_pages: int = 10,
        fetcher: Optional[Callable[[str], str]] = None,
        logger=None,
    ) -> None:
        self.base_url = base_url
        self.selectors = selectors
        self.output_dir = output_dir
        self.max_pages = max_pages
        self.fetcher = fetcher
        self.session = requests.Session()
        self.logger = logger or setup_logger(__name__)

    def get_html(self, url: str) -> str:
        try:
            if self.fetcher:
                return self.fetcher(url)
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()
            return resp.text
        except req_exc.RequestException as exc:
            raise RuntimeError(f"Error fetching {url}: {exc}") from exc

    def get_soup(self, url: str) -> BeautifulSoup:
        html = self.get_html(url)
        return BeautifulSoup(html, "html.parser")

    def scrape_collection(self) -> List[Dict[str, str]]:
        products = []
        url = self.base_url
        pages = 0
        visited = set()
        while url and pages < self.max_pages and url not in visited:
            visited.add(url)
            self.logger.info("Scraping collection page %s", url)
            soup = self.get_soup(url)
            link_sel = self.selectors.get("product_links")
            if not link_sel:
                break
            for tag in soup.select(link_sel):
                href = tag.get("href")
                if href:
                    products.append({"link": requests.compat.urljoin(url, href)})
            next_sel = self.selectors.get("next_page")
            next_link = soup.select_one(next_sel) if next_sel else None
            if next_link:
                href = next_link.get("href")
                url = requests.compat.urljoin(url, href) if href else None
            else:
                url = None
            pages += 1
        return products

    def scrape_product(self, url: str) -> Dict[str, any]:
        html = self.get_html(url)
        return self.parse_product(html, url)

    def parse_product(self, html: str, url: str) -> Dict[str, any]:
        soup = BeautifulSoup(html, "html.parser")
        def text(selector: str) -> str:
            tag = soup.select_one(selector)
            return tag.get_text(strip=True) if tag else ""

        title = text(self.selectors.get("title", "")) or url
        desc_sel = self.selectors.get("description", "")
        description = text(desc_sel)
        image_sel = self.selectors.get("image", "img")
        images = [img.get("src") for img in soup.select(image_sel) if img.get("src")]
        variant_sel = self.selectors.get("variant")
        variants = []
        if variant_sel:
            for opt in soup.select(variant_sel):
                val = opt.get_text(strip=True)
                if val:
                    variants.append(val)

        if description:
            os.makedirs(os.path.join(self.output_dir, "descriptions"), exist_ok=True)
            desc_path = os.path.join(
                self.output_dir,
                "descriptions",
                f"{self.sanitize(title)}.md",
            )
            with open(desc_path, "w", encoding="utf-8") as f:
                f.write(md(description))
        else:
            desc_path = ""

        img_folder = os.path.join(self.output_dir, "images", self.sanitize(title))
        saved_imgs = []
        for src in tqdm(images, desc=f"Images for {title}"):
            if not src.startswith("http"):
                continue
            os.makedirs(img_folder, exist_ok=True)
            name = os.path.basename(src.split("?")[0])
            path = os.path.join(img_folder, name)
            try:
                r = self.session.get(src, timeout=10)
                if r.status_code == 200:
                    with open(path, "wb") as f:
                        f.write(r.content)
                    saved_imgs.append(path)
            except Exception as exc:
                self.logger.warning("Failed to download %s: %s", src, exc)

        product_type = "variable" if variants else "simple"
        return {
            "title": title,
            "link": url,
            "type": product_type,
            "variants": variants,
            "images": saved_imgs,
            "description_path": desc_path,
        }

    @staticmethod
    def sanitize(text: str) -> str:
        return "".join(c if c.isalnum() or c in "-_" else "_" for c in text)
