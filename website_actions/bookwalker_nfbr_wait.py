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

# Bundles vary: classic menu.options.a6l.moveToPage, renamed methods, or deep graph — multi-strategy.
_NFBR_DEEP_FIND_HOLDER_JS = """
function __nfbrOwnKeys(o) {
  try {
    if (typeof Reflect !== 'undefined' && Reflect.ownKeys) return Reflect.ownKeys(o);
  } catch (e0) {}
  try {
    return Object.getOwnPropertyNames(o);
  } catch (e1) {
    try {
      return Object.keys(o);
    } catch (e2) {
      return [];
    }
  }
}
function __nfbrShouldSkipRecurse(o) {
  if (o == null) return true;
  var t = typeof o;
  if (t !== 'object' && t !== 'function') return true;
  try {
    if (o === window || o === document) return true;
    if (typeof o.nodeType === 'number') return true;
  } catch (e) {}
  return false;
}
function __nfbrWrapA6lMethod(a6l, fn) {
  return {
    moveToPage: function (p) {
      return fn.call(a6l, p);
    }
  };
}
function __nfbrScanA6lForPageMethod(a6l) {
  if (!a6l || typeof a6l !== 'object') return null;
  var names = __nfbrOwnKeys(a6l);
  var i;
  for (i = 0; i < names.length; i++) {
    try {
      var fn = a6l[names[i]];
      if (typeof fn !== 'function') continue;
      if (names[i] === 'moveToPage') return __nfbrWrapA6lMethod(a6l, fn);
    } catch (e0) {}
  }
  for (i = 0; i < names.length; i++) {
    try {
      var f2 = a6l[names[i]];
      if (typeof f2 !== 'function' || f2.length > 4) continue;
      var src = Function.prototype.toString.call(f2);
      if (src.indexOf('moveToPage') !== -1 || src.indexOf('pageSliderCounter') !== -1) {
        return __nfbrWrapA6lMethod(a6l, f2);
      }
    } catch (e1) {}
  }
  return null;
}
function __nfbrClassicMenuChains(init) {
  if (!init || typeof init !== 'object') return null;
  var keys = Object.keys(init);
  var i;
  for (i = 0; i < keys.length; i++) {
    try {
      var node = init[keys[i]];
      if (!node) continue;
      var m = node.menu;
      if (!m && node.views_) m = node.views_.menu;
      if (!m || !m.options || !m.options.a6l) continue;
      var a6 = m.options.a6l;
      if (typeof a6.moveToPage === 'function') return a6;
      var w = __nfbrScanA6lForPageMethod(a6);
      if (w) return w;
    } catch (e) {}
  }
  return null;
}
function __nfbrDeepFindAnyOptionsA6l(init) {
  var visited = new WeakSet();
  function walk(o, depth, maxDepth) {
    if (o == null || depth > maxDepth) return null;
    if (__nfbrShouldSkipRecurse(o)) return null;
    try {
      if (visited.has(o)) return null;
      visited.add(o);
    } catch (e0) {
      return null;
    }
    try {
      if (o.options && o.options.a6l) {
        var a6 = o.options.a6l;
        if (typeof a6.moveToPage === 'function') return a6;
        var w = __nfbrScanA6lForPageMethod(a6);
        if (w) return w;
      }
    } catch (e1) {}
    var ks = __nfbrOwnKeys(o);
    var j;
    for (j = 0; j < Math.min(ks.length, 320); j++) {
      try {
        var ch = o[ks[j]];
        if (typeof ch === 'object' || typeof ch === 'function') {
          var f = walk(ch, depth + 1, maxDepth);
          if (f) return f;
        }
      } catch (e2) {}
    }
    return null;
  }
  return walk(init, 0, 36);
}
function __nfbrDeepFindMoveHolder(init) {
  function tryHolder(o) {
    try {
      if (o && typeof o.moveToPage === 'function') return o;
    } catch (e0) {}
    try {
      if (o && o.a6l && typeof o.a6l.moveToPage === 'function') return o.a6l;
    } catch (e1) {}
    return null;
  }
  function deepFind(o, depth, maxDepth, visited) {
    if (o == null || depth > maxDepth) return null;
    if (__nfbrShouldSkipRecurse(o)) return null;
    try {
      if (visited.has(o)) return null;
      visited.add(o);
    } catch (e2) {
      return null;
    }
    var h = tryHolder(o);
    if (h) return h;
    var ks = __nfbrOwnKeys(o);
    var maxK = Math.min(ks.length, 320);
    var i;
    for (i = 0; i < maxK; i++) {
      try {
        var child = o[ks[i]];
        var found = deepFind(child, depth + 1, maxDepth, visited);
        if (found) return found;
      } catch (e5) {}
    }
    return null;
  }
  var visited = new WeakSet();
  var h = deepFind(init, 0, 36, visited);
  if (h) return h;
  try {
    var ag = NFBR && NFBR.a6G;
    if (ag && ag !== init) {
      visited = new WeakSet();
      h = deepFind(ag, 0, 36, visited);
      if (h) return h;
    }
  } catch (e6) {}
  try {
    var root = NFBR;
    if (root && root !== init) {
      visited = new WeakSet();
      h = deepFind(root, 0, 28, visited);
      if (h) return h;
    }
  } catch (e7) {}
  return null;
}
function __nfbrResolveMoveHolder() {
  var init = NFBR && NFBR.a6G && NFBR.a6G.Initializer;
  if (!init) return null;
  var h = __nfbrClassicMenuChains(init);
  if (h) return h;
  h = __nfbrDeepFindAnyOptionsA6l(init);
  if (h) return h;
  h = __nfbrDeepFindMoveHolder(init);
  return h;
}
"""

