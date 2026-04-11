"""manga_env — HTTP Cookie header Latin-1 coercion (used by check_bookwalker_cookie)."""

from manga_env import coerce_http_cookie_header_latin1


def test_coerce_cookie_header_drops_unicode_ellipsis():
    raw = "a=b;" + "\u2026" + "c=d"
    out, dropped = coerce_http_cookie_header_latin1(raw)

    assert dropped == 1
    assert out == "a=b;c=d"


def test_coerce_cookie_header_keeps_ascii():
    s = "foo=bar; baz=qux"
    out, dropped = coerce_http_cookie_header_latin1(s)

    assert dropped == 0
    assert out == s


def test_coerce_cookie_header_keeps_latin1_supplement():
    s = "x=\xff"
    out, dropped = coerce_http_cookie_header_latin1(s)

    assert dropped == 0
    assert out == s
