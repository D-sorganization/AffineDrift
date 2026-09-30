/** Bind the checked SO(3) engine to the article. Failed edits retain labeled prior results. */
(function () {
  'use strict';
  const RC = window.RotationConverter;
  const byId = id => document.getElementById(id);
  const cells = selector => Array.from(document.querySelectorAll(selector));
  const selectors = {R:'.rc-matrix-cell',quaternion:'.rc-q-cell',eulerZYX:'.rc-euler-cell',
    axisAngle:'.rc-aa-cell',expCoord:'.rc-exp-cell'};
  const panels = {R:'R',quaternion:'q',eulerZYX:'euler',axisAngle:'aa',expCoord:'exp'};
  let degrees = true, active = 'eulerZYX', current = null;
  const format = value => Number(value.toPrecision(12)).toString();
  const angleText = value => format(degrees ? RC.rad2deg(value) : value);
  const angleInput = value => degrees ? RC.deg2rad(value) : value;

  /** Accept a complete finite decimal or scientific-notation number, never a prefix. */
  function readCell(cell) {
    const text = cell.value.trim();
    const valid = /^[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?$/.test(text)
      && Number.isFinite(Number(text));
    cell.classList.toggle('rc-input-invalid',!valid);
    cell.setAttribute('aria-invalid',String(!valid));
    if (!valid) throw new Error('Enter a complete finite decimal number in every field');
    return Number(text);
  }

  function readInput() {
    const fields = cells(selectors[active]);
    const values = fields.map(readCell);
    if (active === 'eulerZYX') {
      const [psi,theta,phi] = values.map(angleInput);
      return {psi,theta,phi};
    }
    if (active === 'axisAngle') return {axis:values.slice(0,3),angle:angleInput(values[3])};
    return values;
  }

  function status(message, valid) {
    const element = byId('rc-status');
    element.hidden = false;
    element.style.display = 'block';
    element.dataset.valid = String(valid);
    element.textContent = message;
    byId('rc-app').dataset.valid = String(valid);
  }

  function writeValues(rep, result) {
    const arrays = {R:result.R,quaternion:result.quaternion,
      eulerZYX:[result.eulerZYX.psi,result.eulerZYX.theta,result.eulerZYX.phi],
      axisAngle:[...result.axisAngle.axis,result.axisAngle.angle],expCoord:result.expCoord};
    cells(selectors[rep]).forEach((cell,index) => {
      const angular = rep === 'eulerZYX' || (rep === 'axisAngle' && index === 3);
      cell.value = angular ? angleText(arrays[rep][index]) : format(arrays[rep][index]);
      cell.classList.remove('rc-input-invalid');
      cell.setAttribute('aria-invalid','false');
    });
  }

  function properties(result) {
    const {R,axisAngle,eulerZYX} = result;
    const {axis,angle} = axisAngle;
    const check = RC.validateR(R);
    const det = R[0]*(R[4]*R[8]-R[5]*R[7])-R[1]*(R[3]*R[8]-R[5]*R[6])
      +R[2]*(R[3]*R[7]-R[4]*R[6]);
    const units = degrees ? '°' : 'rad';
    byId('rc-prop-angle').textContent = `${angleText(angle)} ${units}`;
    byId('rc-prop-axis').textContent = angle === 0 ? '(identity — axis undefined)'
      : `[${axis.map(format).join(', ')}]`;
    byId('rc-prop-det').textContent = format(det);
    byId('rc-prop-orth').textContent = check.orthogError.toExponential(2);
    byId('rc-prop-qnorm').textContent = format(Math.hypot(...result.quaternion));
    byId('rc-R-validity').textContent = `Within tolerance: |det R − 1|=${check.detError.toExponential(2)}, max entry residual=${check.orthogError.toExponential(2)}`;
    byId('rc-q-validity').textContent = 'A finite nonzero input is normalized; output quaternion norm is 1.';
    byId('rc-aa-validity').textContent = angle === 0 ? 'Identity: axis undefined.'
      : 'A finite nonzero input axis is normalized. Principal output angle is 0–π.';
    byId('rc-exp-validity').textContent = `Components always in radians; norm=${format(RC.norm3(result.expCoord))} rad.`;
    byId('rc-row-gimbal').style.display = eulerZYX.gimbalLock ? 'table-row' : 'none';
    const warning = 'Numerical ZYX gimbal lock: |cos(pitch)| < 10⁻¹². Output roll is 0; physical orientation remains defined.';
    byId('rc-euler-validity').textContent = eulerZYX.gimbalLock ? warning : '';
    byId('rc-prop-gimbal').textContent = warning;
  }

  /** Show formulas that remain meaningful in the actual selected branch. */
  function formulas(result) {
    const {axisAngle:aa,quaternion:q,eulerZYX:e,expCoord:rho} = result;
    const lines = [`Source: ${active}; active rotation of column vectors.`,
      'R = Rz(yaw) Ry(pitch) Rx(roll); Hamilton quaternion [w,x,y,z].',
      'Rodrigues: R = I + sin(θ)[n]× + 2 sin²(θ/2)[n]×².',
      'R → q: select the largest squared quaternion component; recover the others using a denominator ≥ 2 for exact R.',
      `Normalized q = [${q.map(format).join(', ')}]; choose w ≥ 0.`,
      'θ = 2 atan2(‖q_vector‖, w); n = q_vector/‖q_vector‖ when nonzero.',
      `Principal θ = ${angleText(aa.angle)} ${degrees ? '°' : 'rad'}.`];
    if (aa.angle === 0) lines.push('Identity: axis is undefined; displayed z axis is a convention.');
    else if (Math.abs(aa.angle-Math.PI) < 1e-10) lines.push('At π the axis sign is ambiguous; no division by sin(π) is used.');
    if (e.gimbalLock) lines.push('At numerical gimbal lock: roll=0, yaw=atan2(−R12,R22).');
    else lines.push('yaw=atan2(R21,R11); roll=atan2(R32,R33).');
    lines.push('pitch=atan2(−R31,hypot(R11,R21)).',
      `yaw, pitch, roll = [${[e.psi,e.theta,e.phi].map(angleText).join(', ')}] ${degrees?'degrees':'radians'}.`,
      `Rotation vector ρ = θ n = [${rho.map(format).join(', ')}] rad.`,
      'ρ is not angular velocity. Single orientations do not recover a time history.');
    byId('rc-formula-text').textContent = lines.join('\n');
  }

  function display(result, preserveActive = true) {
    Object.keys(selectors).forEach(rep => {
      if (!preserveActive || rep !== active) writeValues(rep,result);
      byId(`rc-panel-${panels[rep]}`).classList.toggle('rc-panel-active',rep === active);
    });
    properties(result);
    formulas(result);
    window.RotationConverterViz?.update(result,degrees);
  }

  function update() {
    try {
      const result = RC.convert(readInput(),active);
      current = result;
      display(result);
      status('Current conversion valid within the stated numerical tolerances. Axis and quaternion inputs are normalized.',true);
      return true;
    } catch (error) {
      status(`${error.message}. Other panels and the visualization show the last valid result.`,false);
      return false;
    }
  }

  function changeUnits(radio) {
    degrees = radio.value === 'deg';
    const units = degrees ? '°' : 'rad';
    cells('.rc-aa-angle-lbl').forEach(element => { element.textContent = `θ (${units})`; });
    ['psi','theta','phi'].forEach(name => {
      const label = byId(`rc-lbl-${name}`);
      label.textContent = label.textContent.replace(/\(°\)|\(rad\)/,`(${units})`);
    });
    if (current) {
      display(current,false);
      status('Showing the last valid rotation in the selected units; rotation-vector components remain radians.',true);
    }
  }

  const PRESETS = {
    identity:{axis:[0,0,1],angle:0},rx90:{axis:[1,0,0],angle:Math.PI/2},
    ry90:{axis:[0,1,0],angle:Math.PI/2},rz90:{axis:[0,0,1],angle:Math.PI/2},
    rz180:{axis:[0,0,1],angle:Math.PI},arbitrary:{axis:[1,1,1],angle:47.3*Math.PI/180}
  };

  function preset(name) {
    active = name === 'gimbal' ? 'eulerZYX' : 'axisAngle';
    current = name === 'gimbal' ? RC.convert({psi:0,theta:Math.PI/2,phi:0},active)
      : RC.convert(PRESETS[name],active);
    display(current,false);
    status('Preset loaded. The geometry and formulas describe this rotation.',true);
  }

  function boot() {
    if (!byId('rc-app') || byId('rc-app').dataset.ready) return;
    byId('rc-app').dataset.ready = 'true';
    window.RotationConverterViz?.init();
    Object.entries(selectors).forEach(([rep,selector]) => cells(selector).forEach(cell => {
      cell.addEventListener('input',() => { active = rep; update(); });
    }));
    cells('.rc-load-btn').forEach(button => button.addEventListener('click',() => {
      active = button.dataset.rep;
      update();
    }));
    cells('.rc-preset-btn').forEach(button => button.addEventListener('click',() => preset(button.dataset.preset)));
    cells('input[name="rc-units"]').forEach(radio => radio.addEventListener('change',() => changeUnits(radio)));
    update();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded',boot);
  else boot();
})();
