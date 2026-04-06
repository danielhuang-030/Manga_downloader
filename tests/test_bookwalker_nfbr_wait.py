"""Unit tests for bookwalker_nfbr_wait (no real browser)."""

from unittest.mock import MagicMock

import pytest


class TestBookwalkerTwSessionGatePresent:
    """bookwalker_tw_session_gate_present — detect SweetAlert login gate."""

    @pytest.fixture
    def gate_fn(self):
        from website_actions.bookwalker_nfbr_wait import bookwalker_tw_session_gate_present

        return bookwalker_tw_session_gate_present

    def test_true_when_title_is_login_prompt(self, gate_fn):
        d = MagicMock()
        d.title = '請登入會員'
        d.page_source = '<html></html>'
        assert gate_fn(d) is True

    def test_true_when_swal_and_chinese_login_in_source(self, gate_fn):
        d = MagicMock()
        d.title = ''
        d.page_source = (
            "<script>Swal.fire({title: '請登入會員',confirmButtonText: '確定',})</script>"
        )
        assert gate_fn(d) is True

    def test_false_when_nfbr_reader_typical_page(self, gate_fn):
        d = MagicMock()
        d.title = 'Some manga title'
        d.page_source = '<html><body><iframe src="reader"></iframe></body></html>'
        assert gate_fn(d) is False

    def test_false_when_chinese_phrase_without_swal(self, gate_fn):
        d = MagicMock()
        d.title = 'x'
        d.page_source = '請登入會員 but no swal markers'
        assert gate_fn(d) is False


class TestBookwalkerTwLoginGateInMarkup:
    """bookwalker_tw_login_gate_in_markup — HTML-only gate (HTTP/curl)."""

    @pytest.fixture
    def fn(self):
        from website_actions.bookwalker_nfbr_wait import bookwalker_tw_login_gate_in_markup

        return bookwalker_tw_login_gate_in_markup

    def test_swal_gate(self, fn):
        html = "<script>Swal.fire({title: '請登入會員'})</script>"
        assert fn(html) is True

    def test_title_gate(self, fn):
        html = '<html><head><title>請登入會員</title></head><body>x</body></html>'
        assert fn(html) is True

    def test_not_gate_without_markers(self, fn):
        assert fn('請登入會員 plain text no swal title') is False

    def test_empty(self, fn):
        assert fn('') is False


class TestEnsureNfbrMoveToPageReady:
    """ensure_nfbr_move_to_page_ready — probe script result."""

    @pytest.fixture
    def ensure(self):
        from website_actions.bookwalker_nfbr_wait import ensure_nfbr_move_to_page_ready

        return ensure_nfbr_move_to_page_ready

    def test_ok(self, ensure):
        d = MagicMock()
        d.execute_script.return_value = {'ok': True, 'keys': ['X3N']}
        ensure(d)

    def test_raises_when_not_ok(self, ensure):
        d = MagicMock()
        d.execute_script.return_value = {
            'ok': False,
            'err': 'no NFBR page mover resolved',
            'keys': ['a', 'b'],
        }
        with pytest.raises(RuntimeError) as ei:
            ensure(d)
        assert 'no NFBR page mover' in str(ei.value)
        assert 'keys=' in str(ei.value)


class TestResolveNfbrMenuAccessorCompat:
    """resolve_nfbr_menu_accessor still exists; delegates to ensure and returns placeholders."""

    def test_returns_deep_tuple(self):
        from website_actions.bookwalker_nfbr_wait import resolve_nfbr_menu_accessor

        d = MagicMock()
        d.execute_script.return_value = {'ok': True, 'keys': []}
        assert resolve_nfbr_menu_accessor(d) == ('', 'deep')


class TestNfbrMoveToPage:
    def test_invokes_execute_script_with_page(self):
        from website_actions.bookwalker_nfbr_wait import nfbr_move_to_page

        d = MagicMock()
        nfbr_move_to_page(d, 7)
        d.execute_script.assert_called_once()
        assert d.execute_script.call_args[0][1] == 7
