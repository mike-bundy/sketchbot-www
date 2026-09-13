/**
 * Sketchbot Studios — progressive 3D + immersive web.
 *
 * <div class="stage" data-usdz="…" data-poster="…" data-env="…" data-name="…">
 *   Tier 1  native <model> (Safari on visionOS 27, HTMLModelElement) — stagemode="orbit";
 *           the viewer can pinch a model and drag it out of the page into the room.
 *   Tier 2  three.js USDLoader rendering the same USDZ (desktop/mobile browsers).
 *   Tier 3  the poster image.
 *   AR Quick Look (<a rel="ar">) is offered where relList.supports('ar').
 *
 * <div class="immersive" data-backdrop="…usdz" data-audio="…" data-env="…">
 *   visionOS 27 Safari: model.requestImmersive() (button enables when the environment is ready).
 *   Elsewhere: nothing — the poster and copy stand on their own.
 *
 * Plain ES module; three.js comes from the importmap in the page and only downloads
 * when a tier-2 view actually mounts.
 */
const supportsModel = 'HTMLModelElement' in window;
const supportsAR = (() => { try { return document.createElement('a').relList.supports('ar'); } catch { return false; } })();
const READY_TIMEOUT = 20000;

document.querySelectorAll('.stage[data-usdz]').forEach(mountStage);
document.querySelectorAll('.immersive[data-backdrop]').forEach(mountImmersive);

function status(stage, tier, text) {
  const s = stage.querySelector('.status'); if (!s) return; s.dataset.tier = tier; s.textContent = text;
}

function mountStage(stage) {
  const { usdz, poster, env, name = 'model' } = stage.dataset;
  const hud = stage.querySelector('.hud');
  if (supportsAR && hud) {
    const a = document.createElement('a'); a.rel = 'ar'; a.href = usdz; a.className = 'btn btn--ghost';
    a.innerHTML = `<img src="${poster}" alt="" style="display:none">View in your space (AR)`; // img child keeps Quick Look from navigating
    hud.append(a);
  }
  if (supportsModel) return mountNative(stage, usdz, env, poster, name);
  return mountThree(stage, usdz, poster, name);
}

function mountNative(stage, usdz, env, poster, name) {
  stage.classList.add('is-loading');
  const m = document.createElement('model');
  m.setAttribute('stagemode', 'orbit'); m.setAttribute('autoplay', ''); m.setAttribute('loop', '');
  if (env) m.setAttribute('environmentmap', env);
  const src = document.createElement('source'); src.src = usdz; src.type = 'model/vnd.usdz+zip'; m.append(src);
  m.setAttribute('aria-label', name);
  stage.prepend(m);
  status(stage, 'native', 'Spatial · pinch to orbit · drag out into your room');
  const timeout = setTimeout(() => { m.remove(); mountThree(stage, usdz, poster, name); }, READY_TIMEOUT);
  (m.ready || Promise.resolve()).then(() => { clearTimeout(timeout); stage.classList.remove('is-loading'); stage.querySelector('img.poster')?.remove(); })
    .catch(() => { clearTimeout(timeout); m.remove(); mountThree(stage, usdz, poster, name); });
}

