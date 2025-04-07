let socket;
let video = document.getElementById('video');
let canvas = document.getElementById('canvas');
let ctx = canvas.getContext('2d');
let streaming = false;
let streamingInterval;

function onOpenCvReady() {
  console.log("✅ OpenCV.js is ready!");

  // Connect WebSocket
  socket = new WebSocket("ws://localhost:8765");
  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    document.getElementById("animal-name").innerText = data.name;
    document.getElementById("animal-fact").innerText = data.fact;
    document.getElementById("animal-img").src = data.image;
    const audio = document.getElementById("animal-sound");
    audio.src = data.sound;
    audio.play();
  };
}

function onOpenCvFail() {
  alert("❌ OpenCV.js not ready. Please wait.");
}

function startCamera() {
  navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
      video.srcObject = stream;
      video.play();

      streamingInterval = setInterval(() => {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        const imageData = canvas.toDataURL('image/jpeg');

        // Send to backend for processing (via REST or WebSocket later)
        // Placeholder: just log for now
        console.log("📷 Frame captured.");
      }, 2000);
    });
}

function stopCamera() {
  if (video.srcObject) {
    video.srcObject.getTracks().forEach(track => track.stop());
    video.srcObject = null;
    clearInterval(streamingInterval);
    console.log("❌ Camera stopped");
  }
}
