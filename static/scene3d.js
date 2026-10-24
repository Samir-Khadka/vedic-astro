"use strict";
/* Vedic Astro — cinematic 3D hero scene (Three.js).
 * A slowly rotating zodiac ring / armillary with glyph sprites, a glowing
 * central sun, orbiting planets, a deep star particle field and nebula
 * glow sprites, with lerped mouse parallax.
 *
 * Fail-safe by design: if Three.js failed to load, WebGL is unavailable,
 * or the context is lost, the mount is removed and the page keeps the
 * existing SVG hero ring + 2D canvas starfield untouched.
 * Respects prefers-reduced-motion (single static frame), pauses when the
 * tab is hidden or the hero scrolls off-screen. */
(function heroScene3D() {
  const mount = document.getElementById("hero-3d");
  const hero = document.getElementById("hero");
  if (!mount || !hero) return;
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function teardown() {
    try { mount.remove(); } catch (e) { /* already gone */ }
    document.body.classList.remove("webgl-on");
  }

  if (!window.THREE) { teardown(); return; }

  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({
      antialias: true, alpha: true, powerPreference: "low-power",
    });
  } catch (e) { teardown(); return; }
  renderer.domElement.addEventListener("webglcontextlost", (ev) => {
    ev.preventDefault(); teardown();
  });

  const GLYPHS = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"];
  const GOLD = 0xe5c15c, GOLD_HI = 0xf2d584, VIOLET = 0x8a7fe0, DEEP = 0x4a3f9e;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 100);
  camera.position.set(0, 0.4, 9.2);

  const rig = new THREE.Group();          // parallax group
  scene.add(rig);
  const wheel = new THREE.Group();        // zodiac ring + glyphs
  rig.add(wheel);

  /* ---- textures (canvas-generated, no external assets) ---- */
  function glowTexture(inner, outer) {
    const c = document.createElement("canvas"); c.width = c.height = 256;
    const g = c.getContext("2d");
    const grad = g.createRadialGradient(128, 128, 0, 128, 128, 128);
    grad.addColorStop(0, inner); grad.addColorStop(1, outer);
    g.fillStyle = grad; g.fillRect(0, 0, 256, 256);
    return new THREE.CanvasTexture(c);
  }
  function glyphTexture(glyph) {
    const c = document.createElement("canvas"); c.width = c.height = 160;
    const g = c.getContext("2d");
    g.font = "104px 'Segoe UI Symbol','Noto Sans Symbols 2','Noto Sans',serif";
    g.textAlign = "center"; g.textBaseline = "middle";
    g.shadowColor = "rgba(242,213,132,0.95)"; g.shadowBlur = 22;
    g.fillStyle = "#f5dfa0";
    g.fillText(glyph, 80, 86); g.fillText(glyph, 80, 86);
    return new THREE.CanvasTexture(c);
  }

  /* ---- nebula glow sprites (behind everything) ---- */
  const nebTexViolet = glowTexture("rgba(110,90,220,0.85)", "rgba(110,90,220,0)");
  const nebTexGold = glowTexture("rgba(229,193,92,0.7)", "rgba(229,193,92,0)");
  const nebTexIndigo = glowTexture("rgba(52,44,140,0.9)", "rgba(52,44,140,0)");
  [
    [nebTexViolet, -5.6, 2.4, -4.5, 13, 0.16],
    [nebTexIndigo, 5.8, -2.2, -5.5, 15, 0.20],
    [nebTexGold, 3.4, 3.4, -6.5, 10, 0.08],
  ].forEach(([tex, x, y, z, s, op]) => {
    const m = new THREE.SpriteMaterial({
      map: tex, transparent: true, opacity: op,
      blending: THREE.AdditiveBlending, depthWrite: false,
    });
    const sp = new THREE.Sprite(m);
    sp.position.set(x, y, z); sp.scale.set(s, s, 1);
    scene.add(sp);
  });

  /* ---- star particle field with depth ---- */
  const isNarrow = Math.min(window.innerWidth, 1200) < 640;
  const starCount = isNarrow ? 420 : 900;
  const pos = new Float32Array(starCount * 3);
  const col = new Float32Array(starCount * 3);
  const palette = [
    new THREE.Color(0xfff6dd), new THREE.Color(0xe9e2ff),
    new THREE.Color(0xf2d584), new THREE.Color(0xb9aef0),
  ];
  for (let i = 0; i < starCount; i++) {
    pos[i * 3] = (Math.random() - 0.5) * 34;
    pos[i * 3 + 1] = (Math.random() - 0.5) * 20;
    pos[i * 3 + 2] = -2 - Math.random() * 9;
    const c = palette[(Math.random() * palette.length) | 0];
    col[i * 3] = c.r; col[i * 3 + 1] = c.g; col[i * 3 + 2] = c.b;
  }
  const starGeo = new THREE.BufferGeometry();
  starGeo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
  starGeo.setAttribute("color", new THREE.BufferAttribute(col, 3));
  const starMat = new THREE.PointsMaterial({
    size: 0.055, vertexColors: true, transparent: true, opacity: 0.9,
    blending: THREE.AdditiveBlending, depthWrite: false, sizeAttenuation: true,
  });
  const stars = new THREE.Points(starGeo, starMat);
  scene.add(stars);

  /* ---- zodiac wheel: rings + glyph sprites ---- */
  function ring(radius, tube, color, opacity) {
    const mesh = new THREE.Mesh(
      new THREE.TorusGeometry(radius, tube, 12, 180),
      new THREE.MeshBasicMaterial({ color, transparent: true, opacity })
    );
    return mesh;
  }
  wheel.add(ring(3.15, 0.014, GOLD, 0.95));
  wheel.add(ring(2.62, 0.008, VIOLET, 0.55));
  wheel.add(ring(3.68, 0.006, GOLD, 0.35));
  // tick marks between the signs
  const tickGeo = new THREE.BufferGeometry();
  const tickPos = [];
  for (let i = 0; i < 72; i++) {
    const a = (i / 72) * Math.PI * 2;
    const r1 = 3.02, r2 = i % 6 === 0 ? 2.86 : 2.94;
    tickPos.push(Math.cos(a) * r1, Math.sin(a) * r1, 0, Math.cos(a) * r2, Math.sin(a) * r2, 0);
  }
  tickGeo.setAttribute("position", new THREE.BufferAttribute(new Float32Array(tickPos), 3));
  wheel.add(new THREE.LineSegments(tickGeo,
    new THREE.LineBasicMaterial({ color: GOLD, transparent: true, opacity: 0.4 })));

  GLYPHS.forEach((glyph, i) => {
    const a = ((i * 30 + 90) * Math.PI) / 180; // Aries at top, wheel turns CCW visually
    const sp = new THREE.Sprite(new THREE.SpriteMaterial({
      map: glyphTexture(glyph), transparent: true, depthWrite: false,
    }));
    sp.position.set(Math.cos(a) * 3.15, Math.sin(a) * 3.15, 0);
    sp.scale.set(0.62, 0.62, 1);
    wheel.add(sp);
  });

  /* ---- armillary rings (tilted, independent slow axes) ---- */
  const armillary = new THREE.Group();
  const arm1 = ring(3.42, 0.009, GOLD_HI, 0.5);
  arm1.rotation.x = Math.PI / 2.6;
  const arm2 = ring(3.42, 0.009, VIOLET, 0.4);
  arm2.rotation.y = Math.PI / 2.4; arm2.rotation.x = 0.5;
  const arm3 = ring(2.2, 0.007, GOLD, 0.35);
  arm3.rotation.x = Math.PI / 3; arm3.rotation.y = 0.8;
  armillary.add(arm1, arm2, arm3);
  rig.add(armillary);

  /* ---- central sun ---- */
  const sun = new THREE.Mesh(
    new THREE.SphereGeometry(0.52, 40, 40),
    new THREE.MeshBasicMaterial({ color: 0xf7dd8f })
  );
  rig.add(sun);
  const sunGlowTex = glowTexture("rgba(255,224,150,0.95)", "rgba(255,224,150,0)");
  [[2.6, 0.85], [4.6, 0.4]].forEach(([s, op]) => {
    const sp = new THREE.Sprite(new THREE.SpriteMaterial({
      map: sunGlowTex, transparent: true, opacity: op,
      blending: THREE.AdditiveBlending, depthWrite: false,
    }));
    sp.scale.set(s, s, 1);
    rig.add(sp);
  });

  /* ---- orbiting planets on the inner ring ---- */
  const orbiters = [];
  [
    [2.62, 0.075, 0xfff3d6, 0.16], [2.62, 0.06, 0xd9a05a, 0.11],
    [2.62, 0.055, 0xb9aef0, 0.07], [2.62, 0.05, 0x9fd8e8, 0.05],
  ].forEach(([r, size, color, speed], i) => {
    const m = new THREE.Mesh(
      new THREE.SphereGeometry(size, 20, 20),
      new THREE.MeshBasicMaterial({ color })
    );
    m.userData = { r, speed, phase: i * 1.9 };
    rig.add(m); orbiters.push(m);
  });

  /* ---- mount + sizing ---- */
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, isNarrow ? 1.5 : 1.75));
  renderer.domElement.className = "hero-3d-canvas";
  mount.appendChild(renderer.domElement);

  function resize() {
    const w = mount.clientWidth || hero.clientWidth || 1;
    const h = mount.clientHeight || hero.clientHeight || 1;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  }
  resize();

  /* ---- interaction: lerped mouse parallax ---- */
  let tx = 0, ty = 0, mx = 0, my = 0;
  if (!reduced && window.matchMedia("(hover: hover) and (pointer: fine)").matches) {
    window.addEventListener("pointermove", (ev) => {
      tx = (ev.clientX / window.innerWidth - 0.5) * 2;
      ty = (ev.clientY / window.innerHeight - 0.5) * 2;
    }, { passive: true });
  }

  /* ---- run / pause control ---- */
  let heroVisible = true;
  if ("IntersectionObserver" in window) {
    new IntersectionObserver((entries) => {
      heroVisible = entries[0].isIntersecting;
    }, { threshold: 0.02 }).observe(hero);
  }
  let resizeTimer = null;
  window.addEventListener("resize", () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(resize, 140);
  });

  const clock = new THREE.Clock();
  let firstFrame = true;
  function frame() {
    const dt = Math.min(clock.getDelta(), 0.05);
    const t = clock.elapsedTime;
    wheel.rotation.z = t * 0.045;
    arm1.rotation.z = t * 0.06;
    arm2.rotation.z = -t * 0.045;
    arm3.rotation.z = t * 0.09;
    stars.rotation.z = t * 0.004;
    starMat.opacity = 0.82 + 0.14 * Math.sin(t * 0.7);
    sun.scale.setScalar(1 + 0.025 * Math.sin(t * 1.4));
    orbiters.forEach((m) => {
      const a = m.userData.phase + t * m.userData.speed;
      m.position.set(Math.cos(a) * m.userData.r, Math.sin(a) * m.userData.r, 0.05);
    });
    mx += (tx - mx) * 0.045;
    my += (ty - my) * 0.045;
    rig.rotation.y = mx * 0.22;
    rig.rotation.x = my * 0.14;
    camera.position.x = mx * 0.35;
    camera.lookAt(0, 0, 0);
    renderer.render(scene, camera);
    if (firstFrame) {
      firstFrame = false;
      document.body.classList.add("webgl-on");
    }
    void dt;
  }

  if (reduced) {
    frame(); // one static composed frame, no loop
    return;
  }
  (function loop() {
    requestAnimationFrame(loop);
    if (!heroVisible || document.hidden) return;
    frame();
  })();
})();