async function mountThree(stage, usdz, poster, name) {
  stage.classList.add('is-loading');
  status(stage, 'three', 'Loading 3D…');
  try {
    const THREE = await import('three');
    const { USDLoader } = await import('three/addons/loaders/USDLoader.js');
    const { OrbitControls } = await import('three/addons/controls/OrbitControls.js');
    const { RoomEnvironment } = await import('three/addons/environments/RoomEnvironment.js');
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.05;
    const scene = new THREE.Scene();
    const pmrem = new THREE.PMREMGenerator(renderer); scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
    const cam = new THREE.PerspectiveCamera(38, 1, 0.01, 1000);
    const loader = new USDLoader();
    const obj = await new Promise((res, rej) => loader.load(usdz, res, undefined, rej));
    // Materials: USD emissive textures need a non-black emissive colour in three.js.
    obj.traverse(o => { if (o.isMesh && o.material) { const mats = Array.isArray(o.material) ? o.material : [o.material];
      for (const m of mats) { if (m.emissiveMap && m.emissive && m.emissive.getHex() === 0) m.emissive.setHex(0xffffff); m.side = THREE.DoubleSide; } } });
    // Fit: union of mesh boxes, ignoring one outsized mesh (ground planes / backdrops) if present.
    obj.updateMatrixWorld(true);
    const boxes = []; obj.traverse(o => { if (o.isMesh) { const b = new THREE.Box3().setFromObject(o); if (!b.isEmpty()) boxes.push(b); } });
    const vol = b => { const z = b.getSize(new THREE.Vector3()); return Math.max(z.x, z.y, z.z); };
    boxes.sort((a, b) => vol(b) - vol(a));
    let use = boxes;
    if (boxes.length > 1 && vol(boxes[0]) > 4 * vol(boxes[1])) use = boxes.slice(1);
    const box = use.reduce((u, b) => u.union(b), new THREE.Box3());
    const size = box.getSize(new THREE.Vector3()); const c = box.getCenter(new THREE.Vector3());
    const s = 1.6 / Math.max(size.x, size.y, size.z || 1);
    const rig = new THREE.Group(); rig.add(obj); rig.scale.setScalar(s); rig.position.copy(c).multiplyScalar(-s);
    scene.add(rig);
    const key = new THREE.DirectionalLight(0xffffff, 1.6); key.position.set(2, 3, 2); scene.add(key);
    scene.add(new THREE.AmbientLight(0xffffff, .25));
    cam.position.set(0, .35, 3.2);
    const ctl = new OrbitControls(cam, renderer.domElement); ctl.enableDamping = true; ctl.autoRotate = true; ctl.autoRotateSpeed = 1.2; ctl.enablePan = false; ctl.minDistance = 1.6; ctl.maxDistance = 6;
    stage.querySelector('img.poster')?.remove(); stage.prepend(renderer.domElement);
    const fit = () => { const w = stage.clientWidth, h = stage.clientHeight; renderer.setSize(w, h, false); cam.aspect = w / h; cam.updateProjectionMatrix(); };
    new ResizeObserver(fit).observe(stage); fit();
    let running = true;
    new IntersectionObserver(es => es.forEach(e => running = e.isIntersecting)).observe(stage);
    renderer.setAnimationLoop(() => { if (!running) return; ctl.update(); renderer.render(scene, cam); });
    stage.classList.remove('is-loading');
    status(stage, 'three', `${name} · drag to orbit`);
  } catch (e) {
    console.warn('3D fallback failed', e);
    stage.classList.remove('is-loading');
    status(stage, 'poster', 'Preview');
  }
}

function mountImmersive(root) {
  const { backdrop, audio, env } = root.dataset;
  const btn = root.querySelector('[data-enter]'); const note = root.querySelector('[data-status]');
  const say = t => { if (note) note.textContent = t || ''; };
  if (!supportsModel) { if (btn) btn.hidden = true; return; }
  const m = document.createElement('model'); m.setAttribute('aria-hidden', 'true');
  if (env) m.setAttribute('environmentmap', env);
  const src = document.createElement('source'); src.src = backdrop; src.type = 'model/vnd.usdz+zip'; m.append(src);
  root.prepend(m);
  if (!('requestImmersive' in m)) { m.remove(); if (btn) btn.hidden = true; return; }
  // visionOS 27 — programmatic immersion with audio.
  let ctx = null, buf = null, srcNode = null;
  if (audio) fetch(audio).then(r => r.arrayBuffer()).then(b => { ctx = new (window.AudioContext || window.webkitAudioContext)(); return ctx.decodeAudioData(b); }).then(d => buf = d).catch(() => {});
  const start = () => { if (!ctx || !buf) return; if (ctx.state === 'suspended') ctx.resume(); stop(); srcNode = ctx.createBufferSource(); srcNode.buffer = buf; srcNode.loop = true; srcNode.connect(ctx.destination); srcNode.start(0); };
  const stop = () => { if (srcNode) { try { srcNode.stop(); } catch {} srcNode.disconnect(); srcNode = null; } };
  if (btn) { btn.disabled = true; btn.textContent = 'Loading environment…'; }
  m.ready.then(() => { if (btn) { btn.disabled = false; btn.textContent = btn.dataset.enter || 'Enter'; } }).catch(e => say('Environment failed to load: ' + (e?.message || e)));
  btn?.addEventListener('click', () => {
    say('');
    if (document.immersiveElement) { document.exitImmersive().catch(e => say('Exit failed: ' + e.message)); return; }
    start(); m.requestImmersive().catch(e => { stop(); say('Enter failed: ' + e.message); });
  });
  m.onimmersivechange = () => { const on = !!document.immersiveElement; if (btn) btn.textContent = on ? (btn.dataset.exit || 'Exit') : (btn.dataset.enter || 'Enter'); if (!on) stop(); };
  m.onimmersiveerror = e => { stop(); say('Immersive error: ' + (e?.message || '')); };
}
