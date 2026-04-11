function t(key, vars) {
  return window.MangaI18n.t(key, vars);
}

function tRunStarted(n) {
  return window.MangaI18n.tRunStarted(n);
}

/** @param {boolean|string} kind true/"error" | "success" | false/"neutral" */
function setMsg(el, text, kind) {
  const isError = kind === true || kind === "error";
  const isSuccess = kind === "success";
  el.textContent = text;
  el.classList.toggle("error", isError);
  el.classList.toggle("success", isSuccess);
}

let downloadTotalBooks = 1;
let downloadBookIndex = 0;
let lastProgressPercent = 0;

function resetDownloadProgress() {
  downloadTotalBooks = 1;
  downloadBookIndex = 0;
  lastProgressPercent = 0;
  setDownloadProgress(0, t("progress.wait"), { error: false });
}

function setDownloadProgress(percent, detail, opts) {
  const o = opts || {};
  if (percent != null && !Number.isNaN(Number(percent))) {
    lastProgressPercent = Math.max(0, Math.min(100, Math.round(Number(percent))));
  }
  const p = lastProgressPercent;
  const fill = document.getElementById("progress-fill");
  const root = document.getElementById("download-progress");
  const pctEl = document.getElementById("progress-pct");
  const lab = document.getElementById("progress-label");
  if (fill) fill.style.width = p + "%";
  if (pctEl) pctEl.textContent = p + "%";
  if (lab && detail != null) lab.textContent = detail;
  if (root) {
    root.setAttribute("aria-valuenow", String(p));
    root.setAttribute("aria-valuetext", p + "% — " + (detail != null ? detail : ""));
    const err = Boolean(o.error);
    root.classList.toggle("progress-meter--error", err);
    root.classList.toggle("progress-meter--active", !err && p > 2 && p < 100);
  }
}

function overallDownloadPercent(bookIndex, page, totalPages) {
  const tb = Math.max(1, downloadTotalBooks);
  const tp = Math.max(1, Number(totalPages) || 1);
  const pg = Math.min(Math.max(Number(page) || 0, 0), tp);
  const bi = Math.max(0, Number(bookIndex) || 0);
  return Math.min(100, ((bi + pg / tp) / tb) * 100);
}

function applyDownloadProgressEvent(data) {
  if (!data || typeof data !== "object") return;
  const typ = data.type;
  if (typ === "run_started") {
    downloadTotalBooks = Math.max(1, parseInt(data.total_books, 10) || 1);
    downloadBookIndex = 0;
    setDownloadProgress(0, tRunStarted(downloadTotalBooks), { error: false });
    return;
  }
  if (typ === "book_started") {
    downloadBookIndex = Number(data.index);
    if (Number.isNaN(downloadBookIndex)) downloadBookIndex = 0;
    const tit = data.title ? String(data.title).slice(0, 42) : data.viewer_id ? String(data.viewer_id) : "";
    const atStart = (downloadBookIndex / Math.max(1, downloadTotalBooks)) * 100;
    const suffix = tit ? t("progress.title_sep") + tit : "";
    setDownloadProgress(
      atStart,
      t("progress.book", {
        i: downloadBookIndex + 1,
        total: downloadTotalBooks,
        suffix,
      }),
      { error: false },
    );
    return;
  }
  if (typ === "page_progress") {
    const pct = overallDownloadPercent(downloadBookIndex, data.page, data.total_pages);
    const tp = Math.max(1, Number(data.total_pages) || 1);
    const pg = Number(data.page) || 0;
    setDownloadProgress(
      pct,
      t("progress.page", { page: pg, tp, pct: Math.round(pct) }),
      { error: false },
    );
    return;
  }
  if (typ === "run_finished") {
    if (data.ok) {
      setDownloadProgress(100, t("progress.done"), { error: false });
    } else {
      setDownloadProgress(0, t("progress.ended"), { error: false });
    }
    return;
  }
  if (typ === "run_error") {
    const m = data.message ? String(data.message).slice(0, 140) : t("error.generic");
    setDownloadProgress(undefined, t("progress.error_prefix") + m, { error: true });
    return;
  }
}

const THEME_KEY = "manga_web_theme";
const THEME_VALUES = new Set(["light", "dark", "system"]);

function applyTheme(value) {
  const v = THEME_VALUES.has(value) ? value : "system";
  document.documentElement.dataset.theme = v;
  const sel = document.getElementById("theme-select");
  if (sel) sel.value = v;
}

function initTheme() {
  let stored = localStorage.getItem(THEME_KEY);
  if (!THEME_VALUES.has(stored)) {
    stored = "system";
  }
  applyTheme(stored);

  const sel = document.getElementById("theme-select");
  if (!sel) return;

  sel.addEventListener("change", () => {
    const v = sel.value;
    localStorage.setItem(THEME_KEY, v);
    applyTheme(v);
  });
}

function initI18n() {
  const stored = localStorage.getItem("manga_web_lang");
  let initial = "zh-Hant";
  if (stored === "en" || stored === "zh-Hant") {
    initial = stored;
  } else {
    const nav = (navigator.language || "").toLowerCase();
    if (nav.startsWith("zh")) initial = "zh-Hant";
    else initial = "en";
  }
  window.MangaI18n.setLang(initial);
  const sel = document.getElementById("lang-select");
  if (sel) {
    sel.value = initial;
    sel.addEventListener("change", () => {
      window.MangaI18n.setLang(sel.value);
      window.MangaI18n.applyDom();
      resetDownloadProgress();
    });
  }
  window.MangaI18n.applyDom();
}

