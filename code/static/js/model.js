import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

let scene, camera, renderer, model;
let calibrationData = {};
const boneNames = ["Bone", "Bone001", "Bone002", "Bone012", "Bone013", "Bone004", "Bone006", "Bone010", "Bone014", "Bone016", "Bone017"];  // Replace with your actual bone names
const boneRotations = {};  // key: bone name, value: bone object
const chicken1Bones = {};
const chicken2Bones = {};


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
    const model1 = gltf.scene;
    model1.position.set(-0.5, 0, 0);
    model1.lookAt(camera.position);
    scene.add(model1);
    extractBones(model1, chicken1Bones);

    loader.load('/static/models/chikenjiggle.glb', (gltf2) => {
        const model2 = gltf2.scene;
        model2.position.set(0.5, 0, 0);
        model2.lookAt(camera.position);
        scene.add(model2);
        extractBones(model2, chicken2Bones);
    });
    
    animate();
});

function extractBones(model, boneMap) {
    model.traverse((obj) => {
        if (obj.isBone && boneNames.includes(obj.name)) {
            boneMap[obj.name] = obj;
        }
    });

    if (boneMap["Bone"]) {
        boneMap["Bone"].rotation.y = Math.PI / 2;
    }
}

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

function applyRotation(boneName, encoderValue, calibration, axis, minRot, maxRot, boneMap) {
  const bone = boneMap[boneName];
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

    // Chicken 1
    const enc0 = data.motor_0;
    const cal0 = calibrationData["0"];
    const enc1 = data.motor_1;
    const cal1 = calibrationData["1"];
    const enc2 = data.motor_2;
    const cal2 = calibrationData["2"];

    applyRotation("Bone001", enc0, cal0, "z",  -Math.PI / 4, Math.PI / 4, chicken1Bones);
    applyRotation("Bone002", enc0, cal0, "z",  -Math.PI / 4, Math.PI / 4, chicken1Bones);
    applyRotation("Bone001", enc1, cal1, "x",  Math.PI / 4, -Math.PI / 4, chicken1Bones);
    applyRotation("Bone002", enc1, cal1, "x",  Math.PI / 4, -Math.PI / 4, chicken1Bones);
    applyRotation("Bone012", enc2, cal2, "z",  Math.PI/2 + Math.PI/13, Math.PI/2 - Math.PI/13, chicken1Bones);
    applyRotation("Bone013", enc2, cal2, "z",  Math.PI/1.8 - Math.PI/13, Math.PI/1.8 + Math.PI/13, chicken1Bones);

    chicken1Bones["Bone004"].rotation.x = -chicken1Bones["Bone001"].rotation.x * 1.1;
    chicken1Bones["Bone006"].rotation.x = -chicken1Bones["Bone001"].rotation.x * 1.1;
    chicken1Bones["Bone010"].rotation.x = -chicken1Bones["Bone001"].rotation.x * 1.1;

    chicken1Bones["Bone014"].rotation.z = chicken1Bones["Bone013"].rotation.z + Math.PI/52;
    chicken1Bones["Bone016"].rotation.z = chicken1Bones["Bone014"].rotation.z * 0.1;
    chicken1Bones["Bone017"].rotation.z = chicken1Bones["Bone001"].rotation.z * 2.4;


    /// Chicken 2
    const enc10 = data.motor_10;
    const cal10 = calibrationData["10"];
    const enc11 = data.motor_11;
    const cal11 = calibrationData["11"];
    const enc12 = data.motor_12;
    const cal12 = calibrationData["12"];

    // Bone controls
    applyRotation("Bone001", enc10, cal10, "z",  Math.PI / 4, -Math.PI / 4, chicken2Bones);
    applyRotation("Bone002", enc10, cal10, "z",  Math.PI / 4, -Math.PI / 4, chicken2Bones);
    applyRotation("Bone001", enc11, cal11, "x",  Math.PI / 4, -Math.PI / 4, chicken2Bones);
    applyRotation("Bone002", enc11, cal11, "x",  Math.PI / 4, -Math.PI / 4, chicken2Bones);
    applyRotation("Bone012", enc12, cal12, "z",  Math.PI/2 + Math.PI/13, Math.PI/2 - Math.PI/13, chicken2Bones);
    applyRotation("Bone013", enc12, cal12, "z",  Math.PI/1.8 - Math.PI/13, Math.PI/1.8 + Math.PI/13, chicken2Bones);

    chicken2Bones["Bone004"].rotation.x = -chicken2Bones["Bone001"].rotation.x * 1.1;
    chicken2Bones["Bone006"].rotation.x = -chicken2Bones["Bone001"].rotation.x * 1.1;
    chicken2Bones["Bone010"].rotation.x = -chicken2Bones["Bone001"].rotation.x * 1.1;

    chicken2Bones["Bone014"].rotation.z = chicken2Bones["Bone013"].rotation.z + Math.PI/52;
    chicken2Bones["Bone016"].rotation.z = chicken2Bones["Bone014"].rotation.z * 0.1;
    chicken2Bones["Bone017"].rotation.z = chicken2Bones["Bone001"].rotation.z * 2.4;


    renderer.render(scene, camera);
}
await loadCalibrationData(); // Load at start