const dropZone = document.getElementById("drop-zone");
const dropText = document.getElementById("drop-text");
const fileInput = document.getElementById("file-input");
const checkBtn = document.getElementById("check-btn");

const statusText = document.getElementById("status-text");
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

let imageFile = null;
let imageBitmap = null;

dropZone.addEventListener("click", () => fileInput.click());

dropZone.addEventListener("dragover", e => e.preventDefault());

dropZone.addEventListener("drop", e => {
  e.preventDefault();
  imageFile = e.dataTransfer.files[0];
  loadImage();
});

fileInput.addEventListener("change", () => {
  imageFile = fileInput.files[0];
  loadImage();
});

async function loadImage() {
  if (!imageFile) return;

  dropText.innerHTML = `✔ Файл загружен:<br>${imageFile.name}`;

  imageBitmap = await createImageBitmap(imageFile);

  canvas.width = imageBitmap.width;
  canvas.height = imageBitmap.height;

  ctx.drawImage(imageBitmap, 0, 0);
  checkBtn.disabled = false;
}

checkBtn.addEventListener("click", async () => {
  if (!imageFile || !imageBitmap) return;

  statusText.textContent = "⏳ Анализ изображения...";
  statusText.style.color = "#facc15";

  const formData = new FormData();
  formData.append("file", imageFile);

  try {
    const response = await fetch("http://127.0.0.1:8000/predict", {
      method: "POST",
      body: formData
    });

    const data = await response.json();

    drawResult(data);

    statusText.textContent = data.violation
      ? "❌ " + data.message
      : "✅ " + data.message;

    statusText.style.color = data.violation ? "#ef4444" : "#22c55e";

  } catch (err) {
    statusText.textContent = "Ошибка соединения с сервером";
    statusText.style.color = "#facc15";
    console.error(err);
  }
});

function drawResult(data) {
  ctx.drawImage(imageBitmap, 0, 0);

  if (!data.motorcycle_bbox) return;

  const bbox = data.motorcycle_bbox;

  const x = bbox.x * canvas.width;
  const y = bbox.y * canvas.height;
  const w = bbox.w * canvas.width;
  const h = bbox.h * canvas.height;

  ctx.lineWidth = 4;
  ctx.strokeStyle = data.violation ? "#ef4444" : "#22c55e";
  ctx.strokeRect(x, y, w, h);
}