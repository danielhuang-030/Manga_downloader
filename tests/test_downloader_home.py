"""HOME for undetected_chromedriver — Docker numeric user often had HOME=/ → /.local permission error."""

import os
from pathlib import Path

import pytest


def _downloader_mod():
    pytest.importorskip("undetected_chromedriver")
    import downloader

    return downloader


def test_ensure_writable_home_redirects_when_home_is_root(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", "/")
    monkeypatch.delenv("MANGA_RUNTIME_HOME", raising=False)

    downloader = _downloader_mod()
    downloader._ensure_writable_home_for_uc()

    expected = tmp_path / ".manga-runtime"
    assert os.environ["HOME"] == str(expected.resolve())
    assert expected.is_dir()


def test_ensure_writable_home_respects_manga_runtime_home(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    custom = tmp_path / "custom-uc-home"
    monkeypatch.setenv("MANGA_RUNTIME_HOME", str(custom))
    monkeypatch.setenv("HOME", "/")

    downloader = _downloader_mod()
    downloader._ensure_writable_home_for_uc()

    assert os.environ["HOME"] == str(custom.resolve())
    assert custom.is_dir()
