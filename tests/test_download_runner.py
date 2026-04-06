"""download_runner — 以 Mock 驗證參數轉發（無瀏覽器）。"""

from unittest.mock import MagicMock, patch


@patch("download_runner.Downloader")
def test_run_download_from_dotenv_forwards_progress_reporter(mock_dl):
    mock_inst = MagicMock()
    mock_dl.return_value = mock_inst

    cfg = MagicMock()
    kwargs = {
        "manga_url": [],
        "imgdir": [],
        "cookies": "a=b",
        "res": (1445, 2048),
        "sleep_time": 1.0,
        "viewer_ids": ["1"],
        "viewer_url_template": "https://example.com/{id}/read",
    }

    with patch("download_runner.load_manga_config", return_value=cfg):
        with patch(
            "download_runner.downloader_kwargs_for_env",
            return_value=dict(kwargs),
        ):
            from download_runner import run_download_from_dotenv

            def reporter(ev):
                pass

            run_download_from_dotenv(progress_reporter=reporter)

    mock_dl.assert_called_once()
    call_kw = mock_dl.call_args.kwargs
    assert call_kw["progress_reporter"] is reporter
    mock_inst.download.assert_called_once()
