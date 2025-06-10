import pytest
import requests_mock

from scraper_ultime.utils.static_scraper import StaticScraper


def test_get_soup_http_error(tmp_path):
    url = "https://example.com/notfound"
    scraper = StaticScraper(url, selectors={}, output_dir=tmp_path.as_posix())
    with requests_mock.Mocker() as m:
        m.get(url, status_code=404)
        with pytest.raises(RuntimeError):
            scraper.get_soup(url)
