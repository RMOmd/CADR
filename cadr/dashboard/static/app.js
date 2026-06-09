const state = {
  dashboard: null,
  selectedPair: null,
};

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function toneClass(status) {
  if (status === "ok") return "tone-ok";
  if (status === "error") return "tone-error";
  return "tone-partial";
}

function formatNumber(value, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "—";
  }
  return Number(value).toFixed(digits);
}

function formatSigned(value, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "—";
  }
  const number = Number(value);
  return `${number > 0 ? "+" : ""}${number.toFixed(digits)}`;
}

function titleize(value) {
  if (!value) {
    return "—";
  }
  return String(value)
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function setActionLog(message, status = "partial") {
  const el = document.getElementById("action-log");
  el.className = `callout ${toneClass(status)}`;
  el.textContent = message;
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `${response.status} ${response.statusText}`);
  }
  return response.json();
}

function buildMetricBar(value, maxValue = 1) {
  const safeValue = value === null || value === undefined ? 0 : Math.abs(Number(value));
  const width = Math.min(100, Math.round((safeValue / maxValue) * 100));
  return `
    <div class="metric-bar">
      <div class="metric-bar-fill" style="width: ${width}%"></div>
    </div>
  `;
}

function buildSparkline(points, color) {
  const values = points.filter((value) => value !== null && value !== undefined && Number.isFinite(Number(value))).map(Number);
  if (values.length === 0) {
    return `<div class="muted">Not enough history yet.</div>`;
  }

  if (values.length === 1) {
    return `
      <div class="muted">Need at least 2 saved observations to draw a trend.</div>
    `;
  }

  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  const stepX = 180 / (values.length - 1);
  const coordinates = values.map((value, index) => {
    const x = index * stepX;
    const y = 74 - ((value - min) / range) * 60;
    return [x, y];
  });
  const polyline = coordinates.map(([x, y]) => `${x},${y}`).join(" ");
  const fillPath = `M0 80 L${polyline} L180 80 Z`;

  return `
    <svg class="sparkline" viewBox="0 0 180 88" preserveAspectRatio="none" aria-hidden="true">
      <path class="sparkline-grid" d="M0 22 H180 M0 44 H180 M0 66 H180"></path>
      <path class="sparkline-fill" d="${fillPath}" fill="${color}"></path>
      <polyline class="sparkline-line" points="${polyline}" stroke="${color}"></polyline>
    </svg>
  `;
}

function renderStats(stats) {
  const grid = document.getElementById("stats-grid");
  const cards = [
    ["Monitored Pairs", stats.monitored_pairs ?? 0, "Pairs configured for the default scan set."],
    ["Latest Signals", stats.latest_pairs_available ?? 0, "Pairs that currently have a stored signal snapshot."],
    ["Healthy Signals", stats.ok_pairs ?? 0, "Signals generated without execution or data errors."],
    ["Signal Failures", stats.error_pairs ?? 0, "Pairs that need a retry, data fix, or better fallbacks."],
  ];

  grid.innerHTML = cards
    .map(
      ([label, value, note]) => `
        <article class="stat-card">
          <p class="stat-label">${escapeHtml(label)}</p>
          <div class="stat-value">${escapeHtml(value)}</div>
          <div class="stat-note">${escapeHtml(note)}</div>
        </article>
      `
    )
    .join("");
}

function renderRunSummary(containerId, run, emptyText) {
  const container = document.getElementById(containerId);
  if (!run) {
    container.innerHTML = `<div class="muted">${escapeHtml(emptyText)}</div>`;
    return;
  }

  const payload = run.payload ?? {};
  const extraLine =
    run.run_type === "default_scan"
      ? `${payload.ok_count ?? 0} ok / ${payload.error_count ?? 0} errors across ${payload.total_pairs ?? 0} pairs.`
      : payload.summary || payload.market_view || payload.pair || null;

  container.innerHTML = `
    <div class="summary-line">
      <span class="summary-label">Status</span>
      <strong class="${toneClass(run.status)}">${escapeHtml(run.status)}</strong>
    </div>
    <div class="summary-line">
      <span class="summary-label">Window</span>
      <span>${escapeHtml(run.started_at)} → ${escapeHtml(run.finished_at ?? "running")}</span>
    </div>
    <div class="summary-line">
      <span class="summary-label">Message</span>
      <span>${escapeHtml(run.message ?? run.error ?? "No message")}</span>
    </div>
    <div class="summary-line">
      <span class="summary-label">Signal</span>
      <span>${escapeHtml(extraLine ?? "No additional summary available.")}</span>
    </div>
  `;
}

