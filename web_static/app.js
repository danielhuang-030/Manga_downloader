function setMsg(el, text, isError) {
  el.textContent = text;
  el.classList.toggle("error", Boolean(isError));
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

function detailFromErrorBody(body) {
  const d = body && body.detail;
  if (typeof d === "string") return d;
  if (Array.isArray(d)) {
    return d
      .map((item) => {
        if (item && typeof item === "object" && item.msg != null) return String(item.msg);
        return JSON.stringify(item);
      })
      .join("；");
  }
  if (d && typeof d === "object") {
    if (d.message != null) return String(d.message);
    return JSON.stringify(d);
  }
  return "請求失敗";
}

async function loadEnv() {
  const res = await fetch("/api/env");
  if (!res.ok) throw new Error("GET /api/env failed: " + res.status);
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
    setMsg(msg, "已儲存。", false);
    await loadEnv();
  } catch (err) {
    setMsg(msg, String(err.message || err), true);
  }
});

document.getElementById("btn-start").addEventListener("click", async () => {
  const msg = document.getElementById("start-msg");
  const log = document.getElementById("log");
  log.textContent = "";
  try {
    const res = await fetch("/api/download/start", { method: "POST" });
    if (res.status === 409) {
      const j = await res.json().catch(() => ({}));
      const d = j.detail;
      const jid = typeof d === "object" && d && d.job_id ? d.job_id : "";
      setMsg(msg, "已有下載進行中。" + (jid ? " job_id: " + jid : ""), true);
      return;
    }
    if (!res.ok) throw new Error("start failed: " + res.status);
    const { job_id: jobId } = await res.json();
    setMsg(msg, "已啟動 job: " + jobId, false);

    const es = new EventSource("/api/download/stream/" + encodeURIComponent(jobId));
    es.onmessage = (ev) => {
      let line;
      try {
        line = JSON.parse(ev.data);
      } catch {
        line = ev.data;
      }
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
      setMsg(envMsg, detailFromErrorBody(data) || "請求失敗 (" + res.status + ")", true);
      return;
    }

    const result = data.result;
    const messageZh = data.message_zh != null ? String(data.message_zh) : "";

    if (result === "appended") {
      if (idsField && data.manga_ids != null) {
        idsField.value = String(data.manga_ids);
      }
      setMsg(envMsg, messageZh || "已將解析出的 ID 附加至清單", false);
      if (urlEl) urlEl.value = "";
      return;
    }

    if (result === "duplicate") {
      setMsg(envMsg, messageZh || "清單已包含此 ID，未變更", false);
      return;
    }

    setMsg(envMsg, messageZh || JSON.stringify(data), false);
  } catch (err) {
    setMsg(envMsg, String(err.message || err), true);
  }
});

initTheme();

loadEnv().catch((err) => {
  setMsg(document.getElementById("env-msg"), String(err.message || err), true);
});
