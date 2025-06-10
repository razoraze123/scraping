import os
import sys
import pytest
import requests_mock

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    ),
)

from ecom_scraper.utils.static_scraper import StaticScraper  # noqa: E402


def test_get_soup_http_error():
    url = 'https://example.com/notfound'
    scraper = StaticScraper(url, output_dir='outputs')
    with requests_mock.Mocker() as m:
        m.get(url, status_code=404)
        with pytest.raises(RuntimeError):
            scraper.get_soup(url)