function renderSignalBoard(pairs) {
  const board = document.getElementById("signal-board");
  const rankedPairs = [...pairs].sort((left, right) => Math.abs(right.spread_zscore ?? 0) - Math.abs(left.spread_zscore ?? 0));

  if (rankedPairs.length === 0) {
    board.innerHTML = `<div class="muted">Run a scan to populate the signal board.</div>`;
    return;
  }

  board.innerHTML = rankedPairs
    .map((pair) => {
      const isActive = state.selectedPair === pair.pair ? "active" : "";
      return `
        <article class="signal-card ${isActive}" data-pair="${escapeHtml(pair.pair)}">
          <div class="signal-card-top">
            <div>
              <strong>${escapeHtml(pair.pair)}</strong>
              <div class="signal-card-meta">${escapeHtml(titleize(pair.direction))}</div>
            </div>
            <span class="status-pill ${toneClass(pair.status)}">${escapeHtml(pair.status)}</span>
          </div>

          <div class="signal-card-meta">
            ${escapeHtml(titleize(pair.divergence_state))} in a ${escapeHtml(titleize(pair.market_regime))} regime
          </div>

          <div class="metric-rail">
            <div class="metric-row">
              <div class="metric-row-head">
                <span>Dislocation</span>
                <strong>${escapeHtml(formatSigned(pair.spread_zscore))}</strong>
              </div>
              ${buildMetricBar(pair.spread_zscore, 5)}
            </div>
            <div class="metric-row">
              <div class="metric-row-head">
                <span>Conviction</span>
                <strong>${escapeHtml(pair.conviction_score ?? "—")}</strong>
              </div>
              ${buildMetricBar(pair.conviction_score, 5)}
            </div>
            <div class="metric-row">
              <div class="metric-row-head">
                <span>Correlation</span>
                <strong>${escapeHtml(formatNumber(pair.correlation, 3))}</strong>
              </div>
              ${buildMetricBar(pair.correlation, 1)}
            </div>
          </div>
        </article>
      `;
    })
    .join("");

  board.querySelectorAll(".signal-card").forEach((card) => {
    card.addEventListener("click", () => selectPair(card.dataset.pair));
  });
}

function renderPairTable(pairs) {
  const tbody = document.getElementById("pair-table-body");
  tbody.innerHTML = pairs
    .map((pair) => {
      const active = state.selectedPair === pair.pair ? "active" : "";
      return `
        <tr class="clickable ${active}" data-pair="${escapeHtml(pair.pair)}">
          <td>${escapeHtml(pair.pair)}</td>
          <td class="${toneClass(pair.status)}">${escapeHtml(pair.status)}</td>
          <td>${escapeHtml(titleize(pair.direction))}</td>
          <td>${escapeHtml(formatSigned(pair.spread_zscore))}</td>
          <td>${escapeHtml(pair.conviction_score ?? "—")}</td>
          <td>${escapeHtml(titleize(pair.divergence_state))}</td>
          <td>${escapeHtml(formatNumber(pair.correlation, 3))}</td>
          <td>${escapeHtml(titleize(pair.market_regime))}</td>
        </tr>
      `;
    })
    .join("");

  tbody.querySelectorAll("tr").forEach((row) => {
    row.addEventListener("click", () => {
      selectPair(row.dataset.pair);
    });
  });
}

