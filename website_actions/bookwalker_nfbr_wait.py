'''
Shared wait for Bookwalker browserViewer NFBR reader (TW/JP).

NFBR usually lives inside a nested iframe; scripts run on the default document
never see it unless we switch into the reader frame.

If NFBR is slow, #pageSliderCounter (used by get_sum_page_count) may appear first;
we then stay in that frame and keep polling for NFBR.
'''
import logging
import os
import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

# Same ID as bookwalker_*_actions.get_sum_page_count
_PAGE_SLIDER_ID = 'pageSliderCounter'


class BookwalkerSessionError(Exception):
    """
    TW browserViewer rejected the session (cookies missing, expired, or incomplete).

    The page shows SweetAlert「請登入會員」— this is not an NFBR/headless timing issue.
    """


def bookwalker_tw_login_gate_in_markup(html):
    """
    True if raw HTML looks like the TW reader login gate (SweetAlert / title).

    Used by HTTP cookie checks (curl-style) and by session_gate_present (page_source).
    """
    if not html:
        return False
    if '請登入會員' not in html:
        return False
    if 'Swal.fire' in html or 'swal2-' in html:
        return True
    if '<title>請登入會員' in html or '請登入會員</title>' in html:
        return True
    return False


def bookwalker_tw_session_gate_present(driver):
    """
    Return True if the TW reader shows the login gate (invalid session).

    Snapshot: title「請登入會員」+ Swal.fire({title: '請登入會員', ...}) redirecting to bookcase.
    """
    try:
        driver.switch_to.default_content()
    except Exception:
        pass
    try:
        title = driver.title or ''
    except Exception:
        title = ''
    if '請登入會員' in title:
        return True
    try:
        src = driver.page_source or ''
    except Exception:
        src = ''
    return bookwalker_tw_login_gate_in_markup(src)


def _nfbr_ready(driver, script):
    try:
        return bool(driver.execute_script(script))
    except Exception:
        return False


def _find_nfbr_in_frames(driver, script, depth, max_depth):
    """
    DFS: check current context, then each iframe subtree. On success, driver
    stays on the window / frame where NFBR exists.
    """
    if _nfbr_ready(driver, script):
        return True
    if depth >= max_depth:
        return False
    frames = driver.find_elements(By.TAG_NAME, 'iframe')
    for frame in frames:
        try:
            driver.switch_to.frame(frame)
            if _find_nfbr_in_frames(driver, script, depth + 1, max_depth):
                return True
            driver.switch_to.parent_frame()
        except Exception:
            try:
                driver.switch_to.default_content()
            except Exception:
                pass
    return False


def _switch_to_frame_with_element(driver, by, value, depth, max_depth):
    """DFS: leave driver focused on the first frame where the element exists."""
    try:
        if driver.find_elements(by, value):
            return True
    except Exception:
        pass
    if depth >= max_depth:
        return False
    frames = driver.find_elements(By.TAG_NAME, 'iframe')
    for frame in frames:
        try:
            driver.switch_to.frame(frame)
            if _switch_to_frame_with_element(driver, by, value, depth + 1, max_depth):
                return True
            driver.switch_to.parent_frame()
        except Exception:
            try:
                driver.switch_to.default_content()
            except Exception:
                pass
    return False


def _dump_debug_artifacts(driver, base_name='debug_bookwalker_nfbr_timeout'):
    """Write HTML + PNG next to cwd (e.g. /app in Docker) for inspection."""
    try:
        driver.switch_to.default_content()
    except Exception:
        pass
    root = os.getcwd()
    html_path = os.path.join(root, base_name + '.html')
    png_path = os.path.join(root, base_name + '.png')
    try:
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        driver.save_screenshot(png_path)
        logging.error(
            'Saved Bookwalker debug artifacts (open in browser): %s | %s',
            html_path,
            png_path,
        )
    except Exception as err:
        logging.warning('Could not save debug artifacts: %s', err)


def wait_for_nfbr_initializer(
    driver,
    timeout_sec=180,
    poll_sec=2.0,
    log_interval_sec=15,
    max_iframe_depth=8,
):
    """
    Poll until NFBR.a6G.Initializer is ready (including inside nested iframes).

    Logs progress so long waits do not look like a hang.
    """
    deadline = time.monotonic() + timeout_sec
    last_log = 0.0
    script = (
        'return typeof NFBR !== "undefined" && NFBR.a6G && NFBR.a6G.Initializer && '
        'Object.keys(NFBR.a6G.Initializer).length > 0'
    )
    logging.info(
        'Waiting for Bookwalker NFBR (up to %ds), searching default document and iframes...',
        timeout_sec,
    )
    while time.monotonic() < deadline:
        try:
            driver.switch_to.default_content()
            if bookwalker_tw_session_gate_present(driver):
                _dump_debug_artifacts(driver)
                raise BookwalkerSessionError(
                    'Bookwalker TW: session invalid or expired (「請登入會員」). '
                    'Log in at bookwalker.com.tw in a normal browser, copy all cookies '
                    'for that site (not only reLogin), update main.py, and retry.'
                )
            if _find_nfbr_in_frames(driver, script, 0, max_iframe_depth):
                logging.info('Bookwalker NFBR reader is ready.')
                return

            # Reader chrome may appear before NFBR attaches; stay in that frame and poll.
            driver.switch_to.default_content()
            if _switch_to_frame_with_element(
                driver, By.ID, _PAGE_SLIDER_ID, 0, max_iframe_depth
            ):
                logging.info(
                    'Reader UI (#%s) found; NFBR not yet ready — polling in this frame...',
                    _PAGE_SLIDER_ID,
                )
                inner_end = time.monotonic() + min(45.0, deadline - time.monotonic())
                while time.monotonic() < inner_end:
                    if _nfbr_ready(driver, script):
                        logging.info('Bookwalker NFBR reader is ready (after page slider).')
                        return
                    time.sleep(1.0)
        except BookwalkerSessionError:
            raise
        except Exception:
            logging.exception('Error while searching for NFBR (will retry)')
            try:
                driver.switch_to.default_content()
            except Exception:
                pass
        elapsed = timeout_sec - (deadline - time.monotonic())
        if elapsed - last_log >= log_interval_sec:
            logging.info(
                'Waiting for Bookwalker NFBR reader... (~%ds / %ds)',
                int(elapsed),
                timeout_sec,
            )
            last_log = elapsed
        time.sleep(poll_sec)

    _dump_debug_artifacts(driver)
    raise TimeoutException(
        'Bookwalker: NFBR did not become ready within %ss (searched nested iframes to depth %s). '
        'See debug_bookwalker_nfbr_timeout.html / .png in the project directory. '
        'Headless automation may be blocked; try local non-headless or confirm the URL in a normal browser.'
        % (timeout_sec, max_iframe_depth)
    )
