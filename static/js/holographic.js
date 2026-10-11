const THREE = window.THREE;
const video = document.querySelector('#camera');
const canvas = document.querySelector('#landmarks');
const ctx = canvas.getContext('2d');
const sceneHost = document.querySelector('#scene');
const trackingPill = document.querySelector('#tracking-pill');
const cameraState = document.querySelector('#camera-state');
const trackingValue = document.querySelector('#tracking-value');
const detectorValue = document.querySelector('#detector-value');
const handsValue = document.querySelector('#hands-value');
const objectValue = document.querySelector('#object-value');
const errorValue = document.querySelector('#error-value');
const gestureState = document.querySelector('#gesture-state');
const gestureDetail = document.querySelector('#gesture-detail');
const diagnosticBanner = document.querySelector('#diagnostic-banner');
const cameraEmpty = document.querySelector('.camera-empty');
const startButton = document.querySelector('#start-camera');
const stopButton = document.querySelector('#stop-camera');
const interactionButton = document.querySelector('#toggle-interaction');
const demoButton = document.querySelector('#demo-mode');
const handPointer = document.querySelector('#hand-pointer');
const cameraDock = document.querySelector('#camera-dock');
const cameraView = document.querySelector('#camera-view');
const cameraFocusButton = document.querySelector('#camera-focus');

if (!THREE) {
    const banner = document.querySelector('#diagnostic-banner');
    banner.textContent = '3D renderer unavailable. Check network access and reload the workspace.';
    banner.classList.add('error');
    throw new Error('Three.js failed to load.');
}

const config = { pinchGrab: 0.055, pinchRelease: 0.17, pinchHoldMs: 2000, scaleDelta: 0.018, smoothing: 0.32, stableFrames: 5, lostFrames: 12, zoomStableMs: 900, zoomCooldownMs: 1400, minScale: 0.45, maxScale: 2.8 };
const gesture = { state: 'IDLE', pinchFrames: 0, releaseFrames: 0, lostFrames: 0, pointer: new THREE.Vector2(), pinchDistance: 0, rotationAngle: 0, enabled: true, demo: false };
let handLandmarker = null;
let stream = null;
let detectorModule = null;
let lastVideoTime = -1;
let scene;
let camera;
let renderer;
let raycaster;
let objects = [];
let selected = null;
let frameRequest = null;
let pointerGrab = false;
let manualPointerAt = 0;
let manualPointerActive = false;
let pinchCandidate = null;
let pinchStartedAt = 0;
let lastZoomAt = 0;
let zoomPose = null;
let zoomPoseStartedAt = 0;
let zoomLatched = false;
let interactionMessageUntil = 0;

function setReadout(state, detail) { gestureState.textContent = state; gestureDetail.textContent = detail; }
function showInteractionMessage(state, detail, duration = 1800) { setReadout(state, detail); interactionMessageUntil = performance.now() + duration; }
function setError(message) { errorValue.textContent = message || 'NONE'; diagnosticBanner.textContent = message || 'Objects are ready. Enable the camera when you want gesture control.'; diagnosticBanner.classList.toggle('error', Boolean(message)); }
function setTracking(state, detail = '') {
    trackingPill.textContent = state;
    trackingPill.classList.toggle('live', state === 'TRACKING');
    cameraState.textContent = detail || state;
    trackingValue.textContent = state;
}
function setCameraControls(active) { startButton.disabled = active; stopButton.disabled = !active; }

function makeObject(geometry, name, color, position) {
    const material = new THREE.MeshStandardMaterial({ color, emissive: color, emissiveIntensity: .28, transparent: true, opacity: .9, roughness: .25, metalness: .55 });
    const object = new THREE.Mesh(geometry, material);
    object.name = name;
    object.position.set(...position);
    object.userData.baseScale = object.scale.clone();
    scene.add(object);
    objects.push(object);
    return object;
}

