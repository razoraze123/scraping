"""High-level runner that orchestrates the ecom_scraper package.

This script provides a single entry point that ties together the
functionalities from :mod:`ecom_scraper`. It loads the configuration,
chooses between static or dynamic scraping, triggers the extraction of
products and finally saves the data to disk.
"""

import argparse
from ecom_scraper.scraper import load_config
from ecom_scraper.utils.detector import detect_cms
from ecom_scraper.utils.static_scraper import StaticScraper
from ecom_scraper.utils.dynamic_scraper import DynamicFetcher
from ecom_scraper.utils.output import save_data


def orchestrate(config_path: str) -> None:
    """Run the full scraping pipeline using *config_path*.

    Parameters
    ----------
    config_path : str
        Path to a YAML configuration file.
    """
    config = load_config(config_path)

    url = config.get("url")
    mode = config.get("mode", "static")
    output_format = config.get("output_format", "csv")
    output_dir = config.get("output_dir", "outputs")
    headless = config.get("headless", True)

    cms = detect_cms(url)
    print(f"Detected CMS: {cms}")

    fetcher = None
    dynamic_fetcher = None
    if mode == "dynamic":
        dynamic_fetcher = DynamicFetcher(headless=headless)
        fetcher = dynamic_fetcher.fetch

    scraper = StaticScraper(url, output_dir, fetcher=fetcher)

    products_info = []
    products = scraper.scrape_collection()
    print(f"Found {len(products)} products")

    for product in products:
        info = scraper.scrape_product(product["link"])
        products_info.append(info)

    save_data(products_info, output_dir, fmt=output_format)

    if dynamic_fetcher:
        dynamic_fetcher.close()

    print("Scraping finished")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the ecom_scraper pipeline")
    parser.add_argument(
        "--config", default="config.yaml", help="Path to the configuration file"
    )
    args = parser.parse_args()
    orchestrate(args.config)


if __name__ == "__main__":
    main()
