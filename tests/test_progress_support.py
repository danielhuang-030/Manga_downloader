"""progress_support — 無瀏覽器單元測試。"""

from progress_support import emit_progress


def test_emit_progress_invokes_reporter():
    seen = []
    emit_progress(lambda d: seen.append(d), {"type": "run_started"})
    assert seen == [{"type": "run_started"}]


def test_emit_progress_none_reporter():
    emit_progress(None, {"type": "run_started"})
