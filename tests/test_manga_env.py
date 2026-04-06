"""TDD: manga_env — parse .env-related strings and folder sanitization (no browser)."""

import pytest

from manga_env import (
    DEFAULT_VIEWER_URL_TEMPLATE,
    parse_manga_ids,
    parse_manga_res,
    parse_viewer_url_template,
    resolve_cookie_header,
    sanitize_download_folder_name,
)


def test_parse_viewer_url_template_default():
    assert parse_viewer_url_template("") == DEFAULT_VIEWER_URL_TEMPLATE
    assert parse_viewer_url_template(None) == DEFAULT_VIEWER_URL_TEMPLATE


def test_parse_viewer_url_template_custom():
    custom = "https://example.com/v/{id}/read"
    assert parse_viewer_url_template(custom) == custom


def test_parse_viewer_url_template_invalid():
    with pytest.raises(ValueError, match="必須包含"):
        parse_viewer_url_template("https://example.com/no-placeholder")


def test_parse_manga_res_valid():
    assert parse_manga_res("1445x2048") == (1445, 2048)


def test_parse_manga_res_invalid():
    with pytest.raises(ValueError):
        parse_manga_res("1445*2048")


def test_parse_manga_ids():
    assert parse_manga_ids("237928, 340012 ,,") == ["237928", "340012"]


def test_resolve_cookie_header_prefers_manga():
    env = {"MANGA_COOKIES": "a=1", "BOOKWALKER_COOKIE": "b=2"}
    assert resolve_cookie_header(env) == "a=1"


def test_resolve_cookie_header_fallback():
    env = {"BOOKWALKER_COOKIE": "b=2"}
    assert resolve_cookie_header(env) == "b=2"


def test_sanitize_pipe_segment():
    assert sanitize_download_folder_name("書名｜BOOK☆WALKER", "99") == "書名"


def test_sanitize_fallback_id():
    assert sanitize_download_folder_name("   ", "237928") == "browserViewer-237928"
