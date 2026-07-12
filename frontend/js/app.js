const state = {
  runtime: null,
  assets: [],
  snapshots: [],
  selectedAssetId: null,
  selectedSnapshotId: null,
  qualityAssetFilter: null,
};

const elements = {
  badge: document.querySelector("#connectionBadge"),
  assetCount: document.querySelector("#assetCount"),
  typeCount: document.querySelector("#typeCount"),
  edgeCount: document.querySelector("#edgeCount"),
  qualityCount: document.querySelector("#qualityCount"),
  tableStatus: document.querySelector("#tableStatus"),
  search: document.querySelector("#assetSearch"),
  tableBody: document.querySelector("#assetsTableBody"),
  detail: document.querySelector("#assetDetail"),
  refreshButton: document.querySelector("#refreshButton"),
  rawResponse: document.querySelector("#rawResponse"),
  qualityStatus: document.querySelector("#qualityStatus"),
  qualitySelect: document.querySelector("#qualitySnapshotSelect"),
  showSelectedQualityButton: document.querySelector("#showSelectedQualityButton"),
  showAllQualityButton: document.querySelector("#showAllQualityButton"),
  qualityEmpty: document.querySelector("#qualityEmpty"),
  qualityContent: document.querySelector("#qualityContent"),
  qualityAsset: document.querySelector("#qualityAsset"),
  qualityProvider: document.querySelector("#qualityProvider"),
  qualityImportedAt: document.querySelector("#qualityImportedAt"),
  qualitySamples: document.querySelector("#qualitySamples"),
  qualityCurrentSpread: document.querySelector("#qualityCurrentSpread"),
  qualityAvgSpread: document.querySelector("#qualityAvgSpread"),
  qualityP50: document.querySelector("#qualityP50"),
  qualityP90: document.querySelector("#qualityP90"),
  qualityP99: document.querySelector("#qualityP99"),
  qualityYearsBody: document.querySelector("#qualityYearsBody"),
  qualityHoursBody: document.querySelector("#qualityHoursBody"),
};

