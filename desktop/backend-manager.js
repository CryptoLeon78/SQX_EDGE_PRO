const { spawn } = require("child_process");
const path = require("path");
const { getBackendDir } = require("./paths");

let backendProcess = null;

function getPythonCommand() {
  return process.platform === "win32" ? "python" : "python3";
}

function startBackend(port) {
  const backendDir = getBackendDir();

  backendProcess = spawn(
    getPythonCommand(),
    ["-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", String(port)],
    {
      cwd: backendDir,
      env: {
        ...process.env,
        PYTHONPATH: backendDir,
      },
      stdio: ["ignore", "pipe", "pipe"],
      windowsHide: true,
    }
  );

  backendProcess.stdout.on("data", (data) => console.log(`[backend] ${data}`));
  backendProcess.stderr.on("data", (data) => console.error(`[backend] ${data}`));
  backendProcess.on("exit", (code) => {
    console.log(`[backend] exited with code ${code}`);
    backendProcess = null;
  });

  return backendProcess;
}

function stopBackend() {
  if (backendProcess && !backendProcess.killed) {
    backendProcess.kill();
  }
  backendProcess = null;
}

module.exports = {
  startBackend,
  stopBackend,
};