function renderRuns(runs) {
  const list = document.getElementById("runs-list");
  if (runs.length === 0) {
    list.innerHTML = `<div class="muted">No runs have been recorded yet.</div>`;
    return;
  }

  list.innerHTML = runs
    .map(
      (run) => `
        <article class="run-card">
          <strong>${escapeHtml(run.run_type)}${run.pair ? ` · ${escapeHtml(run.pair)}` : ""}</strong>
          <div class="run-meta ${toneClass(run.status)}">${escapeHtml(run.status)}</div>
          <div class="run-meta">${escapeHtml(run.started_at)} → ${escapeHtml(run.finished_at ?? "running")}</div>
          <div>${escapeHtml(run.message ?? run.error ?? "No details")}</div>
        </article>
      `
    )
    .join("");
}

function metricChip(label, value) {
  return `
    <div class="detail-chip">
      <strong>${escapeHtml(label)}</strong>
      ${escapeHtml(value)}
    </div>
  `;
}

function renderPairDetail(detail) {
  const container = document.getElementById("pair-detail");
  const latest = detail.latest ?? {};
  const history = [...(detail.history ?? [])].reverse();
  const spec = latest.spec ?? {};
  const evidence = spec.analysis?.skill_hub_pair_context ?? {};
  const riskNotes = evidence.risk_notes ?? [];

  const zscoreSeries = history.map((entry) => entry.spread_zscore);
  const correlationSeries = history.map((entry) => entry.correlation);
  const historyRows = history
    .slice(-6)
    .reverse()
    .map(
      (entry) => `
        <div class="history-row">
          <div>
            <strong>${escapeHtml(formatSigned(entry.spread_zscore))}</strong>
            <div class="muted">${escapeHtml(titleize(entry.direction))}</div>
          </div>
          <time>${escapeHtml(entry.created_at)}</time>
        </div>
      `
    )
    .join("");

  container.innerHTML = `
    <div class="detail-layout">
      <section class="detail-section">
        <div class="detail-summary">
          <div>
            <h3>${escapeHtml(latest.pair ?? "Unknown pair")}</h3>
            <p>${escapeHtml(titleize(latest.direction))} with ${escapeHtml(titleize(latest.divergence_state))} context.</p>
          </div>
          <span class="status-pill ${toneClass(latest.status)}">${escapeHtml(latest.status ?? "unknown")}</span>
        </div>

        <div class="detail-grid">
          ${metricChip("Z-Score", formatSigned(latest.spread_zscore))}
          ${metricChip("Conviction", latest.conviction_score ?? "—")}
          ${metricChip("Correlation", formatNumber(latest.correlation, 3))}
          ${metricChip("Regime", titleize(latest.market_regime))}
          ${metricChip("Return Spread", `${formatSigned(latest.base_vs_peer_average_return_pct)}%`)}
          ${metricChip("Base vs Peer", `${escapeHtml(latest.base_asset ?? "—")} vs ${escapeHtml(latest.quote_asset ?? "—")}`)}
        </div>

        <div class="detail-section" style="margin-top: 16px;">
          <h3>Operator Notes</h3>
          <div class="insight-list">
            <div class="insight-item"><strong>Summary:</strong> ${escapeHtml(evidence.summary ?? "No summary available yet.")}</div>
            <div class="insight-item"><strong>Decision:</strong> ${escapeHtml(evidence.business_decision ?? "No decision text available.")}</div>
            <div class="insight-item"><strong>Risk Notes:</strong> ${escapeHtml(riskNotes.join(" | ") || "No explicit risk notes returned.")}</div>
          </div>
        </div>
      </section>

      <section class="detail-section chart-panel">
        <div class="chart-card">
          <div class="chart-head">
            <strong>Z-Score Trend</strong>
            <span>Last ${history.length} saved observations</span>
          </div>
          ${buildSparkline(zscoreSeries, "#cb6e36")}
        </div>

        <div class="chart-card">
          <div class="chart-head">
            <strong>Correlation Trend</strong>
            <span>Stability of the pair relationship</span>
          </div>
          ${buildSparkline(correlationSeries, "#125e50")}
        </div>

        <div class="chart-card">
          <div class="chart-head">
            <strong>Recent History</strong>
            <span>Most recent signal snapshots</span>
          </div>
          <div class="history-grid">
            ${historyRows || `<div class="muted">No history entries yet.</div>`}
          </div>
        </div>
      </section>
    </div>

    <section class="detail-section" style="margin-top: 18px;">
      <div class="panel-header compact">
        <div>
          <h3>Raw Strategy Payload</h3>
          <p class="panel-caption">Available when needed for debugging, audit, or export.</p>
        </div>
        <button type="button" class="ghost-btn" id="toggle-raw-json">Show JSON</button>
      </div>
      <div class="json-shell">
        <pre id="raw-json" class="code-box" hidden>${escapeHtml(JSON.stringify(spec && Object.keys(spec).length > 0 ? spec : latest, null, 2))}</pre>
      </div>
    </section>
  `;

  const toggleButton = document.getElementById("toggle-raw-json");
  const rawJson = document.getElementById("raw-json");
  toggleButton.addEventListener("click", () => {
    const isHidden = rawJson.hasAttribute("hidden");
    if (isHidden) {
      rawJson.removeAttribute("hidden");
      toggleButton.textContent = "Hide JSON";
    } else {
      rawJson.setAttribute("hidden", "");
      toggleButton.textContent = "Show JSON";
    }
  });
}

