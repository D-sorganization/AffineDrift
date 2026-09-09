/** Optional 3-D orientation illustration; it does not locate an anatomical axis line. */
(function () {
  'use strict';
  const $ = id => document.getElementById(id);
  const RC = window.RotationConverter;
  let angleDeg = true;
  function disposeObject(object) {
    object?.traverse(child => {
      child.geometry?.dispose();
      child.material?.dispose();
    });
  }
  let vizScene, vizCamera, vizRenderer, vizControls;
  let vizAxisArrow, vizArcLine, vizFrame0, vizFrameR;
  const VIZ_SCREW_LEN  = 1.4;
  const VIZ_FRAME_LEN  = 0.7;
  const VIZ_ARC_SEGS   = 64;

  function initViz() {
    const canvas = $("rc-canvas");
    if (!window.THREE) {
      $("rc-webgl-fallback").style.display = "block";
      canvas.style.display = "none";
      return;
    }
    const THREE = window.THREE;

    vizRenderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false });
    vizRenderer.setPixelRatio(window.devicePixelRatio);
    vizRenderer.setClearColor(0x0a0a14, 1);

    vizScene = new THREE.Scene();
    vizScene.add(new THREE.AmbientLight(0xffffff, 0.6));
    const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
    dirLight.position.set(3, 5, 3);
    vizScene.add(dirLight);

    const w = canvas.clientWidth, h = canvas.clientHeight || 450;
    vizCamera = new THREE.PerspectiveCamera(40, w / h, 0.01, 100);
    vizCamera.position.set(2.2, 1.8, 2.2);
    vizCamera.lookAt(0, 0, 0);

    if (window.THREE.OrbitControls) {
      vizControls = new THREE.OrbitControls(vizCamera, vizRenderer.domElement);
      vizControls.enableDamping = true;
      vizControls.dampingFactor = 0.08;
      vizControls.target.set(0, 0, 0);
    }

  }

  function addSceneObjects() {
    const THREE = window.THREE;
    const canvas = $("rc-canvas");
    const grid = new THREE.GridHelper(4, 8, 0x222233, 0x1a1a2e);
    vizScene.add(grid);
    vizFrame0 = makeCoordFrame(VIZ_FRAME_LEN, [0xff4444, 0x44ff44, 0x4488ff], 3);
    vizScene.add(vizFrame0);
    addAxisLabel("X", [VIZ_FRAME_LEN + 0.12, 0, 0], 0xff4444);
    addAxisLabel("Y", [0, VIZ_FRAME_LEN + 0.12, 0], 0x44ff44);
    addAxisLabel("Z", [0, 0, VIZ_FRAME_LEN + 0.12], 0x4488ff);
    vizFrameR = makeCoordFrame(VIZ_FRAME_LEN, [0xff8888, 0x88ff88, 0x88aaff], 2);
    vizScene.add(vizFrameR);
    vizAxisArrow = makeArrow([0,0,0], [0,1,0]);
    vizScene.add(vizAxisArrow);
    vizArcLine = makeArc([0,0,1], 0, 0.5, VIZ_ARC_SEGS);
    vizScene.add(vizArcLine);
    const dotGeo = new THREE.SphereGeometry(0.03, 12, 8);
    const dotMat = new THREE.MeshPhongMaterial({ color: 0xffffff });
    vizScene.add(new THREE.Mesh(dotGeo, dotMat));
    new ResizeObserver(() => resizeViz()).observe(canvas);

    requestAnimationFrame(animateViz);
  }

  function resizeViz() {
    const canvas = $("rc-canvas");
    if (!vizRenderer || !canvas) return;
    const w = canvas.clientWidth, h = canvas.clientHeight || 450;
    vizRenderer.setSize(w, h, false);
    vizCamera.aspect = w / h;
    vizCamera.updateProjectionMatrix();
  }

  function animateViz() {
    requestAnimationFrame(animateViz);
    if (vizControls) vizControls.update();
    if (vizRenderer) vizRenderer.render(vizScene, vizCamera);
  }

  function updateViz(result, degrees) {
    angleDeg = degrees;
    if (!vizScene || !window.THREE) return;
    const { R, axisAngle } = result;
    const { axis, angle } = axisAngle;

    updateCoordFrame(vizFrameR, R);

    disposeObject(vizAxisArrow);
    vizScene.remove(vizAxisArrow);
    const axisDir = angle === 0 ? [0,1,0] : axis;
    vizAxisArrow = makeArrow(
      axisDir.map(v => -v * VIZ_SCREW_LEN * 0.5),  // center the arrow at origin
      axisDir
    );
    vizAxisArrow.visible = angle !== 0;
    vizScene.add(vizAxisArrow);

    disposeObject(vizArcLine);
    vizScene.remove(vizArcLine);
    if (Math.abs(angle) > 1e-4) {
      vizArcLine = makeArc(axisDir, angle, VIZ_FRAME_LEN * 0.85, VIZ_ARC_SEGS);
      vizScene.add(vizArcLine);
    }

    const th = angleDeg ? RC.rad2deg(angle).toFixed(2) + "°" : angle.toFixed(4) + " rad";
    $("rc-viz-info").textContent = angle === 0
      ? "Identity: no unique rotation axis"
      : `n̂ = [${axis.map(v=>v.toFixed(3)).join(", ")}]   θ = ${th}`;
  }

  function makeCoordFrame(length, colors, lineW) {
    const THREE = window.THREE;
    const group = new THREE.Group();
    const dirs = [[1,0,0],[0,1,0],[0,0,1]];
    dirs.forEach((d, i) => {
      const mat = new THREE.LineBasicMaterial({ color: colors[i], linewidth: lineW });
      const pts = [new THREE.Vector3(0,0,0), new THREE.Vector3(...d.map(v=>v*length))];
      const geo = new THREE.BufferGeometry().setFromPoints(pts);
      group.add(new THREE.Line(geo, mat));
      const coneH = length * 0.14, coneR = length * 0.04;
      const coneGeo = new THREE.ConeGeometry(coneR, coneH, 8);
      const coneMat = new THREE.MeshPhongMaterial({ color: colors[i] });
      const cone = new THREE.Mesh(coneGeo, coneMat);
      cone.position.set(...d.map(v=>v*(length + coneH/2)));
      cone.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0), new THREE.Vector3(...d));
      group.add(cone);
    });
    return group;
  }

  function makeArrow(origin, dir) {
    const length = VIZ_SCREW_LEN, color = 0xfbbf24, shaftR = 0.018, headR = 0.07;
    const THREE = window.THREE;
    const group = new THREE.Group();
    const d = new THREE.Vector3(...dir).normalize();
    const o = new THREE.Vector3(...origin);
    const shaftH = length * 0.82;
    const shaftGeo = new THREE.CylinderGeometry(shaftR, shaftR, shaftH, 12);
    const shaftMat = new THREE.MeshPhongMaterial({ color });
    const shaft = new THREE.Mesh(shaftGeo, shaftMat);
    shaft.position.copy(o).addScaledVector(d, shaftH / 2);
    shaft.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0), d);
    group.add(shaft);
    const headH = length * 0.18;
    const headGeo = new THREE.ConeGeometry(headR, headH, 12);
    const headMat = new THREE.MeshPhongMaterial({ color });
    const head = new THREE.Mesh(headGeo, headMat);
    head.position.copy(o).addScaledVector(d, shaftH + headH / 2);
    head.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0), d);
    group.add(head);

    return group;
  }

  function makeArc(axis, angle, radius, segments) {
    const THREE = window.THREE;
    const n = new THREE.Vector3(...axis).normalize();
    const ref = Math.abs(n.x) < 0.9 ? new THREE.Vector3(1,0,0) : new THREE.Vector3(0,1,0);
    const u = ref.clone().sub(n.clone().multiplyScalar(n.dot(ref))).normalize();
    const v = n.clone().cross(u);

    const pts = [];
    const steps = Math.max(4, Math.ceil(Math.abs(angle) / (2*Math.PI) * segments));
    for (let i = 0; i <= steps; i++) {
      const t = (i / steps) * angle;
      const p = u.clone().multiplyScalar(Math.cos(t) * radius)
                 .addScaledVector(v, Math.sin(t) * radius);
      pts.push(p);
    }
    const geo = new THREE.BufferGeometry().setFromPoints(pts);
    const mat = new THREE.LineBasicMaterial({ color: 0xfbbf24, linewidth: 2 });
    return new THREE.Line(geo, mat);
  }

  function updateCoordFrame(group, R) {
    const THREE = window.THREE;
    const dirs = [
      [R[0], R[3], R[6]],  // image of ex  (column 0 of R)
      [R[1], R[4], R[7]],  // image of ey
      [R[2], R[5], R[8]],  // image of ez
    ];
    const L = VIZ_FRAME_LEN;
    group.children.forEach((child, ci) => {
      const axIdx = Math.floor(ci / 2);
      const isLine = ci % 2 === 0;
      const d = new THREE.Vector3(...dirs[axIdx]);
      if (isLine) {
        const pos = child.geometry.attributes.position;
        pos.setXYZ(1, d.x*L, d.y*L, d.z*L);
        pos.needsUpdate = true;
      } else {
        const coneH = L * 0.14;
        child.position.set(...d.toArray().map(v=>v*(L + coneH/2)));
        child.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0), d);
      }
    });
  }

  function addAxisLabel(text, pos, color) {
    if (!window.THREE) return;
    const THREE = window.THREE;
    const canvas = document.createElement("canvas");
    canvas.width = 64; canvas.height = 64;
    const ctx = canvas.getContext("2d");
    ctx.fillStyle = "#" + color.toString(16).padStart(6,"0");
    ctx.font = "bold 48px sans-serif";
    ctx.textAlign = "center"; ctx.textBaseline = "middle";
    ctx.fillText(text, 32, 32);
    const tex = new THREE.CanvasTexture(canvas);
    const mat = new THREE.SpriteMaterial({ map: tex, transparent: true });
    const sprite = new THREE.Sprite(mat);
    sprite.position.set(...pos);
    sprite.scale.set(0.22, 0.22, 1);
    vizScene.add(sprite);
  }


  function init() {
    try {
      initViz();
      if (vizScene) { addSceneObjects(); resizeViz(); }
    } catch (error) {
      vizScene = null;
      $("rc-webgl-fallback").style.display = "block";
      $("rc-canvas").style.display = "none";
      $("rc-webgl-fallback").textContent = "3-D view unavailable; all numerical conversions remain available.";
    }
  }
  window.RotationConverterViz = {init, update: updateViz};
})();
