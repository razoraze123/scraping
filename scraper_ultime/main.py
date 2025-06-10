from __future__ import annotations

import argparse
from pathlib import Path
import yaml

from .utils.detector import detect_cms
from .utils.dynamic_scraper import DynamicFetcher
from .utils.output import save_data
from .utils.static_scraper import StaticScraper
from .utils.logger import setup_logger

__all__ = [
    "load_config",
    "save_config",
    "run_scraper",
    "run",
    "main",
]


LOGGER = setup_logger(__name__)


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_config(cfg: dict, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f)


def run_scraper(cfg: dict) -> None:
    url = cfg.get("url")
    mode = cfg.get("mode", "static")
    output_format = cfg.get("output_format", "csv")
    output_dir = cfg.get("output_dir", "outputs")
    headless = cfg.get("headless", True)
    max_pages = cfg.get("max_pages", 10)
    selectors = cfg.get("selectors", {})

    cms = detect_cms(url)
    LOGGER.info("Detected CMS: %s", cms)

    fetcher = None
    dyn = None
    if mode == "dynamic":
        dyn = DynamicFetcher(headless=headless)
        fetcher = dyn.fetch

    scraper = StaticScraper(
        url,
        selectors=selectors,
        output_dir=output_dir,
        max_pages=max_pages,
        fetcher=fetcher,
        logger=LOGGER,
    )

    products_info = []
    products = scraper.scrape_collection()
    LOGGER.info("Found %s products", len(products))
    for p in products:
        info = scraper.scrape_product(p["link"])
        products_info.append(info)

    save_data(products_info, output_dir, fmt=output_format)

    if dyn:
        dyn.close()


def run(config_path: str) -> None:
    cfg = load_config(config_path)
    run_scraper(cfg)


def main() -> None:
    parser = argparse.ArgumentParser(description="Scraper Ultime")
    default_cfg = Path(__file__).with_name("config.yaml")
    parser.add_argument("--config", default=str(default_cfg))
    args = parser.parse_args()
    run(args.config)


if __name__ == "__main__":
    main()
