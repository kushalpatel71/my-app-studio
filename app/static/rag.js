"use strict";
const form = document.getElementById("rag-form");
form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = document.getElementById("ask-button");
  const status = document.getElementById("rag-status");
  const result = document.getElementById("rag-result");
  const panel = document.getElementById("trace-panel");
  const trace = document.getElementById("rag-trace");
  const citations = document.getElementById("rag-citations");
  button.disabled = true;
  status.textContent = "Searching approved documents and generating an answer…";
  result.hidden = true;
  panel.hidden = true;
  trace.replaceChildren();
  citations.replaceChildren();
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 30000);
  try {
    const response = await fetch("/api/rag/ask", {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({question: document.getElementById("question").value}),
      signal: controller.signal
    });
    const data = await response.json();
    for (const passage of data.trace || []) {
      const item = document.createElement("li");
      const link = document.createElement("a");
      link.href = passage.url;
      link.textContent = `${passage.id} · ${passage.metric} ${passage.score}`;
      item.append(link);
      trace.append(item);
    }
    panel.hidden = !(data.trace || []).length;
    if (!response.ok) {
      status.textContent = typeof data.detail === "string" ? data.detail : "Question rejected. Check its length and try again.";
      if (typeof data.error_code === "string") status.textContent += ` Reference: ${data.error_code}.`;
      return;
    }
    document.getElementById("rag-answer").textContent = data.answer;
    for (const source of data.citations) {
      const item = document.createElement("li");
      const link = document.createElement("a");
      link.href = source.url;
      link.textContent = `${source.title} · ${source.id}`;
      item.append(link);
      citations.append(item);
    }
    if (!data.citations.length) {
      const item = document.createElement("li");
      item.textContent = "No supporting citation: insufficient evidence.";
      citations.append(item);
    }
    result.hidden = false;
    status.textContent = data.insufficient ? "Insufficient evidence." : "Answer ready. Inspect the supporting passages.";
  } catch (error) {
    status.textContent = error.name === "AbortError" ? "Request timed out. Please try again later." : "Connection failed. Please try again later.";
  } finally {
    clearTimeout(timeout);
    button.disabled = false;
  }
});

const importButton = document.getElementById("import-corpus");
if (importButton) importButton.addEventListener("click", async () => {
  const status = document.getElementById("import-status");
  importButton.disabled = true;
  status.textContent = "Validating and indexing approved documents…";
  try {
    const csrfResponse = await fetch("/api/csrf");
    const csrf = await csrfResponse.json();
    const response = await fetch("/api/rag/import", {
      method: "POST", headers: {"X-CSRF-Token": csrf.csrf_token}
    });
    const data = await response.json();
    status.textContent = response.ok ? `${data.status}: ${data.documents} documents, ${data.chunks} chunks. Reload to update the counter.` : data.detail;
  } catch (_) {
    status.textContent = "Import connection failed. Check server status before retrying.";
  } finally {
    importButton.disabled = false;
  }
});
