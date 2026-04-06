"""Tests for check_bookwalker_cookie helpers (no HTTP)."""

import pytest


def test_load_settings_from_main(tmp_path):
    stub = tmp_path / 'main_stub.py'
    stub.write_text(
        "settings = {'cookies': 'a=b; c=d', 'manga_url': ['https://example.com/viewer']}\n",
        encoding='utf-8',
    )
    from check_bookwalker_cookie import _load_settings_from_main

    s = _load_settings_from_main(str(stub))
    assert s['cookies'] == 'a=b; c=d'
    assert s['manga_url'] == ['https://example.com/viewer']


def test_load_settings_from_main_missing_settings(tmp_path):
    bad = tmp_path / 'bad.py'
    bad.write_text('x = 1\n', encoding='utf-8')
    from check_bookwalker_cookie import _load_settings_from_main

    with pytest.raises(ValueError, match='settings'):
        _load_settings_from_main(str(bad))
