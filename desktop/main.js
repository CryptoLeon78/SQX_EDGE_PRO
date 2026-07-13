const { app, BrowserWindow, dialog, ipcMain } = require("electron");
const path = require("path");
const net = require("net");

const { getFrontendPath } = require("./paths");
const { startBackend, stopBackend } = require("./backend-manager");

let mainWindow;
let apiBaseUrl;

function findFreePort() {
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    server.unref();
    server.on("error", reject);
    server.listen(0, "127.0.0.1", () => {
      const { port } = server.address();
      server.close(() => resolve(port));
    });
  });
}

async function waitForHealth(url, attempts = 40) {
  for (let attempt = 0; attempt < attempts; attempt += 1) {
    try {
      const response = await fetch(`${url}/api/health`);
      if (response.ok) return response.json();
    } catch (_) {
      // Backend todavía arrancando.
    }
    await new Promise((resolve) => setTimeout(resolve, 250));
  }
  throw new Error("El backend FastAPI no respondió al health check.");
}

async function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1100,
    height: 760,
    minWidth: 860,
    minHeight: 620,
    backgroundColor: "#0a0d12",
    title: "SQX Edge Pro",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
  });

  await mainWindow.loadFile(getFrontendPath());
}

app.whenReady().then(async () => {
  try {
    const port = await findFreePort();
    apiBaseUrl = `http://127.0.0.1:${port}`;

    startBackend(port);
    await waitForHealth(apiBaseUrl);

    ipcMain.handle("app:get-runtime-info", async () => ({
      apiBaseUrl,
      appVersion: app.getVersion(),
      platform: process.platform,
    }));
    ipcMain.handle("quality:select-csv", async () => {
      const result = await dialog.showOpenDialog(mainWindow, {
        title: "Selecciona los CSV de calidad MT5",
        properties: ["openFile", "multiSelections"],
        filters: [{ name: "CSV de calidad MT5", extensions: ["csv"] }],
      });
      return { canceled: result.canceled, filePaths: result.filePaths };
    });

    await createWindow();
  } catch (error) {
    console.error(error);
    app.quit();
  }
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});

app.on("before-quit", () => {
  stopBackend();
});
