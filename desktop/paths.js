const path = require("path");
const { app } = require("electron");

function getProjectRoot() {
  return path.resolve(__dirname, "..");
}

function getFrontendPath() {
  return path.join(getProjectRoot(), "frontend", "index.html");
}

function getBackendDir() {
  return path.join(getProjectRoot(), "backend");
}

function getUserDataDir() {
  return app.getPath("userData");
}

module.exports = {
  getProjectRoot,
  getFrontendPath,
  getBackendDir,
  getUserDataDir,
};