_NFBR_PROBE_MOVE_SCRIPT = (
    _NFBR_DEEP_FIND_HOLDER_JS
    + """
return (function () {
  try {
    var init = NFBR && NFBR.a6G && NFBR.a6G.Initializer;
    if (!init) return { ok: false, err: 'NFBR.a6G.Initializer missing' };
    var h = __nfbrResolveMoveHolder();
    if (h) return { ok: true, keys: Object.keys(init) };
    return { ok: false, err: 'no NFBR page mover resolved', keys: Object.keys(init) };
  } catch (e) {
    return { ok: false, err: String(e) };
  }
})();
"""
)

_NFBR_MOVE_TO_PAGE_SCRIPT = (
    _NFBR_DEEP_FIND_HOLDER_JS
    + """
var page = arguments[0];
var init = NFBR && NFBR.a6G && NFBR.a6G.Initializer;
if (!init) throw new Error('NFBR.a6G.Initializer missing');
var holder = __nfbrResolveMoveHolder();
if (!holder || typeof holder.moveToPage !== 'function') {
  throw new Error('NFBR moveToPage holder not found');
}
holder.moveToPage(page);
return true;
"""
)


def ensure_nfbr_move_to_page_ready(driver):
    """
    Confirm we can find an object with moveToPage under NFBR.a6G.Initializer (minified keys OK).
    """
    raw = driver.execute_script(_NFBR_PROBE_MOVE_SCRIPT)
    if not raw or not raw.get('ok'):
        err = (raw or {}).get('err', 'unknown')
        keys = (raw or {}).get('keys')
        detail = ' keys=%s' % (keys,) if keys is not None else ''
        raise RuntimeError(
            'Bookwalker: could not resolve NFBR moveToPage (%s).%s' % (err, detail)
        )


def nfbr_move_to_page(driver, page):
    """Invoke moveToPage using the same deep discovery as ensure_nfbr_move_to_page_ready."""
    driver.execute_script(_NFBR_MOVE_TO_PAGE_SCRIPT, page)


def resolve_nfbr_menu_accessor(driver):
    """
    Back-compat: older Bookwalker bundles used a fixed Initializer.<name>.menu chain.

    Now we only verify deep search works; return placeholders (call sites use nfbr_move_to_page).
    """
    ensure_nfbr_move_to_page_ready(driver)
    return '', 'deep'


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