function initScene() {
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(42, Math.max(sceneHost.clientWidth, 1) / Math.max(sceneHost.clientHeight, 1), .1, 100);
    camera.position.set(0, 0, 8);
    renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(sceneHost.clientWidth, sceneHost.clientHeight);
    sceneHost.appendChild(renderer.domElement);
    raycaster = new THREE.Raycaster();
    scene.add(new THREE.AmbientLight(0x6db9d8, 2));
    const key = new THREE.PointLight(0x65edf1, 18, 14); key.position.set(-2, 3, 4); scene.add(key);
    const fill = new THREE.PointLight(0x5b9dff, 12, 12); fill.position.set(3, -2, 4); scene.add(fill);

    makeObject(new THREE.BoxGeometry(1.05, 1.05, 1.05), 'DATA CUBE', 0x5b9dff, [1.8, .95, 0]);
    makeObject(new THREE.SphereGeometry(.68, 32, 20), 'CORE SPHERE', 0x65edf1, [-1.8, .9, 0]);
    makeObject(new THREE.TorusKnotGeometry(.55, .16, 64, 12), 'ROTATION KNOT', 0xa8f0c6, [0, -1.25, 0]);
    makeObject(new THREE.BoxGeometry(1.55, .9, .12), 'SYSTEM PANEL', 0xffd083, [0, 1.9, -.3]);
    window.addEventListener('resize', resizeScene);
    if (window.ResizeObserver) new ResizeObserver(resizeScene).observe(sceneHost);
}

function resizeScene() {
    if (!renderer) return;
    camera.aspect = Math.max(sceneHost.clientWidth, 1) / Math.max(sceneHost.clientHeight, 1);
    camera.updateProjectionMatrix();
    renderer.setSize(sceneHost.clientWidth, sceneHost.clientHeight);
}

function drawLandmarks(results) {
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const connections = [[0,1],[1,2],[2,3],[3,4],[0,5],[5,6],[6,7],[7,8],[5,9],[9,10],[10,11],[11,12],[9,13],[13,14],[14,15],[15,16],[13,17],[17,18],[18,19],[19,20],[0,17]];
    for (const landmarks of results?.landmarks || []) {
        ctx.strokeStyle = 'rgba(101,237,241,.82)'; ctx.fillStyle = '#a8f0c6'; ctx.lineWidth = 2;
        for (const [from, to] of connections) { ctx.beginPath(); ctx.moveTo(landmarks[from].x * canvas.width, landmarks[from].y * canvas.height); ctx.lineTo(landmarks[to].x * canvas.width, landmarks[to].y * canvas.height); ctx.stroke(); }
        for (const point of landmarks) { ctx.beginPath(); ctx.arc(point.x * canvas.width, point.y * canvas.height, 3, 0, Math.PI * 2); ctx.fill(); }
    }
}

function distance(a, b) { return Math.hypot(a.x - b.x, a.y - b.y); }
function smoothPointer(point) { gesture.pointer.lerp(new THREE.Vector2(point.x * 2 - 1, -(point.y * 2 - 1)), config.smoothing); }
function moveSelectedToPointer() {
    if (!selected) return;
    const point = new THREE.Vector3(gesture.pointer.x, gesture.pointer.y, 0).unproject(camera);
    const direction = point.sub(camera.position).normalize();
    selected.position.lerp(camera.position.clone().add(direction.multiplyScalar(-camera.position.z / direction.z)), .42);
}
function scaleObject(object, factor) {
    if (!object) return;
    object.scale.multiplyScalar(THREE.MathUtils.clamp(factor, .88, 1.12));
    object.scale.clamp(new THREE.Vector3(config.minScale, config.minScale, config.minScale), new THREE.Vector3(config.maxScale, config.maxScale, config.maxScale));
    objectValue.textContent = object.name;
}

function distanceFromWrist(hand, index) { return distance(hand[0], hand[index]); }
function fingerExtended(hand, tip, pip) { return distanceFromWrist(hand, tip) > distanceFromWrist(hand, pip) * 1.12; }
function classifyHand(hand) {
    const extended = [fingerExtended(hand, 8, 6), fingerExtended(hand, 12, 10), fingerExtended(hand, 16, 14), fingerExtended(hand, 20, 18)];
    return extended.every(Boolean) ? 'OPEN' : extended.every(value => !value) ? 'FIST' : 'NEUTRAL';
}
function updateWorkspaceZoom(hands, now) {
    if (selected || pointerGrab || hands.length < 2) { zoomPose = null; zoomPoseStartedAt = 0; zoomLatched = false; return; }
    const first = classifyHand(hands[0]);
    const second = classifyHand(hands[1]);
    const pose = first === second && (first === 'OPEN' || first === 'FIST') ? first : 'NEUTRAL';
    if (pose === 'NEUTRAL') { zoomPose = null; zoomPoseStartedAt = 0; zoomLatched = false; return; }
    if (pose !== zoomPose) { zoomPose = pose; zoomPoseStartedAt = now; zoomLatched = false; return; }
    if (!zoomLatched && now - zoomPoseStartedAt >= config.zoomStableMs && now - lastZoomAt >= config.zoomCooldownMs) {
        document.querySelector('.holo-stage').classList.toggle('workspace-zoom-out', pose === 'FIST');
        lastZoomAt = now;
        zoomLatched = true;
        showInteractionMessage(pose === 'FIST' ? 'ZOOM OUT' : 'ZOOM IN', pose === 'FIST' ? 'Workspace zoomed out' : 'Workspace zoomed in');
    }
}

