/**
 * Web UI strings — 正體中文 / English
 * Exposes window.MangaI18n: { getLang, setLang, t, applyDom }
 */
(function (global) {
  const STORAGE_KEY = "manga_web_lang";

  const STRINGS = {
    "zh-Hant": {
      "app.title": "Manga_downloader",
      "skip.main": "跳至主要內容",
      "site.tagline": "本機漫畫下載控制台",
      "nav.lang": "介面語言",
      "nav.lang.aria": "介面語言",
      "nav.theme": "主題",
      "nav.theme.aria": "介面主題",
      "theme.light": "淺色",
      "theme.dark": "深色",
      "theme.system": "跟隨系統",
      "hint.env":
        "本機設定（.env）。Cookie 欄位載入後為遮罩；若不變更請勿覆寫為其他字串。",
      "section.env": "環境變數",
      "section.download": "下載",
      "section.progress": "進度",
      "section.log": "Log",
      "env.cookies": "Cookie（MANGA_COOKIES）",
      "env.res": "視窗解析度 WxH（MANGA_RES）",
      "env.sleep": "翻頁間隔秒數（MANGA_SLEEP_TIME）",
      "env.ids": "漫畫 ID 清單（MANGA_IDS）",
      "env.viewer_tpl": "Viewer 網址模板（MANGA_VIEWER_URL_TEMPLATE）",
      "env.headless": "Headless 模式（MANGA_HEADLESS）",
      "env.save": "儲存",
      "ph.masked": "***masked***",
      "ph.optional": "選填",
      "ph.optional_tpl": "選填，須含 {id}",
      "ph.optional_headless": "選填：new / old / 0",
      "ph.viewer_url": "貼上完整 viewer 網址",
      "paste.group.aria": "從 viewer 網址解析並附加至漫畫 ID 清單",
      "paste.title": "從網址輔助填入",
      "paste.hint": "選用，不影響儲存鈕",
      "paste.append": "從網址加入 ID",
      "download.start": "開始下載",
      "download.stop": "停止",
      "download.stopping": "停止中…",
      "progress.cancelled": "已停止下載",
      "error.stop_failed": "停止下載失敗（{status}）",
      "progress.subtitle": "多篇時依各書頁數加權估算整體完成度",
      "progress.aria.bar": "下載整體進度百分比",
      "progress.wait": "等待開始…",
      "log.aria": "下載事件與日誌（SSE JSON）",
      "error.request_failed": "請求失敗",
      "error.generic": "發生錯誤",
      "error.get_env": "讀取設定失敗：GET /api/env（{status}）",
      "error.start_failed": "啟動下載失敗（{status}）",
      "msg.saved": "已儲存。",
      "msg.job_started": "已啟動 job：{id}",
      "msg.download_busy": "已有下載進行中。",
      "msg.job_id": "job_id：{id}",
      "manga_id.appended": "已將解析出的 ID 附加至清單",
      "manga_id.duplicate": "清單已包含此 ID，未變更",
      "progress.run_started": "準備中…（共 {n} 本）",
      "progress.book": "第 {i} / {total} 本{suffix}",
      "progress.page": "第 {page} / {tp} 頁（整體約 {pct}%）",
      "progress.title_sep": " · ",
      "progress.done": "全部完成。",
      "progress.ended": "已結束。",
      "progress.error_prefix": "錯誤：",
    },
    en: {
      "app.title": "Manga_downloader",
      "skip.main": "Skip to main content",
      "site.tagline": "Local manga download console",
      "nav.lang": "Language",
      "nav.lang.aria": "Interface language",
      "nav.theme": "Theme",
      "nav.theme.aria": "Interface theme",
      "theme.light": "Light",
      "theme.dark": "Dark",
      "theme.system": "Match system",
      "hint.env":
        "Local settings (`.env`). Cookie fields load masked; do not overwrite with unrelated text unless you intend to change them.",
      "section.env": "Environment",
      "section.download": "Download",
      "section.progress": "Progress",
      "section.log": "Log",
      "env.cookies": "Cookie (MANGA_COOKIES)",
      "env.res": "Window size W×H (MANGA_RES)",
      "env.sleep": "Page delay seconds (MANGA_SLEEP_TIME)",
      "env.ids": "Manga ID list (MANGA_IDS)",
      "env.viewer_tpl": "Viewer URL template (MANGA_VIEWER_URL_TEMPLATE)",
      "env.headless": "Headless mode (MANGA_HEADLESS)",
      "env.save": "Save",
      "ph.masked": "***masked***",
      "ph.optional": "Optional",
      "ph.optional_tpl": "Optional; must include {id}",
      "ph.optional_headless": "Optional: new / old / 0",
      "ph.viewer_url": "Paste full viewer URL",
      "paste.group.aria": "Parse viewer URL and append to manga ID list",
      "paste.title": "Paste URL helper",
      "paste.hint": "Optional; does not affect Save",
      "paste.append": "Append ID from URL",
      "download.start": "Start download",
      "download.stop": "Stop",
      "download.stopping": "Stopping…",
      "progress.cancelled": "Download stopped.",
      "error.stop_failed": "Failed to stop download ({status})",
      "progress.subtitle": "Multi-volume estimate weighted by page counts",
      "progress.aria.bar": "Overall download progress percent",
      "progress.wait": "Waiting to start…",
      "log.aria": "Download events and log (SSE JSON)",
      "error.request_failed": "Request failed",
      "error.generic": "Something went wrong",
      "error.get_env": "Failed to load settings: GET /api/env ({status})",
      "error.start_failed": "Failed to start download ({status})",
      "msg.saved": "Saved.",
      "msg.job_started": "Started job: {id}",
      "msg.download_busy": "A download is already running.",
      "msg.job_id": "job_id: {id}",
      "manga_id.appended": "Parsed ID appended to the list",
      "manga_id.duplicate": "List already contains this ID; unchanged",
      "progress.run_started": "Preparing… ({n} books)",
      "progress.run_started_one": "Preparing… (1 book)",
      "progress.run_started_many": "Preparing… ({n} books)",
      "progress.book": "Book {i} / {total}{suffix}",
      "progress.page": "Page {page} / {tp} (overall ~{pct}%)",
      "progress.title_sep": " — ",
      "progress.done": "All done.",
      "progress.ended": "Finished.",
      "progress.error_prefix": "Error: ",
    },
  };

  let lang = "zh-Hant";

  function normalizeLang(v) {
    return v === "en" ? "en" : "zh-Hant";
  }

  function getLang() {
    return lang;
  }

  function setLang(v) {
    lang = normalizeLang(v);
    try {
      localStorage.setItem(STORAGE_KEY, lang);
    } catch {
      /* ignore */
    }
    document.documentElement.setAttribute("lang", lang === "zh-Hant" ? "zh-Hant" : "en");
  }

  function pickTable() {
    return STRINGS[lang] || STRINGS.en;
  }

  function t(key, vars) {
    const table = pickTable();
    let s = table[key];
    if (s == null) s = STRINGS.en[key];
    if (s == null) return key;
    if (vars && typeof vars === "object") {
      Object.keys(vars).forEach(function (k) {
        s = s.split("{" + k + "}").join(String(vars[k]));
      });
    }
    return s;
  }

  function applyDom() {
    document.querySelectorAll("[data-i18n]").forEach(function (el) {
      const k = el.getAttribute("data-i18n");
      if (k) el.textContent = t(k);
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach(function (el) {
      const k = el.getAttribute("data-i18n-placeholder");
      if (k) el.setAttribute("placeholder", t(k));
    });
    document.querySelectorAll("[data-i18n-aria-label]").forEach(function (el) {
      const k = el.getAttribute("data-i18n-aria-label");
      if (k) el.setAttribute("aria-label", t(k));
    });
    document.querySelectorAll("option[data-i18n-opt]").forEach(function (opt) {
      const k = opt.getAttribute("data-i18n-opt");
      if (k) opt.textContent = t(k);
    });
    document.title = t("app.title");
  }

  function tRunStarted(n) {
    const num = Math.max(1, parseInt(n, 10) || 1);
    if (lang === "en") {
      return num === 1 ? t("progress.run_started_one") : t("progress.run_started_many", { n: num });
    }
    return t("progress.run_started", { n: num });
  }

  global.MangaI18n = {
    getLang,
    setLang,
    t,
    tRunStarted,
    applyDom,
    normalizeLang,
    STRINGS,
  };
})(typeof window !== "undefined" ? window : globalThis);
