// Adjust if backend isn't on localhost:8000 in your environment
const BACKEND_BASE = "http://localhost:8000";

const startUrlInput = document.getElementById("start_url");
const baseUrlInput = document.getElementById("base_url");
const nextSelectorInput = document.getElementById("next_selector");
const outputFilenameInput = document.getElementById("output_filename");
const darkModeInput = document.getElementById("dark_mode");

const generateBtn = document.getElementById("generate_btn");
const downloadBtn = document.getElementById("download_btn");
const statusDiv = document.getElementById("status");

let lastGeneratedFilename = null;

generateBtn.addEventListener("click", async () => {
  statusDiv.textContent = "Generating PDF... this may take a while.";
  downloadBtn.disabled = true;

  const payload = {
    start_url: startUrlInput.value.trim(),
    base_url: baseUrlInput.value.trim(),
    next_selector: nextSelectorInput.value.trim(),
    output_filename: outputFilenameInput.value.trim(),
    dark_mode: darkModeInput.checked,
  };

  try {
    const res = await fetch(`${BACKEND_BASE}/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Failed to generate");
    }

    const data = await res.json();
    lastGeneratedFilename = data.filename;
    statusDiv.textContent = `Success! Generated: ${data.filename}`;
    downloadBtn.disabled = false;
  } catch (e) {
    console.error(e);
    statusDiv.textContent = "Error: " + e.message;
  }
});

downloadBtn.addEventListener("click", () => {
  if (!lastGeneratedFilename) {
    statusDiv.textContent = "No PDF generated yet.";
    return;
  }

  const url = `${BACKEND_BASE}/download?filename=${encodeURIComponent(
    lastGeneratedFilename
  )}`;

  // Simple download via hidden link
  const a = document.createElement("a");
  a.href = url;
  a.download = lastGeneratedFilename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
});
