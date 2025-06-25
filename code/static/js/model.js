import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

let scene, camera, renderer, model;
let calibrationData = {};
const boneNames = ["Bone", "Bone001", "Bone002", "Bone012", "Bone013"];  // Replace with your actual bone names
const boneRotations = {};  // key: bone name, value: bone object

// Setup scene
scene = new THREE.Scene();
scene.background = null;

camera = new THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 0.1, 100);
camera.position.set(0, 1, 1.2);

renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.getElementById("three-container").appendChild(renderer.domElement);

scene.add(new THREE.AmbientLight(0xffffff, 0.4));
const directionalLight = new THREE.DirectionalLight(0xffffff, 3);
directionalLight.position.set(1, 4, 7);
scene.add(directionalLight);

// Load model
const loader = new GLTFLoader();
loader.load('/static/models/chikenjiggle.glb', (gltf) => {
    model = gltf.scene;
    scene.add(model);

    // Log bones for inspection
    model.traverse((obj) => {
        if (obj.isBone) console.log("Bone:", obj.name);
    });

    // Get all bones we care about
    boneNames.forEach((name) => {
        const bone = model.getObjectByName(name);
        if (bone) {
            boneRotations[name] = bone;
        } else {
            console.warn(`Bone not found: ${name}`);
        }
    });

    //example: inital rotate
    const bone = model.getObjectByName("Bone");
    if (bone) {
        bone.rotation.y = Math.PI / 2;  // 90 degree rotation
    }

    animate();
});

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

//Fetch motor calibration data
async function loadCalibrationData() {
    try {
        console.log("here");
        const res = await fetch(`/static/calibration.json`);
        console.log("here2");
        calibrationData = await res.json();
        console.log("Loaded calibration:", calibrationData);
    } catch (err) {
        console.error("Failed to load calibration data:", err);
    }
}

function updateCalibrationData(newCalib) {
  calibrationData = newCalib;
  console.log("Calibration data updated:", calibrationData);
  resetBones();
}
window.updateCalibrationData = updateCalibrationData;

async function reloadCalibration() {
  try {
    const res = await fetch('/calibration-data', { cache: "no-store" });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const json = await res.json();
    updateCalibrationData(json);
  } catch (err) {
    console.error("Failed to reload calibration:", err);
  }
}
window.reloadCalibration = reloadCalibration;

//Periodically fetch encoder values
async function fetchEncoderValues() {
    try {
        const res = await fetch('/encoder_values');
        return await res.json();  // { motor_1: ..., motor_2: ..., motor_3: ... }
    } catch (err) {
        console.error("Failed to fetch encoder values:", err);
        return null;
    }
}

function resetBones() {
    for (const name of Object.keys(boneRotations)) {
        const bone = boneRotations[name];
        bone.rotation.set(0, 0, 0); // Reset all axes
    }
    const bone = model.getObjectByName("Bone");
    if (bone) {
        bone.rotation.y = Math.PI / 2;  // 90 degree rotation
    }
    console.log("Bones reset.");
}

function mapEncoderToRotation(value, min, max, minRot, maxRot) {
    const clamped = Math.max(min, Math.min(max, value));
    const ratio = (clamped - min) / (max - min);
    return minRot + ratio * (maxRot - minRot);
}

function applyRotation(boneName, encoderValue, calibration, axis, minRot, maxRot) {
  const bone = boneRotations[boneName];
  if (!bone || !calibration) return;
  const rot = mapEncoderToRotation(encoderValue, calibration.min, calibration.max, minRot, maxRot);
  bone.rotation[axis] = rot;
}


//Loop render
async function animate() {
    requestAnimationFrame(animate);

    // Fetch encoder values
    const data = await fetchEncoderValues();
    if (!data) return;

    // Motor 1
    const encoder1 = data.motor_1;
    const calibration1 = calibrationData["0"];
    // Motor 2
    const encoder2 = data.motor_2;
    const calibration2 = calibrationData["1"];
    // Motor 3
    const encoder3 = data.motor_3;
    const calibration3 = calibrationData["2"];

    // Bone controls
    applyRotation("Bone001", encoder1, calibration1, "z", -Math.PI / 4, Math.PI / 4);
    applyRotation("Bone002", encoder1, calibration1, "z", -Math.PI / 4, Math.PI / 4);
    applyRotation("Bone001", encoder2, calibration2, "x", Math.PI / 4, -Math.PI / 4);
    applyRotation("Bone002", encoder2, calibration2, "x", Math.PI / 4, -Math.PI / 4);
    applyRotation("Bone012", encoder3, calibration3, "z", Math.PI/2 - Math.PI/13, Math.PI/2 + Math.PI/13);
    applyRotation("Bone013", encoder3, calibration3, "z", Math.PI/1.8 + Math.PI/13, Math.PI/1.8 - Math.PI/13);


    renderer.render(scene, camera);
}
await loadCalibrationData(); // Load at start