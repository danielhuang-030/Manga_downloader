"""可選的下載進度回呼（供 Web SSE 與 CLI 共用）。"""


def emit_progress(reporter, payload):
    """若 reporter 非 None，傳入單一 dict（須含 type）。"""
    if reporter is None:
        return
    reporter(dict(payload))
