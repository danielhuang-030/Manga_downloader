#!/usr/bin/env python3
"""
Check Bookwalker TW cookie string against a URL using HTTP only (no Chrome).

Cookie 格式與 Downloader 相同：name=value; name2=value2

預設會載入目前目錄的 .env（python-dotenv）。優先使用 MANGA_COOKIES，否則 BOOKWALKER_COOKIE。

Examples:
  # 使用 .env 內的 cookie（與 main_env.py 相同來源），並以 MANGA_IDS 第一個 ID 組 viewer URL（未傳 --url 時）
  python check_bookwalker_cookie.py

  # 仍支援自舊版 main.py 讀取（--from-main）
  python check_bookwalker_cookie.py --from-main

  python check_bookwalker_cookie.py --from-main --main-path ./legacy_main.py --manga-index 0

  python check_bookwalker_cookie.py --url 'https://...' --cookie 'a=b; c=d'

Exit codes: 0 = no login gate detected (cookie may be valid); 1 = login gate; 2 = request / cookie format error (e.g. Cookie contains non-Latin-1 characters — fix .env and retry).
"""
import argparse
import importlib.util
import os
import sys

import requests

from manga_env import (
    coerce_http_cookie_header_latin1,
    parse_manga_ids,
    parse_viewer_url_template,
    resolve_cookie_header,
)
from website_actions.bookwalker_nfbr_wait import bookwalker_tw_login_gate_in_markup


def _load_settings_from_main(path):
    """Load `settings` dict from a main.py file without importing package name `main`."""
    abs_path = os.path.abspath(path)
    spec = importlib.util.spec_from_file_location('manga_main_cookie_check', abs_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, 'settings'):
        raise ValueError('%s has no `settings` dict' % path)
    return mod.settings


def _load_cookie(args):
    if args.cookie_file:
        with open(args.cookie_file, encoding='utf-8') as f:
            return f.read().strip()
    if args.cookie is not None:
        return args.cookie.strip()
    return resolve_cookie_header(os.environ)


def main():
    from dotenv import load_dotenv

    load_dotenv()

    parser = argparse.ArgumentParser(
        description='Verify Bookwalker TW cookies with a GET request (no browser).',
    )
    parser.add_argument(
        '--from-main',
        action='store_true',
        help='Load cookies from main.py `settings["cookies"]`; default URL = manga_url[manga-index].',
    )
    parser.add_argument(
        '--main-path',
        default='main.py',
        metavar='PATH',
        help='Path to main.py (with --from-main). Default: main.py in current directory.',
    )
    parser.add_argument(
        '--manga-index',
        type=int,
        default=0,
        metavar='N',
        help='Which settings["manga_url"][N] to use when --from-main and --url is omitted. Default: 0.',
    )
    parser.add_argument(
        '--url',
        default=None,
        metavar='URL',
        help='Target URL. Optional if MANGA_IDS is set (uses first id as browserViewer URL). With --from-main, optional (overrides manga_url[N]).',
    )
    parser.add_argument(
        '--cookie',
        default=None,
        help='Cookie header value (semicolon-separated). Ignored when --from-main is set.',
    )
    parser.add_argument(
        '--cookie-file',
        dest='cookie_file',
        default=None,
        metavar='PATH',
        help='File containing one line of cookies. Ignored when --from-main is set.',
    )
    args = parser.parse_args()

    cookie = ''
    url = args.url

    if args.from_main:
        try:
            settings = _load_settings_from_main(args.main_path)
        except (OSError, ValueError) as err:
            print('Failed to load main.py:', err, file=sys.stderr)
            return 2
        cookie = settings.get('cookies') or ''
        if isinstance(cookie, bytes):
            cookie = cookie.decode('utf-8', errors='replace')
        cookie = str(cookie).strip()
        if not url:
            manga_urls = settings.get('manga_url') or []
            if not manga_urls:
                print('main.py settings has no manga_url list.', file=sys.stderr)
                return 2
            if args.manga_index < 0 or args.manga_index >= len(manga_urls):
                print(
                    'manga_index %d out of range (0..%d).'
                    % (args.manga_index, len(manga_urls) - 1),
                    file=sys.stderr,
                )
                return 2
            url = manga_urls[args.manga_index]
        print('Cookie source: %s' % os.path.abspath(args.main_path))
    else:
        cookie = _load_cookie(args)
        if not url:
            ids = parse_manga_ids(os.environ.get('MANGA_IDS', ''))
            if ids:
                tpl = parse_viewer_url_template(os.environ.get('MANGA_VIEWER_URL_TEMPLATE'))
                url = tpl.format(id=ids[0])
        if not url:
            parser.error(
                '--url is required unless --from-main is used or MANGA_IDS provides a default.',
            )

    if not cookie:
        parser.error(
            'No cookie: use --from-main, or .env MANGA_COOKIES / BOOKWALKER_COOKIE, '
            'or pass --cookie / --cookie-file.',
        )

    cookie, dropped = coerce_http_cookie_header_latin1(cookie)
    if dropped:
        print(
            'Error: Cookie contains %d character(s) that cannot be sent in HTTP headers (must be Latin-1). '
            'Common cause: Unicode ellipsis … (U+2026) from a truncated copy — the middle of a token may be missing.\n'
            'Fix: In browser DevTools → Application → Cookies → https://www.bookwalker.com.tw , '
            'copy the full raw cookie string (or re-export), update MANGA_COOKIES in .env, retry.'
            % dropped,
            file=sys.stderr,
        )
        return 2
    if not cookie.strip():
        parser.error('Cookie is empty; set MANGA_COOKIES / BOOKWALKER_COOKIE or use --cookie / --from-main.')

    headers = {
        'Cookie': cookie,
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    }

    try:
        resp = requests.get(
            url,
            headers=headers,
            timeout=45,
            allow_redirects=True,
        )
    except requests.RequestException as err:
        print('HTTP error:', err, file=sys.stderr)
        return 2

    html = resp.text or ''
    print('URL:', url)
    print('HTTP', resp.status_code, 'final URL:', resp.url)

    if bookwalker_tw_login_gate_in_markup(html):
        print('Result: INVALID — response looks like 「請登入會員」gate (session not accepted for this URL).')
        return 1

    if 'pageSliderCounter' in html or 'NFBR' in html:
        print('Result: OK — response contains reader markers (NFBR / pageSliderCounter).')
        return 0

    print(
        'Result: UNCLEAR — no login gate in HTML, but no NFBR/pageSliderCounter either. '
        'Might be a redirect, challenge page, or JS-only shell; try the same URL in a browser.'
    )
    return 0


if __name__ == '__main__':
    sys.exit(main() or 0)