function updateInteraction(hands) {
    if (!gesture.enabled || !hands.length) return;
    if (pointerGrab || manualPointerActive || performance.now() - manualPointerAt < 800) return;
    const hand = hands[0];
    smoothPointer({ x: 1 - hand[8].x, y: hand[8].y });
    handPointer.style.left = `${((gesture.pointer.x + 1) / 2) * 100}%`;
    handPointer.style.top = `${((1 - gesture.pointer.y) / 2) * 100}%`;
    handPointer.classList.add('visible');
    const pinch = distance(hand[4], hand[8]);
    raycaster.setFromCamera(gesture.pointer, camera);
    const hovered = raycaster.intersectObjects(objects, false)[0]?.object || null;
    objects.forEach(object => { object.material.emissiveIntensity = object === hovered || object === selected ? .9 : .28; });
    if (pinch < config.pinchGrab) gesture.pinchFrames += 1; else gesture.pinchFrames = 0;
    if (pinch > config.pinchRelease) gesture.releaseFrames += 1; else gesture.releaseFrames = 0;
    if (!selected && hovered && pinch < config.pinchGrab) {
        if (pinchCandidate !== hovered) { pinchCandidate = hovered; pinchStartedAt = performance.now(); gesture.state = 'PINCHING'; }
        if (performance.now() - pinchStartedAt >= config.pinchHoldMs) { selected = hovered; gesture.pinchDistance = pinch; gesture.state = 'GRABBING'; objectValue.textContent = selected.name; showInteractionMessage('OBJECT SELECTED', `Object Selected: ${selected.name}`); }
    } else if (!selected && pinch >= config.pinchRelease) { pinchCandidate = null; pinchStartedAt = 0; }
    if (selected && gesture.releaseFrames >= 3) { const released = selected.name; selected = null; pinchCandidate = null; pinchStartedAt = 0; gesture.state = 'RELEASING'; objectValue.textContent = 'NONE'; showInteractionMessage('OBJECT RELEASED', `Object Released: ${released}`); }
    if (selected && gesture.releaseFrames < 3) {
        moveSelectedToPointer();
        if (Math.abs(pinch - gesture.pinchDistance) > config.scaleDelta) { scaleObject(selected, 1 + (pinch - gesture.pinchDistance) * 3.2); gesture.state = 'SCALING'; } else gesture.state = 'DRAGGING';
        if (hands.length >= 2 && pinch > config.pinchRelease) { const angle = Math.atan2(hands[1][0].y - hands[0][0].y, hands[1][0].x - hands[0][0].x); if (gesture.rotationAngle) selected.rotation.z += angle - gesture.rotationAngle; gesture.rotationAngle = angle; gesture.state = 'ROTATING'; }
    }
    if (!selected && hovered) { gesture.state = 'HOVERING'; objectValue.textContent = hovered.name; }
    setReadout(gesture.state, selected ? `Controlling ${selected.name}` : hovered ? `Hovering ${hovered.name}` : 'Move your index finger over an object');
}

function updateTracking(results) {
    drawLandmarks(results);
    const hands = results?.landmarks || [];
    handsValue.textContent = String(hands.length);
    if (hands.length) { gesture.lostFrames = 0; setTracking('TRACKING', 'HAND SEARCH'); updateWorkspaceZoom(hands, performance.now()); updateInteraction(hands); }
    else { gesture.lostFrames += 1; handPointer.classList.remove('visible'); zoomPose = null; zoomPoseStartedAt = 0; zoomLatched = false; setTracking('TRACKING', 'HAND LOST'); if (gesture.lostFrames > config.lostFrames) { selected = null; pinchCandidate = null; pinchStartedAt = 0; objectValue.textContent = 'NONE'; setReadout('IDLE', 'Hand lost. Interaction safely cancelled.'); } }
}

