const fields = {
  badge: document.querySelector("#connectionBadge"),
  backendStatus: document.querySelector("#backendStatus"),
  apiUrl: document.querySelector("#apiUrl"),
  apiVersion: document.querySelector("#apiVersion"),
  schemaVersion: document.querySelector("#schemaVersion"),
  dataDir: document.querySelector("#dataDir"),
  dbPath: document.querySelector("#dbPath"),
  runtimeInfo: document.querySelector("#runtimeInfo"),
  rawResponse: document.querySelector("#rawResponse"),
};

function setBadge(text, state) {
  fields.badge.textContent = text;
  fields.badge.className = `badge ${state}`;
}

async function validate() {
  setBadge("Conectando…", "pending");
  fields.backendStatus.textContent = "Verificando…";

  try {
    const runtime = await window.sqxEdge.getRuntimeInfo();
    const response = await fetch(`${runtime.apiBaseUrl}/api/health`);

    if (!response.ok) {
      throw new Error(`Health check HTTP ${response.status}`);
    }

    const health = await response.json();

    fields.backendStatus.textContent = "Conectado";
    fields.apiUrl.textContent = runtime.apiBaseUrl;
    fields.apiVersion.textContent = health.app_version;
    fields.schemaVersion.textContent = health.schema_version;
    fields.dataDir.textContent = health.data_dir;
    fields.dbPath.textContent = health.database_path;
    fields.runtimeInfo.textContent = `${runtime.platform} · Electron ${runtime.appVersion}`;
    fields.rawResponse.textContent = JSON.stringify(health, null, 2);
    setBadge("Backend conectado", "ok");
  } catch (error) {
    fields.backendStatus.textContent = "Error";
    fields.rawResponse.textContent = String(error.stack || error);
    setBadge("Error de conexión", "error");
  }
}

document.querySelector("#refreshButton").addEventListener("click", validate);
validate();
