let isCalibrating = false;
let progressBar = document.getElementById("calibration-progress");

// On button click
function toggleCalibration() {
  fetch("/toggle_calibration", { method: "POST" })
    .then(res => res.json())
    .then(async data => {
      isCalibrating = data.status === "started";
      console.log("[JS] toggleCalibration → isCalibrating =", isCalibrating, "| response =", data.status);
      updateButton();

      if (isCalibrating) {
        startProgressBar(10);
      } else {
        resetProgressBar();

        // Calibration just stopped
        if (data.status === "stopped") {
          if (data.calibration) {
            console.log("good");
            updateCalibrationData(data.calibration);
          } else {
            console.log("bad");
            // Fallback: reload from JSON file
            await reloadCalibration();
          }
        }
      }
    })
    .catch(err => {
      console.error("Toggle calibration error:", err);
    });
}

// Polling for backend
function pollCalibrationStatus() {
  setInterval(() => {
    fetch("/status")
      .then(res => res.json())
      .then(async data => {
        const prevState = isCalibrating;
        isCalibrating = data.running;
        //console.log("[JS] /status → isCalibrating =", isCalibrating);

        if (prevState !== isCalibrating) {
          updateButton();

          if (isCalibrating) {
            startProgressBar(10);
          } else {
            resetProgressBar();
            //console.log("polling said false");
            if (data.calibration) {
              console.log("good");
              updateCalibrationData(data.calibration);
            } else {
              console.log("bad");
              // Fallback: reload from JSON file
              await reloadCalibration();
            }
          }
        }
      });
  }, 500);
}

function updateButton() {
  console.log("updatebuttoned");
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

function pollEncoderValues() {
  setInterval(() => {
    fetch("/encoder_values")
      .then(res => res.json())
      .then(data => {
        document.getElementById("m1").innerText = data.motor_1;
        document.getElementById("m2").innerText = data.motor_2;
        document.getElementById("m3").innerText = data.motor_3;
      });
  }, 100);
}

// Loops
pollCalibrationStatus();
pollEncoderValues();
