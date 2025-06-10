import argparse
import yaml
from .utils.static_scraper import StaticScraper
from .utils.dynamic_scraper import DynamicFetcher
from .utils.detector import detect_cms
from .utils.output import save_data


def load_config(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser(description="E-commerce scraper")
    parser.add_argument('--config', required=True, help='Path to config.yaml')
    args = parser.parse_args()
    config = load_config(args.config)

    url = config.get('url')
    mode = config.get('mode', 'static')
    output_format = config.get('output_format', 'csv')
    output_dir = config.get('output_dir', 'outputs')
    headless = config.get('headless', True)

    cms = detect_cms(url)
    print(f"Detected CMS: {cms}")

    fetcher = None
    if mode == 'dynamic':
        dyn = DynamicFetcher(headless=headless)

        def fetch(url_to_fetch: str) -> str:
            return dyn.fetch(url_to_fetch)

        fetcher = fetch
    scraper = StaticScraper(url, output_dir, fetcher=fetcher)

    products_info = []
    products = scraper.scrape_collection()
    print(f"Found {len(products)} products")
    for p in products:
        info = scraper.scrape_product(p['link'])
        products_info.append(info)

    save_data(products_info, output_dir, fmt=output_format)
    if mode == 'dynamic':
        dyn.close()
    print('Scraping finished')


if __name__ == '__main__':
    main()