async function selectPair(pair) {
  const detail = await api(`/api/pairs/${encodeURIComponent(pair)}`);
  state.selectedPair = pair;
  renderPairDetail(detail);
  renderSignalBoard(state.dashboard?.pair_signals ?? []);
  renderPairTable(state.dashboard?.pair_signals ?? []);
}

async function loadDashboard() {
  const data = await api("/api/dashboard");
  state.dashboard = data;
  document.getElementById("snapshot-status").textContent = data.latest_overview?.status ?? "ready";
  renderStats(data.stats);
  renderRunSummary("latest-overview", data.latest_overview, "No daily overview has been run yet.");
  renderRunSummary("latest-scan", data.latest_scan, "No pair scan has been run yet.");
  renderSignalBoard(data.pair_signals);
  renderPairTable(data.pair_signals);
  renderRuns(data.recent_runs);

  const availablePairs = data.pair_signals.map((entry) => entry.pair);
  if (state.selectedPair && availablePairs.includes(state.selectedPair)) {
    await selectPair(state.selectedPair);
    return;
  }

  if (availablePairs.length > 0) {
    await selectPair(availablePairs[0]);
    return;
  }

  state.selectedPair = null;
  document.getElementById("pair-detail").innerHTML =
    '<div class="muted">Run a pair scan to unlock detailed history, trend charts, and operator notes.</div>';
}

async function runAction(label, fn) {
  try {
    setActionLog(`${label} is running...`);
    const result = await fn();
    setActionLog(`${label} finished successfully.`, "ok");
    await loadDashboard();
    return result;
  } catch (error) {
    setActionLog(`${label} failed: ${error.message}`, "error");
  }
}

document.getElementById("refresh-dashboard").addEventListener("click", () => runAction("Refresh", loadDashboard));
document.getElementById("run-daily").addEventListener("click", () =>
  runAction("Daily overview", () => api("/api/runs/daily-overview", { method: "POST" }))
);
document.getElementById("run-default-scan").addEventListener("click", () =>
  runAction("Default scan", () =>
    api("/api/runs/default-scan", {
      method: "POST",
      body: JSON.stringify({ lookback_days: 90 }),
    })
  )
);

document.getElementById("pair-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = {
    base_asset: document.getElementById("base-asset").value.trim().toUpperCase(),
    quote_asset: document.getElementById("quote-asset").value.trim().toUpperCase(),
    lookback_days: Number(document.getElementById("lookback-days").value),
  };
  const result = await runAction(`Pair scan ${payload.base_asset}/${payload.quote_asset}`, () =>
    api("/api/runs/pair", {
      method: "POST",
      body: JSON.stringify(payload),
    })
  );
  if (result?.pair) {
    await selectPair(result.pair);
  }
});

loadDashboard().catch((error) => setActionLog(`Initial load failed: ${error.message}`, "error"));
