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

function renderDetail(asset) {
  const edgeNotice = asset.edge_count === 0
    ? `<p class="edge-empty">Aún no hay entradas Edge para este activo. El siguiente bloque añadirá categorías, ratings, direcciones y scoring desde el backend.</p>`
    : "";

  elements.detail.innerHTML = `
    <dl class="detail-list">
      <div><dt>Símbolo</dt><dd>${escapeHtml(asset.id)}</dd></div>
      <div><dt>Nombre</dt><dd>${escapeHtml(asset.name)}</dd></div>
      <div><dt>Tipo</dt><dd>${escapeHtml(asset.asset_type)}</dd></div>
      <div><dt>Subtipo</dt><dd>${escapeHtml(asset.subtype || "—")}</dd></div>
      <div><dt>Activo</dt><dd>${asset.enabled ? "Sí" : "No"}</dd></div>
      <div><dt>Versión catálogo</dt><dd>${escapeHtml(asset.catalog_version)}</dd></div>
      <div><dt>Entradas Edge</dt><dd>${asset.edge_count}</dd></div>
    </dl>
    ${edgeNotice}
  `;
}

async function loadAssetDetail(assetId) {
  try {
    const response = await fetch(`${state.runtime.apiBaseUrl}/api/assets/${assetId}`);
    if (!response.ok) throw new Error(`Detalle no disponible: HTTP ${response.status}`);

    const asset = await response.json();
    state.selectedAssetId = asset.id;
    renderTable();
    renderDetail(asset);
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

    setBadge("Catálogo conectado", "ok");

    if (state.assets.length > 0 && !state.selectedAssetId) {
      await loadAssetDetail(state.assets.find((asset) => asset.id === "EURUSD")?.id || state.assets[0].id);
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
