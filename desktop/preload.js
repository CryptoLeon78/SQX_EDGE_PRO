const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("sqxEdge", {
  getRuntimeInfo: () => ipcRenderer.invoke("app:get-runtime-info"),
});
