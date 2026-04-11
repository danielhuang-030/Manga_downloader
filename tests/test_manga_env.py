"""TDD: manga_env — parse .env-related strings and folder sanitization (no browser)."""

import pytest

from manga_env import (
    DEFAULT_VIEWER_URL_TEMPLATE,
    append_parsed_id_to_manga_ids,
    extract_viewer_id_from_url,
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


def test_extract_viewer_id_default_template():
    tpl = parse_viewer_url_template("")
    url = "https://www.bookwalker.com.tw/browserViewer/237928/read"
    assert extract_viewer_id_from_url(url, tpl) == "237928"


def test_extract_viewer_id_strips_query_before_match():
    tpl = parse_viewer_url_template("")
    url = "https://www.bookwalker.com.tw/browserViewer/237928/read?ref=1"
    assert extract_viewer_id_from_url(url, tpl) == "237928"


def test_extract_viewer_id_custom_template():
    tpl = parse_viewer_url_template("https://example.com/v/{id}/end")
    assert extract_viewer_id_from_url("https://example.com/v/42/end", tpl) == "42"


def test_extract_viewer_id_no_match():
    tpl = parse_viewer_url_template("https://example.com/v/{id}/end")
    assert extract_viewer_id_from_url("https://evil.com/other", tpl) is None


def test_extract_viewer_id_template_must_have_exactly_one_id_placeholder():
    with pytest.raises(ValueError, match="恰好一個"):
        extract_viewer_id_from_url(
            "https://example.com/v/1/end",
            "https://example.com/v/{id}/end/{id}",
        )
    with pytest.raises(ValueError, match="恰好一個"):
        extract_viewer_id_from_url(
            "https://example.com/v/1/end",
            "https://example.com/v/only-no-placeholder",
        )


def test_parse_manga_res_valid():
    assert parse_manga_res("1445x2048") == (1445, 2048)


def test_parse_manga_res_invalid():
    with pytest.raises(ValueError):
        parse_manga_res("1445*2048")


def test_parse_manga_ids():
    assert parse_manga_ids("237928, 340012 ,,") == ["237928", "340012"]


def test_append_parsed_id_appends_and_normalizes_commas():
    new_csv, status = append_parsed_id_to_manga_ids("10, 20", "99")
    assert status == "appended"
    assert new_csv == "10,20,99"


def test_append_parsed_id_duplicate():
    new_csv, status = append_parsed_id_to_manga_ids("10,20", "20")
    assert status == "duplicate"
    assert new_csv == "10,20"


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