async function loadDetector() {
    if (detectorModule) return detectorModule;
    detectorValue.textContent = 'LOADING';
    detectorModule = await import('https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision/+esm');
    return detectorModule;
}

async function startCamera() {
    if (stream) return;
    setError(''); setTracking('REQUESTING', 'REQUESTING PERMISSION'); setReadout('STARTING', 'Requesting camera permission...'); startButton.disabled = true;
    try {
        if (!window.isSecureContext || !navigator.mediaDevices?.getUserMedia) throw new Error('Camera requires a secure localhost context or a supported browser.');
        stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480, facingMode: 'user' }, audio: false });
        video.srcObject = stream; await video.play(); cameraEmpty.style.display = 'none'; setTracking('STARTING', 'LOADING MODEL'); setReadout('STARTING', 'Loading local hand detector...');
        const { FilesetResolver, HandLandmarker } = await loadDetector();
        const vision = await FilesetResolver.forVisionTasks('https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision/wasm');
        handLandmarker = await HandLandmarker.createFromOptions(vision, { baseOptions: { modelAssetPath: 'https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task', delegate: 'GPU' }, runningMode: 'VIDEO', numHands: 2, minHandDetectionConfidence: .65, minHandPresenceConfidence: .65, minTrackingConfidence: .65 });
        detectorValue.textContent = 'READY'; setTracking('TRACKING', 'HAND SEARCH'); setReadout('IDLE', 'Show your hand to begin'); setCameraControls(true); if (!frameRequest) frameRequest = requestAnimationFrame(renderLoop);
    } catch (error) { const message = error?.name === 'NotAllowedError' ? 'Permission denied. Allow camera access in browser settings, then retry.' : error?.name === 'NotFoundError' ? 'No camera was found.' : error?.message || 'Camera initialization failed.'; detectorValue.textContent = 'ERROR'; setError(message); setTracking('CAMERA ERROR', 'RETRY AVAILABLE'); setReadout('ERROR', message); stopCamera(false); }
}

function stopCamera(resetError = true) { manualPointerActive = false; stream?.getTracks().forEach(track => track.stop()); stream = null; handLandmarker = null; video.srcObject = null; ctx.clearRect(0, 0, canvas.width, canvas.height); handPointer.classList.remove('visible'); cameraEmpty.style.display = 'grid'; handsValue.textContent = '0'; detectorValue.textContent = 'READY'; setTracking('CAMERA OFF', 'CAMERA OFF'); setReadout('IDLE', 'Objects remain available in demo mode'); setCameraControls(false); if (resetError) setError(''); }

function renderLoop(now) { if (handLandmarker && video.readyState >= 2 && video.currentTime !== lastVideoTime) { lastVideoTime = video.currentTime; try { updateTracking(handLandmarker.detectForVideo(video, now)); } catch (error) { setError(`Tracking error: ${error.message}`); stopCamera(false); } } objects.forEach((object, index) => { if (object !== selected) { object.rotation.x += .002 + index * .0004; object.rotation.y += .004; } }); renderer.render(scene, camera); if (interactionMessageUntil && now > interactionMessageUntil) { interactionMessageUntil = 0; setReadout('IDLE', selected ? `Controlling ${selected.name}` : 'Move your finger or cursor over an object'); } frameRequest = requestAnimationFrame(renderLoop); }

