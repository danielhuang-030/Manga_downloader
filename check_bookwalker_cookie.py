#!/usr/bin/env python3
"""
Check Bookwalker TW cookie string against a URL using HTTP only (no Chrome).

Use the same Cookie format as main.py: name=value; name2=value2

Examples:
  # Use cookies + first manga_url from main.py (same source as Downloader)
  python check_bookwalker_cookie.py --from-main

  python check_bookwalker_cookie.py --from-main --main-path ./main.py --manga-index 0

  python check_bookwalker_cookie.py --url 'https://...' --cookie 'a=b; c=d'

  BOOKWALKER_COOKIE='a=b; c=d' python check_bookwalker_cookie.py --url '...'

Exit codes: 0 = no login gate detected (cookie may be valid); 1 = login gate; 2 = request error.
"""
import argparse
import importlib.util
import os
import sys

import requests

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
    env = os.environ.get('BOOKWALKER_COOKIE', '').strip()
    if env:
        return env
    return ''


def main():
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
        help='Target URL. With --from-main, optional (overrides manga_url[N]). Otherwise required.',
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
            parser.error('--url is required unless --from-main is used.')

    if not cookie:
        parser.error(
            'No cookie: use --from-main, or pass --cookie / --cookie-file / BOOKWALKER_COOKIE.'
        )

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
