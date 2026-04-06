function setMsg(el, text, isError) {
  el.textContent = text;
  el.classList.toggle("error", Boolean(isError));
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
      throw new Error(detail.detail || res.statusText);
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

loadEnv().catch((err) => {
  setMsg(document.getElementById("env-msg"), String(err.message || err), true);
});
