let isCalibrating = false;
let progressBar = document.getElementById("calibration-progress");

function toggleCalibration() {
  fetch("/toggle_calibration", { method: "POST" })
    .then(res => res.json())
    .then(data => {
      isCalibrating = data.status === "started";
      updateButton();
      if (isCalibrating) startProgressBar(10);
      else resetProgressBar();
    });
}

function updateButton() {
  const btn = document.getElementById("calibrate-btn");
  const span = btn.querySelector("span");
  span.innerText = isCalibrating ? "Stop Calibration" : "Start Calibration";
  btn.classList.toggle("active", isCalibrating);
}

function startProgressBar(duration) {
  progressBar.style.transition = "none";
  progressBar.style.width = "100%";
  void progressBar.offsetWidth;
  progressBar.style.transition = `width ${duration}s linear`;
  progressBar.style.width = "0%";
}

function resetProgressBar() {
  progressBar.style.transition = "none";
  progressBar.style.width = "0%";
}

function pollCalibrationStatus() {
  setInterval(() => {
    fetch("/status")
      .then(res => res.json())
      .then(data => {
        const prev = isCalibrating;
        isCalibrating = data.running;
        if (prev !== isCalibrating) {
          updateButton();
          if (!isCalibrating) resetProgressBar();
        }
      });
  }, 1000);
}

pollCalibrationStatus();

function pollEncoderValues() {
  setInterval(() => {
    fetch("/encoder_values")
      .then(res => res.json())
      .then(data => {
        document.getElementById("m1").innerText = data.motor_1;
        document.getElementById("m2").innerText = data.motor_2;
        document.getElementById("m3").innerText = data.motor_3;
      });
  }, 250);
}

pollEncoderValues();
