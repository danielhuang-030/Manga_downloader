"""Downloader 合作式取消 — 最小單元測試（無瀏覽器）。"""

import threading

import pytest

from downloader import Downloader, DownloadCancelled


def test_check_cancel_raises_when_event_set():
    ev = threading.Event()
    ev.set()
    d = object.__new__(Downloader)
    d._cancel_event = ev
    with pytest.raises(DownloadCancelled):
        Downloader._check_cancel(d)
