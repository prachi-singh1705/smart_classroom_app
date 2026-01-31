const canvas = document.getElementById("whiteboard");
const ctx = canvas.getContext("2d");

let drawing = false;
let mode = "pen";

canvas.width = canvas.offsetWidth;
canvas.height = 400;

// default board background
ctx.fillStyle = "#dff5df"; // light green
ctx.fillRect(0, 0, canvas.width, canvas.height);

function getPos(e) {
  const rect = canvas.getBoundingClientRect();
  return {
    x: (e.clientX || e.touches[0].clientX) - rect.left,
    y: (e.clientY || e.touches[0].clientY) - rect.top
  };
}

canvas.addEventListener("mousedown", start);
canvas.addEventListener("mousemove", draw);
canvas.addEventListener("mouseup", stop);
canvas.addEventListener("mouseleave", stop);

canvas.addEventListener("touchstart", start);
canvas.addEventListener("touchmove", draw);
canvas.addEventListener("touchend", stop);

function start(e) {
  drawing = true;
  ctx.beginPath();
  const p = getPos(e);
  ctx.moveTo(p.x, p.y);
}

function draw(e) {
  if (!drawing) return;
  const p = getPos(e);

  ctx.lineCap = "round";
  ctx.lineJoin = "round";

  if (mode === "pen") {
    ctx.strokeStyle = document.getElementById("penColor").value;
    ctx.lineWidth = document.getElementById("penSize").value;
  } else {
    ctx.strokeStyle = "#dff5df";
    ctx.lineWidth = 20;
  }

  ctx.lineTo(p.x, p.y);
  ctx.stroke();
}

function stop() {
  drawing = false;
  ctx.closePath();
}

// Toolbar buttons
document.getElementById("penBtn").onclick = () => mode = "pen";
document.getElementById("eraserBtn").onclick = () => mode = "eraser";
document.getElementById("clearBtn").onclick = () => {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = "#dff5df";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
};