function setBadge(text, stateName) {
  elements.badge.textContent = text;
  elements.badge.className = `badge ${stateName}`;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function formatNumber(value, maximumFractionDigits = 2) {
  if (value === null || value === undefined || value === "") return "—";
  return new Intl.NumberFormat("es-ES", {
    maximumFractionDigits,
  }).format(Number(value));
}

function formatSpread(value) {
  if (value === null || value === undefined || value === "") return "—";
  return `${formatNumber(value, 4)} pts`;
}

function formatDate(value) {
  if (!value) return "—";
  const normalized = value.includes("T") ? value : value.replace(" ", "T");
  const date = new Date(normalized);
  return Number.isNaN(date.getTime())
    ? value
    : new Intl.DateTimeFormat("es-ES", {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(date);
}

function ratingClass(rating) {
  return {
    "++": "rating rating-plus-plus",
    "+": "rating rating-plus",
    "-": "rating rating-minus",
    "--": "rating rating-minus-minus",
  }[rating] || "rating";
}

async function request(path) {
  const response = await fetch(`${state.runtime.apiBaseUrl}${path}`);
  if (!response.ok) {
    const body = await response.text();
    throw new Error(`${response.status}: ${body || "Error de API"}`);
  }
  return response.json();
}

function getQualitySnapshotForAsset(assetId) {
  return state.snapshots.find(
    (snapshot) => snapshot.canonical_asset_id === assetId,
  );
}

function renderMetrics() {
  const types = new Set(state.assets.map((asset) => asset.asset_type));
  const edgeCount = state.assets.reduce(
    (total, asset) => total + asset.edge_count,
    0,
  );

  elements.assetCount.textContent = state.assets.length;
  elements.typeCount.textContent = types.size;
  elements.edgeCount.textContent = edgeCount;
  elements.qualityCount.textContent = state.snapshots.length;
}

function filteredAssets() {
  const search = elements.search.value.trim().toLowerCase();
  if (!search) return state.assets;

  return state.assets.filter((asset) =>
    [asset.id, asset.name, asset.asset_type, asset.subtype]
      .filter(Boolean)
      .join(" ")
      .toLowerCase()
      .includes(search),
  );
}

function renderTable() {
  const assets = filteredAssets();
  elements.tableStatus.textContent =
    `${assets.length} de ${state.assets.length} activos visibles`;

  elements.tableBody.innerHTML = assets.map((asset) => {
    const snapshot = getQualitySnapshotForAsset(asset.id);
    const quality = snapshot
      ? `<span class="quality-pill">P99 ${formatNumber(snapshot.p99, 1)}</span>`
      : `<span class="quality-missing">Sin snapshot</span>`;

    return `
      <tr data-asset-id="${escapeHtml(asset.id)}"
          class="${asset.id === state.selectedAssetId ? "selected" : ""}">
        <td class="symbol">${escapeHtml(asset.id)}</td>
        <td>${escapeHtml(asset.name)}</td>
        <td>${escapeHtml(asset.asset_type)}</td>
        <td>${escapeHtml(asset.subtype || "—")}</td>
        <td><span class="pill">${asset.edge_count}</span></td>
        <td>${quality}</td>
      </tr>
    `;
  }).join("");

  document.querySelectorAll("[data-asset-id]").forEach((row) => {
    row.addEventListener("click", () => loadAssetDetail(row.dataset.assetId));
  });
}

function renderScore(label, score) {
  return `
    <div class="score-card">
      <span>${label}</span>
      <strong>${score.score}</strong>
      <small>${score.coverage}/${score.category_count} categorías · ${score.raw_points}/${score.max_points} pts</small>
    </div>
  `;
}

function renderAssetQualityLink(assetId) {
  const snapshot = getQualitySnapshotForAsset(assetId);
  if (!snapshot) {
    return `<div class="edge-empty">No hay snapshot MT5 importado para este activo.</div>`;
  }

  return `
    <div class="asset-quality-link">
      <div>
        <span>Último snapshot MT5</span>
        <strong>${escapeHtml(snapshot.raw_symbol)} · P99 ${formatSpread(snapshot.p99)}</strong>
        <small>${formatDate(snapshot.imported_at)} · ${escapeHtml(snapshot.provider)}</small>
      </div>
      <button type="button" data-show-quality="${escapeHtml(snapshot.id)}">Ver calidad</button>
    </div>
  `;
}

function renderDetail(asset, longScore, shortScore) {
  const edges = asset.edges.length
    ? asset.edges.map((edge) => `
      <tr>
        <td>${escapeHtml(edge.category_name)}</td>
        <td><span class="dir">${escapeHtml(edge.direction)}</span></td>
        <td><span class="${ratingClass(edge.rating)}">${escapeHtml(edge.rating)}</span></td>
        <td>${escapeHtml(edge.timeframes.join(", "))}</td>
      </tr>
    `).join("")
    : `<tr><td colspan="4" class="no-data">Sin entradas Edge.</td></tr>`;

  elements.detail.innerHTML = `
    <dl class="detail-list">
      <div><dt>Símbolo</dt><dd>${escapeHtml(asset.id)}</dd></div>
      <div><dt>Nombre</dt><dd>${escapeHtml(asset.name)}</dd></div>
      <div><dt>Tipo</dt><dd>${escapeHtml(asset.asset_type)} · ${escapeHtml(asset.subtype || "—")}</dd></div>
      <div><dt>Versión</dt><dd>${escapeHtml(asset.catalog_version)}</dd></div>
    </dl>

    <div class="scores">
      ${renderScore("Score Long", longScore)}
      ${renderScore("Score Short", shortScore)}
    </div>

    ${renderAssetQualityLink(asset.id)}

    <h3>Entradas Edge</h3>
    <div class="edge-table-wrap">
      <table class="edge-table">
        <thead>
          <tr><th>Categoría</th><th>Dir.</th><th>Rating</th><th>TF</th></tr>
        </thead>
        <tbody>${edges}</tbody>
      </table>
    </div>
  `;

  const qualityButton = elements.detail.querySelector("[data-show-quality]");
  if (qualityButton) {
    qualityButton.addEventListener("click", () => {
      state.qualityAssetFilter = asset.id;
      selectQualitySnapshot(Number(qualityButton.dataset.showQuality));
      document.querySelector(".quality-panel").scrollIntoView({ behavior: "smooth" });
    });
  }
}

async function loadAssetDetail(assetId) {
  try {
    elements.detail.innerHTML = '<div class="empty-state">Cargando detalle y score…</div>';

    const [asset, longScore, shortScore] = await Promise.all([
      request(`/api/assets/${encodeURIComponent(assetId)}`),
      request(`/api/assets/${encodeURIComponent(assetId)}/score?direction=L`),
      request(`/api/assets/${encodeURIComponent(assetId)}/score?direction=S`),
    ]);

    state.selectedAssetId = asset.id;
    renderTable();
    renderDetail(asset, longScore, shortScore);
  } catch (error) {
    elements.detail.innerHTML =
      `<div class="empty-state">${escapeHtml(error.message)}</div>`;
  }
}

function snapshotLabel(snapshot) {
  return `${snapshot.canonical_asset_id} · ${formatDate(snapshot.imported_at)} · ${snapshot.provider}`;
}

function renderQualitySelector() {
  const visibleSnapshots = state.qualityAssetFilter
    ? state.snapshots.filter(
      (snapshot) => snapshot.canonical_asset_id === state.qualityAssetFilter,
    )
    : state.snapshots;

  elements.qualitySelect.innerHTML = visibleSnapshots.length
    ? visibleSnapshots.map((snapshot) => `
      <option value="${snapshot.id}"
        ${snapshot.id === state.selectedSnapshotId ? "selected" : ""}>
        ${escapeHtml(snapshotLabel(snapshot))}
      </option>
    `).join("")
    : `<option value="">Sin snapshots disponibles</option>`;

  const isEnabled = visibleSnapshots.length > 0;
  elements.qualitySelect.disabled = !isEnabled;
  elements.showSelectedQualityButton.disabled = !isEnabled;
  elements.showAllQualityButton.disabled = state.snapshots.length === 0;

  if (state.qualityAssetFilter) {
    elements.qualityStatus.textContent =
      `Mostrando snapshots de ${state.qualityAssetFilter}`;
  } else {
    elements.qualityStatus.textContent =
      `${state.snapshots.length} snapshot(s) MT5 disponibles`;
  }
}

async function selectQualitySnapshot(snapshotId) {
  if (!snapshotId) return;

  try {
    state.selectedSnapshotId = snapshotId;
    renderQualitySelector();

    elements.qualityEmpty.hidden = false;
    elements.qualityContent.hidden = true;
    elements.qualityEmpty.textContent = "Cargando detalle del snapshot…";

    const snapshot = await request(`/api/quality/${snapshotId}`);
    renderQualityDetail(snapshot);
  } catch (error) {
    elements.qualityContent.hidden = true;
    elements.qualityEmpty.hidden = false;
    elements.qualityEmpty.textContent = `No se pudo cargar la calidad: ${error.message}`;
  }
}

function renderQualityDetail(snapshot) {
  elements.qualityEmpty.hidden = true;
  elements.qualityContent.hidden = false;

  elements.qualityAsset.textContent = snapshot.canonical_asset_id;
  elements.qualityProvider.textContent = snapshot.provider;
  elements.qualityImportedAt.textContent = formatDate(snapshot.imported_at);
  elements.qualitySamples.textContent = formatNumber(snapshot.samples_count, 0);

  elements.qualityCurrentSpread.textContent = formatSpread(snapshot.current_spread);
  elements.qualityAvgSpread.textContent = formatSpread(snapshot.avg_spread);
  elements.qualityP50.textContent = formatSpread(snapshot.p50);
  elements.qualityP90.textContent = formatSpread(snapshot.p90);
  elements.qualityP99.textContent = formatSpread(snapshot.p99);

  elements.qualityYearsBody.innerHTML = snapshot.years.length
    ? snapshot.years.map((row) => `
      <tr>
        <td class="symbol">${row.year}</td>
        <td>${formatSpread(row.avg_spread)}</td>
        <td>${formatSpread(row.p50)}</td>
        <td>${formatSpread(row.p90)}</td>
        <td>${formatSpread(row.p99)}</td>
        <td>${formatSpread(row.max_spread)}</td>
        <td>${formatNumber(row.samples_count, 0)}</td>
      </tr>
    `).join("")
    : `<tr><td colspan="7" class="no-data">Sin desglose anual.</td></tr>`;

  elements.qualityHoursBody.innerHTML = snapshot.hours.length
    ? snapshot.hours.map((row) => `
      <tr>
        <td class="symbol">${String(row.hour).padStart(2, "0")}:00</td>
        <td><span class="session session-${String(row.session).toLowerCase()}">${escapeHtml(row.session)}</span></td>
        <td>${formatSpread(row.avg_spread)}</td>
        <td>${formatSpread(row.p50)}</td>
        <td>${formatSpread(row.p90)}</td>
        <td>${formatSpread(row.p99)}</td>
        <td>${formatNumber(row.samples_count, 0)}</td>
      </tr>
    `).join("")
    : `<tr><td colspan="7" class="no-data">Sin desglose horario.</td></tr>`;
}

async function loadApplicationData() {
  setBadge("Cargando datos…", "pending");
  elements.tableStatus.textContent = "Consultando API local…";
  elements.qualityStatus.textContent = "Consultando snapshots MT5…";

  try {
    state.runtime = await window.sqxEdge.getRuntimeInfo();

    const [health, assetsPayload, qualityPayload] = await Promise.all([
      request("/api/health"),
      request("/api/assets"),
      request("/api/quality"),
    ]);

    state.assets = assetsPayload.assets;
    state.snapshots = qualityPayload.snapshots;
    state.qualityAssetFilter = null;

    renderMetrics();
    renderTable();
    renderQualitySelector();

    elements.rawResponse.textContent = JSON.stringify(
      { health, assets: assetsPayload, quality: qualityPayload },
      null,
      2,
    );

    setBadge("Catálogo y calidad MT5 conectados", "ok");

    if (state.assets.length > 0 && !state.selectedAssetId) {
      const defaultAsset =
        state.assets.find((asset) => asset.id === "EURUSD") || state.assets[0];
      await loadAssetDetail(defaultAsset.id);
    }

    if (state.snapshots.length > 0) {
      await selectQualitySnapshot(state.snapshots[0].id);
    } else {
      elements.qualityEmpty.hidden = false;
      elements.qualityContent.hidden = true;
      elements.qualityEmpty.textContent =
        "Todavía no hay snapshots MT5 importados.";
    }
  } catch (error) {
    elements.tableStatus.textContent = "Error de conexión";
    elements.qualityStatus.textContent = "Error de conexión";
    elements.rawResponse.textContent = String(error.stack || error);
    setBadge("Error de conexión", "error");
  }
}

elements.search.addEventListener("input", renderTable);

elements.refreshButton.addEventListener("click", () => {
  state.selectedAssetId = null;
  state.selectedSnapshotId = null;
  loadApplicationData();
});

elements.qualitySelect.addEventListener("change", () => {
  selectQualitySnapshot(Number(elements.qualitySelect.value));
});

elements.showSelectedQualityButton.addEventListener("click", () => {
  selectQualitySnapshot(Number(elements.qualitySelect.value));
});

elements.showAllQualityButton.addEventListener("click", () => {
  state.qualityAssetFilter = null;
  renderQualitySelector();
  if (state.snapshots.length > 0) {
    selectQualitySnapshot(state.snapshots[0].id);
  }
});

loadApplicationData();
