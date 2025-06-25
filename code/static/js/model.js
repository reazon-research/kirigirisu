import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const scene = new THREE.Scene();
scene.background = null;

const camera = new THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 0.1, 100);
camera.position.set(0, 1, 1.2);

const container = document.getElementById('three-container');
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);
container.appendChild(renderer.domElement);

// Add light
scene.add(new THREE.AmbientLight(0xffffff, 1));

// Load glTF model
const loader = new GLTFLoader();
let mixer;
loader.load('/static/models/chikenjiggle.glb', function (gltf) {
    const model = gltf.scene;
    scene.add(model);

    // Log bones for inspection
    model.traverse((obj) => {
        if (obj.isBone) console.log("Bone:", obj.name);
    });

    // EXAMPLE: Rotate a bone (replace "Bone.001" with your actual name)
    const bone = model.getObjectByName("Bone");
    if (bone) {
        bone.rotation.y = Math.PI / 2;  // 90 degree rotation
    }
});

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}
animate();
