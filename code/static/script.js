let isCalibrating = false;

function toggleCalibration() {
  fetch("/toggle_calibration", { method: "POST" })
    .then(res => res.json())
    .then(data => {
      isCalibrating = !isCalibrating;
      document.getElementById("calibrate-btn").innerText = isCalibrating ? "Stop Calibration" : "Start Calibration";
    });
}

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
