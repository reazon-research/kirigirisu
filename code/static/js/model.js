import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

let scene, camera, renderer, model;
let calibData = {};
const boneNames = ["Bone"];  // Replace with your actual bone names
const boneRotations = {};  // key: bone name, value: bone object

init();

async function init() {
    // Setup scene
    scene = new THREE.Scene();
    scene.background = null;

    camera = new THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 0.1, 100);
    camera.position.set(4, 0.75, 1.5);

    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.getElementById("three-container").appendChild(renderer.domElement);

    scene.add(new THREE.AmbientLight(0xffffff, 2));

    // Load calibration data
    await loadCalibrationData();

    // Load model
    const loader = new GLTFLoader();
    loader.load('/static/models/chikenjiggle.glb', (gltf) => {
        model = gltf.scene;
        scene.add(model);

        // Get all bones we care about
        boneNames.forEach((name) => {
            const bone = model.getObjectByName(name);
            if (bone) {
                boneRotations[name] = bone;
            } else {
                console.warn(`Bone not found: ${name}`);
            }
        });

        animate();
    });
}

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

//Fetch motor calibration data
async function loadCalibrationData() {
    try {
        const res = await fetch('/static/calibration.json');
        calibrationData = await res.json();
        console.log("Loaded calibration:", calibrationData);
    } catch (err) {
        console.error("Failed to load calibration data:", err);
    }
}

await loadCalibrationData();  // Make sure this runs before animating bones


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

function mapEncoderToRotation(value, min, max, minRot, maxRot) {
    const clamped = Math.max(min, Math.min(max, value));
    const ratio = (clamped - min) / (max - min);
    return minRot + ratio * (maxRot - minRot);
}


//Loop render
async function animate() {
    requestAnimationFrame(animate);

    // Fetch encoder values
    const data = await fetchEncoderValues();
    if (!data) return;

    for (let i = 0; i < 3; i++) {
        const motorKey = `motor_${i + 1}`;
        const encoderVal = data[motorKey];
        const calib = calibrationData[String(i)];
        const boneName = boneNames[i];
        const bone = boneRotations[boneName];

        if (!bone || !calib) continue;

        // Customize rotation axis and limits here
        const minRot = -Math.PI / 4;
        const maxRot = Math.PI / 4;

        const rot = mapEncoderToRotation(encoderVal, calib.min, calib.max, minRot, maxRot);

        // Apply to desired rotation axis (e.g., .x or .z or .y)
        bone.rotation.z = rot;
    }

    renderer.render(scene, camera);
}