function detailFromErrorBody(body) {
  const d = body && body.detail;
  if (typeof d === "string") return d;
  if (Array.isArray(d)) {
    return d
      .map((item) => {
        if (item && typeof item === "object" && item.msg != null) return String(item.msg);
        return JSON.stringify(item);
      })
      .join(window.MangaI18n.getLang() === "en" ? "; " : "；");
  }
  if (d && typeof d === "object") {
    if (d.message != null) return String(d.message);
    return JSON.stringify(d);
  }
  return t("error.request_failed");
}

async function loadEnv() {
  const res = await fetch("/api/env");
  if (!res.ok) throw new Error(t("error.get_env", { status: res.status }));
  const data = await res.json();
  const form = document.getElementById("env-form");
  for (const [k, v] of Object.entries(data)) {
    const field = form.elements.namedItem(k);
    if (!field) continue;
    field.value = v == null ? "" : String(v);
  }
}

document.getElementById("env-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.target;
  const body = {};
  const fd = new FormData(form);
  for (const [k, v] of fd.entries()) {
    if (String(v).trim() !== "") body[k] = String(v);
  }
  const msg = document.getElementById("env-msg");
  try {
    const res = await fetch("/api/env", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      const detail = await res.json().catch(() => ({}));
      throw new Error(detailFromErrorBody(detail) || res.statusText);
    }
    setMsg(msg, t("msg.saved"), "success");
    await loadEnv();
  } catch (err) {
    setMsg(msg, String(err.message || err), true);
  }
});

document.getElementById("btn-start").addEventListener("click", async () => {
  const msg = document.getElementById("start-msg");
  const log = document.getElementById("log");
  log.textContent = "";
  resetDownloadProgress();
  try {
    const res = await fetch("/api/download/start", { method: "POST" });
    if (res.status === 409) {
      const j = await res.json().catch(() => ({}));
      const d = j.detail;
      const jid = typeof d === "object" && d && d.job_id ? d.job_id : "";
      const busy = t("msg.download_busy");
      const jidPart = jid ? " " + t("msg.job_id", { id: jid }) : "";
      setMsg(msg, busy + jidPart, true);
      return;
    }
    if (!res.ok) throw new Error(t("error.start_failed", { status: res.status }));
    const { job_id: jobId } = await res.json();
    setMsg(msg, t("msg.job_started", { id: jobId }), "success");

    const es = new EventSource("/api/download/stream/" + encodeURIComponent(jobId));
    es.onmessage = (ev) => {
      let line;
      try {
        line = JSON.parse(ev.data);
      } catch {
        line = ev.data;
      }
      applyDownloadProgressEvent(line);
      log.textContent += JSON.stringify(line, null, 2) + "\n";
      log.scrollTop = log.scrollHeight;
    };
    es.onerror = () => {
      es.close();
    };
  } catch (err) {
    setMsg(msg, String(err.message || err), true);
  }
});

document.getElementById("btn-append-id").addEventListener("click", async () => {
  const envMsg = document.getElementById("env-msg");
  const form = document.getElementById("env-form");
  const urlEl = document.getElementById("viewer-url-paste");
  const url = urlEl ? String(urlEl.value || "").trim() : "";
  const idsField = form.elements.namedItem("MANGA_IDS");
  const tplField = form.elements.namedItem("MANGA_VIEWER_URL_TEMPLATE");
  const mangaIds = idsField ? String(idsField.value || "") : "";
  const templateRaw = tplField ? String(tplField.value || "") : "";

  const payload = {
    url,
    MANGA_IDS: mangaIds,
    MANGA_VIEWER_URL_TEMPLATE: templateRaw.trim() === "" ? "" : templateRaw,
  };

  try {
    const res = await fetch("/api/env/manga-id-from-url", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json().catch(() => ({}));

    if (res.status === 400) {
      setMsg(envMsg, detailFromErrorBody(data), true);
      return;
    }

    if (!res.ok) {
      setMsg(
        envMsg,
        detailFromErrorBody(data) || t("error.request_failed") + " (" + res.status + ")",
        true,
      );
      return;
    }

    const result = data.result;
    const messageZh = data.message_zh != null ? String(data.message_zh) : "";

    if (result === "appended") {
      if (idsField && data.manga_ids != null) {
        idsField.value = String(data.manga_ids);
      }
      setMsg(envMsg, messageZh || t("manga_id.appended"), "success");
      if (urlEl) urlEl.value = "";
      return;
    }

    if (result === "duplicate") {
      setMsg(envMsg, messageZh || t("manga_id.duplicate"), false);
      return;
    }

    setMsg(envMsg, messageZh || JSON.stringify(data), false);
  } catch (err) {
    setMsg(envMsg, String(err.message || err), true);
  }
});

initI18n();
initTheme();
resetDownloadProgress();

loadEnv().catch((err) => {
  setMsg(document.getElementById("env-msg"), String(err.message || err), true);
});
