const state = {
  runtime: null,
  assets: [],
  selectedAssetId: null,
};

const elements = {
  badge: document.querySelector("#connectionBadge"),
  assetCount: document.querySelector("#assetCount"),
  typeCount: document.querySelector("#typeCount"),
  edgeCount: document.querySelector("#edgeCount"),
  apiPort: document.querySelector("#apiPort"),
  tableStatus: document.querySelector("#tableStatus"),
  search: document.querySelector("#assetSearch"),
  tableBody: document.querySelector("#assetsTableBody"),
  detail: document.querySelector("#assetDetail"),
  rawResponse: document.querySelector("#rawResponse"),
  refreshButton: document.querySelector("#refreshButton"),
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

function ratingClass(rating) {
  return {
    "++": "rating rating-plus-plus",
    "+": "rating rating-plus",
    "-": "rating rating-minus",
    "--": "rating rating-minus-minus",
  }[rating] || "rating";
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
  elements.apiPort.textContent = new URL(state.runtime.apiBaseUrl).port;
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
  elements.tableStatus.textContent = `${assets.length} de ${state.assets.length} activos visibles`;

  elements.tableBody.innerHTML = assets.map((asset) => `
    <tr data-asset-id="${escapeHtml(asset.id)}"
        class="${asset.id === state.selectedAssetId ? "selected" : ""}">
      <td class="symbol">${escapeHtml(asset.id)}</td>
      <td>${escapeHtml(asset.name)}</td>
      <td>${escapeHtml(asset.asset_type)}</td>
      <td>${escapeHtml(asset.subtype || "—")}</td>
      <td><span class="pill">${asset.edge_count}</span></td>
    </tr>
  `).join("");

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
}

async function loadAssetDetail(assetId) {
  try {
    elements.detail.innerHTML = '<div class="empty-state">Cargando detalle y score…</div>';

    const [assetResponse, longResponse, shortResponse] = await Promise.all([
      fetch(`${state.runtime.apiBaseUrl}/api/assets/${assetId}`),
      fetch(`${state.runtime.apiBaseUrl}/api/assets/${assetId}/score?direction=L`),
      fetch(`${state.runtime.apiBaseUrl}/api/assets/${assetId}/score?direction=S`),
    ]);

    if (!assetResponse.ok || !longResponse.ok || !shortResponse.ok) {
      throw new Error("No se pudo obtener el detalle completo.");
    }

    const [asset, longScore, shortScore] = await Promise.all([
      assetResponse.json(),
      longResponse.json(),
      shortResponse.json(),
    ]);

    state.selectedAssetId = asset.id;
    renderTable();
    renderDetail(asset, longScore, shortScore);
  } catch (error) {
    elements.detail.innerHTML = `<div class="empty-state">${escapeHtml(error.message)}</div>`;
  }
}

async function loadCatalog() {
  setBadge("Cargando catálogo…", "pending");
  elements.tableStatus.textContent = "Consultando API local…";

  try {
    state.runtime = await window.sqxEdge.getRuntimeInfo();

    const [healthResponse, assetsResponse] = await Promise.all([
      fetch(`${state.runtime.apiBaseUrl}/api/health`),
      fetch(`${state.runtime.apiBaseUrl}/api/assets`),
    ]);

    if (!healthResponse.ok || !assetsResponse.ok) {
      throw new Error("El backend no respondió correctamente.");
    }

    const health = await healthResponse.json();
    const payload = await assetsResponse.json();
    state.assets = payload.assets;

    renderMetrics();
    renderTable();
    elements.rawResponse.textContent = JSON.stringify(
      { health, assets: payload },
      null,
      2,
    );

    setBadge("Catálogo y scoring conectados", "ok");

    if (state.assets.length > 0 && !state.selectedAssetId) {
      const defaultAsset = state.assets.find((asset) => asset.id === "EURUSD") || state.assets[0];
      await loadAssetDetail(defaultAsset.id);
    }
  } catch (error) {
    elements.tableStatus.textContent = "Error de conexión";
    elements.rawResponse.textContent = String(error.stack || error);
    setBadge("Error de conexión", "error");
  }
}

elements.search.addEventListener("input", renderTable);
elements.refreshButton.addEventListener("click", loadCatalog);

loadCatalog();
