"""
Unit tests for pure helpers in downloader.py (no real browser).

TDD: these tests lock behavior for stack upgrades (Python / deps) without E2E.
"""
from unittest.mock import MagicMock, patch

import pytest


class TestGetCookieDict:
    """get_cookie_dict — cookie string → dict (semicolon-separated)."""

    @pytest.fixture
    def get_cookie_dict(self):
        from downloader import get_cookie_dict

        return get_cookie_dict

    def test_single_pair(self, get_cookie_dict):
        assert get_cookie_dict("a=b") == {"a": "b"}

    def test_semicolon_space_separator(self, get_cookie_dict):
        assert get_cookie_dict("a=b; c=d") == {"a": "b", "c": "d"}

    def test_semicolon_only_separator(self, get_cookie_dict):
        assert get_cookie_dict("a=b;c=d") == {"a": "b", "c": "d"}

    def test_value_contains_equals(self, get_cookie_dict):
        assert get_cookie_dict("token=abc=def") == {"token": "abc=def"}

    def test_empty_segment_skipped(self, get_cookie_dict):
        assert get_cookie_dict("a=b; ; c=d") == {"a": "b", "c": "d"}

    def test_multiple_equals_in_value(self, get_cookie_dict):
        assert get_cookie_dict("x=y=z=w") == {"x": "y=z=w"}


class TestStrToDataUri:
    """Downloader.str_to_data_uri — data: URI for --app flag."""

    @pytest.fixture
    def downloader(self):
        with patch("downloader.uc.Chrome") as mock_chrome:
            driver = MagicMock()
            driver.execute_script.return_value = [800, 600]
            driver.execute_cdp_cmd = MagicMock()
            mock_chrome.return_value = driver
            from downloader import Downloader

            d = Downloader(
                manga_url=["https://example.com/book/1"],
                cookies="s=1",
                imgdir=["/tmp/manga_test"],
                res=(800, 600),
            )
            return d

    def test_prefix_and_roundtrip(self, downloader):
        uri = downloader.str_to_data_uri("Manga_downloader")
        assert uri.startswith("data:text/plain;charset=utf-8;base64,")
        import base64

        b64 = uri.split(",", 1)[1]
        assert base64.b64decode(b64).decode("utf-8") == "Manga_downloader"


class TestAddCookies:
    """add_cookies — delegates to driver.add_cookie per key."""

    def test_calls_add_cookie_for_each_key(self):
        from downloader import add_cookies

        driver = MagicMock()
        cookies = {"sid": "abc", "token": "xyz"}
        add_cookies(driver, cookies)
        assert driver.add_cookie.call_count == 2
        driver.add_cookie.assert_any_call({"name": "sid", "value": "abc"})
        driver.add_cookie.assert_any_call({"name": "token", "value": "xyz"})


class TestDownloaderInitPageIndices:
    """start_page / end_page normalization (no download)."""

    @pytest.fixture
    def make_downloader(self):
        def _make(**kwargs):
            defaults = dict(
                manga_url=["https://example.com/book/1"],
                cookies="a=b",
                imgdir=["/tmp/t"],
                res=(800, 600),
            )
            defaults.update(kwargs)
            with patch("downloader.uc.Chrome") as mock_chrome:
                driver = MagicMock()
                driver.execute_script.return_value = [800, 600]
                driver.execute_cdp_cmd = MagicMock()
                mock_chrome.return_value = driver
                from downloader import Downloader

                return Downloader(**defaults)

        return _make

    def test_start_page_none_is_zero(self, make_downloader):
        d = make_downloader(start_page=None)
        assert d.start_page == 0

    def test_start_page_positive_becomes_zero_indexed(self, make_downloader):
        d = make_downloader(start_page=3)
        assert d.start_page == 2

    def test_start_page_zero_or_negative_is_zero(self, make_downloader):
        d = make_downloader(start_page=0)
        assert d.start_page == 0

    def test_file_name_model_padding(self, make_downloader):
        d = make_downloader(number_of_digits=4, file_name_prefix="vol1")
        assert "/vol1_" in d.file_name_model
        assert d.file_name_model.endswith("%04d.png")