async function closeWorkspace() { stopCamera(); await fetch('/holographic/deactivate', { method: 'POST', keepalive: true }); window.location.href = '/'; }
function setCameraFocus(active) {
    document.body.classList.toggle('camera-focus', active);
    cameraFocusButton.textContent = active ? 'Minimize' : 'Expand';
    cameraFocusButton.setAttribute('aria-label', active ? 'Minimize camera preview' : 'Expand camera preview');
}
initScene(); setCameraControls(false); setTracking('CAMERA OFF', 'CAMERA OFF'); frameRequest = requestAnimationFrame(renderLoop);
startButton.addEventListener('click', startCamera);
stopButton.addEventListener('click', () => stopCamera());
renderer.domElement.addEventListener('pointermove', event => {
    {
    manualPointerActive = true;
    manualPointerAt = performance.now();
        const bounds = sceneHost.getBoundingClientRect();
        smoothPointer({ x: (event.clientX - bounds.left) / bounds.width, y: (event.clientY - bounds.top) / bounds.height });
        handPointer.style.left = `${((gesture.pointer.x + 1) / 2) * 100}%`;
        handPointer.style.top = `${((1 - gesture.pointer.y) / 2) * 100}%`;
        handPointer.classList.add('visible');
        raycaster.setFromCamera(gesture.pointer, camera);
        const hovered = raycaster.intersectObjects(objects, false)[0]?.object || null;
        objects.forEach(object => { object.material.emissiveIntensity = object === hovered || object === selected ? .9 : .28; });
        if (!pointerGrab) { objectValue.textContent = hovered?.name || 'NONE'; setReadout(hovered ? 'HOVERING' : 'IDLE', hovered ? `Pointer over ${hovered.name}` : 'Move the cursor over an object'); }
        if (pointerGrab) { moveSelectedToPointer(); gesture.state = 'DRAGGING'; setReadout('DRAGGING', `Controlling ${selected?.name || 'object'}`); }
    }
});
renderer.domElement.addEventListener('pointerdown', event => {
    if (!gesture.enabled) return;
    manualPointerAt = performance.now();
    const bounds = sceneHost.getBoundingClientRect();
    smoothPointer({ x: (event.clientX - bounds.left) / bounds.width, y: (event.clientY - bounds.top) / bounds.height });
    raycaster.setFromCamera(gesture.pointer, camera);
    selected = raycaster.intersectObjects(objects, false)[0]?.object || null;
    if (selected) { pointerGrab = true; renderer.domElement.setPointerCapture(event.pointerId); gesture.state = 'GRABBING'; objectValue.textContent = selected.name; setReadout('GRABBING', `Controlling ${selected.name}`); }
});
renderer.domElement.addEventListener('pointerup', event => { if (pointerGrab) { const released = selected?.name || 'object'; pointerGrab = false; selected = null; objectValue.textContent = 'NONE'; renderer.domElement.releasePointerCapture(event.pointerId); gesture.state = 'RELEASING'; showInteractionMessage('OBJECT RELEASED', `Object Released: ${released}`); } });
renderer.domElement.addEventListener('pointerenter', () => { manualPointerActive = true; });
renderer.domElement.addEventListener('pointerleave', () => { manualPointerActive = false; if (!pointerGrab) handPointer.classList.remove('visible'); });
renderer.domElement.addEventListener('wheel', event => { const target = selected || raycaster.intersectObjects(objects, false)[0]?.object; if (target) { event.preventDefault(); scaleObject(target, event.deltaY < 0 ? 1.08 : .92); gesture.state = 'SCALING'; setReadout('SCALING', `Resizing ${target.name}`); } }, { passive: false });
cameraFocusButton.addEventListener('click', () => setCameraFocus(!document.body.classList.contains('camera-focus')));
cameraView.addEventListener('dblclick', () => setCameraFocus(!document.body.classList.contains('camera-focus')));
interactionButton.addEventListener('click', () => { gesture.enabled = !gesture.enabled; interactionButton.textContent = gesture.enabled ? 'Disable gestures' : 'Enable gestures'; setReadout(gesture.enabled ? 'IDLE' : 'PAUSED', gesture.enabled ? 'Show your hand to begin' : 'Interaction disabled'); });
demoButton.addEventListener('click', () => { gesture.demo = !gesture.demo; demoButton.textContent = gesture.demo ? 'Exit demo mode' : 'Test without camera'; setReadout(gesture.demo ? 'DEMO MODE' : 'IDLE', gesture.demo ? 'Objects are ready for rendering tests; camera is not active.' : 'Objects remain available in demo mode'); });
document.querySelector('#exit-holo').addEventListener('click', closeWorkspace);
window.addEventListener('keydown', event => { if (event.key === 'Escape' && document.body.classList.contains('camera-focus')) setCameraFocus(false); else if (event.key === 'Escape') closeWorkspace(); });
window.addEventListener('beforeunload', () => navigator.sendBeacon('/holographic/deactivate'));
