/**
 * rotation-converter.js
 *
 * Pure-function rotation math module. All representations are stored as plain
 * JS values (flat arrays, numbers) — no classes, no mutable state.
 *
 * Representations supported:
 *   R   — 3×3 rotation matrix stored row-major as a 9-element Float64Array
 *          (or regular Array). Indexed R[row*3 + col].
 *   q   — unit quaternion [w, x, y, z]
 *   aa  — axis-angle {axis: [nx, ny, nz], angle: θ}  (axis is unit vector)
 *   exp — exponential coordinates ω = θ·n̂ ∈ ℝ³  (same as compact axis-angle)
 *   zyx — ZYX Euler angles {psi: ψ, theta: θ, phi: φ} in radians
 *          Composition order: R = Rz(ψ) Ry(θ) Rx(φ)
 *
 * All angles in radians unless the function name says Deg.
 *
 * Design by Contract:
 *   Every public function asserts its preconditions and throws a descriptive
 *   Error on violation. Postconditions are checked in the _validate* helpers.
 *
 * Reference: Park & Lynch, Modern Robotics, 2017, Chapters 3–4.
 */

"use strict";

/* ─── Tolerance constants ─────────────────────────────────────────────────── */

/** Maximum acceptable deviation from unit length. */
const UNIT_TOL = 1e-6;

/** Maximum acceptable det(R) - 1 or max|RᵀR - I| entry. */
const ORTHOG_TOL = 1e-5;

/** Angle below which the axis is treated as undefined (identity rotation). */
const ANGLE_ZERO = 1e-10;

/* ─── Contract assertion ──────────────────────────────────────────────────── */

/**
 * Assert a boolean condition; throw with a descriptive message on failure.
 * @param {boolean} condition
 * @param {string}  message
 */
function assert(condition, message) {
  if (!condition) throw new Error(`[rotation-converter] Contract violation: ${message}`);
}

/* ─── Low-level helpers ───────────────────────────────────────────────────── */

/**
 * Clamp x to [lo, hi].
 * @param {number} x
 * @param {number} lo
 * @param {number} hi
 * @returns {number}
 */
function clamp(x, lo, hi) { return x < lo ? lo : x > hi ? hi : x; }

/**
 * Euclidean norm of a 3-vector.
 * @param {number[]} v  — length-3 array
 * @returns {number}
 */
function norm3(v) { return Math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2]); }

/**
 * Dot product of two 3-vectors.
 * @param {number[]} a
 * @param {number[]} b
 * @returns {number}
 */
function dot3(a, b) { return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]; }

/**
 * Skew-symmetric (cross-product) matrix [v]× from a 3-vector.
 *
 *   [v]× = ⎡  0   -v₂   v₁ ⎤
 *           ⎢  v₂   0   -v₀ ⎥
 *           ⎣ -v₁   v₀   0  ⎦
 *
 * Precondition: v is a length-3 array of finite numbers.
 * @param {number[]} v
 * @returns {number[]}  row-major 9-element array
 */
function skew(v) {
  assert(Array.isArray(v) && v.length === 3, `skew: expected length-3 array, got ${v}`);
  assert(isFinite(v[0]) && isFinite(v[1]) && isFinite(v[2]), "skew: components must be finite");
  return [
     0,    -v[2],  v[1],
     v[2],  0,    -v[0],
    -v[1],  v[0],  0
  ];
}

/**
 * Multiply two 3×3 matrices (row-major flat arrays).
 * @param {number[]} A
 * @param {number[]} B
 * @returns {number[]}
 */
function matMul33(A, B) {
  const C = new Array(9);
  for (let r = 0; r < 3; r++) {
    for (let c = 0; c < 3; c++) {
      C[r*3+c] = A[r*3+0]*B[0*3+c] + A[r*3+1]*B[1*3+c] + A[r*3+2]*B[2*3+c];
    }
  }
  return C;
}

/**
 * Transpose a 3×3 matrix (row-major flat array).
 * @param {number[]} M
 * @returns {number[]}
 */
function transpose33(M) {
  return [
    M[0], M[3], M[6],
    M[1], M[4], M[7],
    M[2], M[5], M[8]
  ];
}

/**
 * Add two 3×3 matrices element-wise.
 * @param {number[]} A
 * @param {number[]} B
 * @returns {number[]}
 */
function matAdd33(A, B) { return A.map((a, i) => a + B[i]); }

/**
 * Scale a 3×3 matrix by a scalar.
 * @param {number}   s
 * @param {number[]} M
 * @returns {number[]}
 */
function matScale33(s, M) { return M.map(m => s * m); }

/* ─── Validation / postcondition checks ──────────────────────────────────── */

/**
 * Validate a 3×3 rotation matrix.
 * Checks: RᵀR ≈ I  and  det(R) ≈ +1.
 *
 * @param {number[]} R — row-major 9-element array
 * @returns {{ valid: boolean, detError: number, orthogError: number }}
 */
function validateR(R) {
  assert(R.length === 9, `validateR: expected length-9 array, got ${R.length}`);
  const Rt = transpose33(R);
  const RtR = matMul33(Rt, R);
  // Identity matrix
  const I9 = [1,0,0, 0,1,0, 0,0,1];
  const orthogError = Math.max(...RtR.map((v, i) => Math.abs(v - I9[i])));
  // det(R) via Sarrus' rule
  const det = R[0]*(R[4]*R[8]-R[5]*R[7]) - R[1]*(R[3]*R[8]-R[5]*R[6]) + R[2]*(R[3]*R[7]-R[4]*R[6]);
  const detError = Math.abs(det - 1);
  return {
    valid: orthogError < ORTHOG_TOL && detError < ORTHOG_TOL,
    detError,
    orthogError
  };
}

/**
 * Validate a quaternion [w, x, y, z].
 * @param {number[]} q
 * @returns {{ valid: boolean, normError: number }}
 */
function validateQuaternion(q) {
  assert(q.length === 4, `validateQuaternion: expected length-4 array, got ${q.length}`);
  const n = Math.sqrt(q[0]*q[0] + q[1]*q[1] + q[2]*q[2] + q[3]*q[3]);
  return { valid: Math.abs(n - 1) < UNIT_TOL, normError: Math.abs(n - 1) };
}

/* ─── Conversion: Axis-angle → Rotation matrix ───────────────────────────── */

/**
 * Convert axis-angle to rotation matrix using the Rodrigues formula:
 *
 *   R = I + sin(θ)·[n̂]× + (1−cos(θ))·[n̂]×²
 *
 * Preconditions:
 *   - axis is a unit 3-vector: |axis| ≈ 1
 *   - angle is a finite real number
 *
 * Postcondition: returned R satisfies det(R) ≈ 1 and RᵀR ≈ I.
 *
 * @param {number[]} axis   unit rotation axis [nx, ny, nz]
 * @param {number}   angle  rotation angle in radians
 * @returns {number[]}      row-major 9-element rotation matrix
 */
function axisAngleToR(axis, angle) {
  assert(Array.isArray(axis) && axis.length === 3, "axisAngleToR: axis must be length-3 array");
  assert(isFinite(angle), "axisAngleToR: angle must be finite");
  const n = norm3(axis);
  assert(Math.abs(n - 1) < UNIT_TOL, `axisAngleToR: axis must be unit vector (|n| = ${n.toFixed(6)})`);

  if (Math.abs(angle) < ANGLE_ZERO) {
    return [1,0,0, 0,1,0, 0,0,1]; // identity
  }

  const K  = skew(axis);          // [n̂]×
  const K2 = matMul33(K, K);      // [n̂]×²
  const s  = Math.sin(angle);
  const c1 = 1 - Math.cos(angle);

  const I9 = [1,0,0, 0,1,0, 0,0,1];
  const R  = matAdd33(I9, matAdd33(matScale33(s, K), matScale33(c1, K2)));
  return R;
}

/* ─── Conversion: Rotation matrix → Axis-angle ───────────────────────────── */

/**
 * Extract axis and angle from a rotation matrix.
 *
 *   θ = arccos((tr(R) − 1) / 2)
 *   n̂ = 1/(2 sin θ) · [R₃₂−R₂₃, R₁₃−R₃₁, R₂₁−R₁₂]ᵀ
 *
 * Special cases:
 *   - θ ≈ 0: returns axis [0,0,1], angle 0
 *   - θ ≈ π: uses eigenvector extraction (Shepperd method)
 *
 * Precondition: R must be a 3×3 rotation matrix (length-9 row-major array).
 *
 * @param {number[]} R
 * @returns {{ axis: number[], angle: number }}
 */
function rToAxisAngle(R) {
  assert(R.length === 9, "rToAxisAngle: expected length-9 matrix");

  const traceR = R[0] + R[4] + R[8];
  const cosTheta = clamp((traceR - 1) / 2, -1, 1);
  const angle = Math.acos(cosTheta);

  if (Math.abs(angle) < ANGLE_ZERO) {
    return { axis: [0, 0, 1], angle: 0 };
  }

  if (Math.abs(angle - Math.PI) < 1e-7) {
    // 180° case: axis from diagonal of (R + I) / 2
    const Bdiag = [(1 + R[0])/2, (1 + R[4])/2, (1 + R[8])/2];
    const idx = Bdiag.indexOf(Math.max(...Bdiag));
    const axis = [0, 0, 0];
    axis[idx] = Math.sqrt(Math.max(0, Bdiag[idx]));
    // Resolve sign from off-diagonal
    if (idx === 0) {
      axis[1] = (R[1] + R[3]) / (4 * axis[0]);
      axis[2] = (R[2] + R[6]) / (4 * axis[0]);
    } else if (idx === 1) {
      axis[0] = (R[1] + R[3]) / (4 * axis[1]);
      axis[2] = (R[5] + R[7]) / (4 * axis[1]);
    } else {
      axis[0] = (R[2] + R[6]) / (4 * axis[2]);
      axis[1] = (R[5] + R[7]) / (4 * axis[2]);
    }
    const len = norm3(axis);
    return { axis: axis.map(v => v / len), angle: Math.PI };
  }

  const s2 = 2 * Math.sin(angle);
  const axis = [
    (R[7] - R[5]) / s2,   // R[2,1] - R[1,2]
    (R[2] - R[6]) / s2,   // R[0,2] - R[2,0]
    (R[3] - R[1]) / s2    // R[1,0] - R[0,1]
  ];
  return { axis, angle };
}

/* ─── Conversion: Quaternion → Rotation matrix ───────────────────────────── */

/**
 * Convert a unit quaternion q = [w, x, y, z] to a rotation matrix.
 *
 *   R = ⎡ 1−2(y²+z²)   2(xy−wz)   2(xz+wy) ⎤
 *       ⎢  2(xy+wz)   1−2(x²+z²)   2(yz−wx) ⎥
 *       ⎣  2(xz−wy)    2(yz+wx)  1−2(x²+y²) ⎦
 *
 * Precondition: q is unit quaternion — |q| ≈ 1.
 *
 * @param {number[]} q  [w, x, y, z]
 * @returns {number[]}  row-major 9-element rotation matrix
 */
function quaternionToR(q) {
  assert(q.length === 4, "quaternionToR: expected length-4 quaternion");
  const n = Math.sqrt(q[0]*q[0]+q[1]*q[1]+q[2]*q[2]+q[3]*q[3]);
  assert(Math.abs(n - 1) < UNIT_TOL, `quaternionToR: quaternion must be unit (|q| = ${n.toFixed(6)})`);

  // Normalize for numerical safety
  const [w, x, y, z] = q.map(v => v / n);
  return [
    1-2*(y*y+z*z),   2*(x*y-w*z),   2*(x*z+w*y),
      2*(x*y+w*z), 1-2*(x*x+z*z),   2*(y*z-w*x),
      2*(x*z-w*y),   2*(y*z+w*x), 1-2*(x*x+y*y)
  ];
}

/* ─── Conversion: Rotation matrix → Quaternion ───────────────────────────── */

/**
 * Convert a rotation matrix to a unit quaternion [w, x, y, z].
 *
 * General case (w > 0):
 *   w = ½√(1 + tr(R))
 *   x = (R₃₂ − R₂₃) / (4w)
 *   y = (R₁₃ − R₃₁) / (4w)
 *   z = (R₂₁ − R₁₂) / (4w)
 *
 * Degenerate case (θ = 180°, w ≈ 0): Shepperd's method on diagonal.
 *
 * Always returns w ≥ 0 (canonical half of S³).
 *
 * @param {number[]} R  row-major 9-element rotation matrix
 * @returns {number[]}  [w, x, y, z]
 */
function rToQuaternion(R) {
  assert(R.length === 9, "rToQuaternion: expected length-9 matrix");

  const traceR = R[0] + R[4] + R[8];
  const w = 0.5 * Math.sqrt(Math.max(0, 1 + traceR));

  if (w < 1e-10) {
    // 180° rotation: Shepperd's method
    const x = Math.sqrt(Math.max(0, (1 + R[0]) / 2));
    let   y = Math.sqrt(Math.max(0, (1 + R[4]) / 2));
    let   z = Math.sqrt(Math.max(0, (1 + R[8]) / 2));
    // Sign from off-diagonal entries
    if (R[7] - R[5] < 0) {}            // x stays positive (convention)
    if (R[2] - R[6] < 0) y = -y;
    if (R[3] - R[1] < 0) z = -z;
    const len = Math.sqrt(x*x + y*y + z*z);
    return len > 0 ? [0, x/len, y/len, z/len] : [1, 0, 0, 0];
  }

  const inv4w = 1 / (4 * w);
  return [
    w,
    (R[7] - R[5]) * inv4w,   // (R[2,1] - R[1,2]) / 4w
    (R[2] - R[6]) * inv4w,   // (R[0,2] - R[2,0]) / 4w
    (R[3] - R[1]) * inv4w    // (R[1,0] - R[0,1]) / 4w
  ];
}

/* ─── Conversion: ZYX Euler angles → Rotation matrix ─────────────────────── */

/**
 * Convert ZYX Euler angles to rotation matrix.
 *
 *   R = Rz(ψ) Ry(θ) Rx(φ)
 *
 * where (ψ, θ, φ) = (yaw, pitch, roll) in aerospace convention.
 *
 * Precondition: all angles are finite reals; pitch |θ| < π/2 avoids gimbal lock.
 *
 * @param {number} psi    yaw   ψ (about Z)
 * @param {number} theta  pitch θ (about Y)  ← gimbal lock at ±π/2
 * @param {number} phi    roll  φ (about X)
 * @returns {number[]}  row-major 9-element rotation matrix
 */
function eulerZYXToR(psi, theta, phi) {
  assert(isFinite(psi) && isFinite(theta) && isFinite(phi),
    "eulerZYXToR: angles must be finite");

  const cp = Math.cos(psi),   sp = Math.sin(psi);
  const ct = Math.cos(theta), st = Math.sin(theta);
  const cr = Math.cos(phi),   sr = Math.sin(phi);

  // Expanded product Rz·Ry·Rx
  return [
    cp*ct,  cp*st*sr - sp*cr,  cp*st*cr + sp*sr,
    sp*ct,  sp*st*sr + cp*cr,  sp*st*cr - cp*sr,
      -st,          ct*sr,             ct*cr
  ];
}

/* ─── Conversion: Rotation matrix → ZYX Euler angles ─────────────────────── */

/**
 * Extract ZYX Euler angles from a rotation matrix.
 *
 *   ψ = atan2(R₂₁, R₁₁)
 *   θ = −arcsin(R₃₁)         ← undefined at R₃₁ = ±1 (gimbal lock)
 *   φ = atan2(R₃₂, R₃₃)
 *
 * At gimbal lock (θ = ±π/2) ψ and φ are not independently determined;
 * the function returns φ = 0 and encodes all rotation into ψ.
 *
 * @param {number[]} R  row-major 9-element rotation matrix
 * @returns {{ psi: number, theta: number, phi: number, gimbalLock: boolean }}
 */
function rToEulerZYX(R) {
  assert(R.length === 9, "rToEulerZYX: expected length-9 matrix");

  const sinTheta = clamp(-R[6], -1, 1);   // -R[2,0]
  const theta = Math.asin(sinTheta);
  const gimbalLock = Math.abs(Math.abs(sinTheta) - 1) < 1e-7;

  let psi, phi;
  if (gimbalLock) {
    // φ and ψ cannot be independently resolved; set φ=0 by convention
    phi = 0;
    psi = Math.atan2(-R[5], R[4]);         // atan2(-R[1,2], R[1,1])
  } else {
    psi = Math.atan2(R[3], R[0]);           // atan2(R[1,0], R[0,0])
    phi = Math.atan2(R[7], R[8]);           // atan2(R[2,1], R[2,2])
  }

  return { psi, theta, phi, gimbalLock };
}

/* ─── Conversion: Exponential coordinates ↔ Rotation matrix ─────────────── */

/**
 * Convert exponential coordinates ω = θ·n̂ ∈ ℝ³ to rotation matrix.
 *
 *   |ω| = θ,  n̂ = ω/θ  →  R = I + sin(θ)[n̂]× + (1−cos θ)[n̂]×²
 *
 * @param {number[]} omega  3-vector exponential coordinates
 * @returns {number[]}      row-major 9-element rotation matrix
 */
function expCoordToR(omega) {
  assert(Array.isArray(omega) && omega.length === 3,
    "expCoordToR: expected length-3 array");
  assert(omega.every(isFinite), "expCoordToR: components must be finite");

  const theta = norm3(omega);
  if (theta < ANGLE_ZERO) return [1,0,0, 0,1,0, 0,0,1];

  const axis = omega.map(v => v / theta);
  return axisAngleToR(axis, theta);
}

/**
 * Convert rotation matrix to exponential coordinates ω = θ·n̂.
 * @param {number[]} R  row-major 9-element rotation matrix
 * @returns {number[]}  3-vector ω
 */
function rToExpCoord(R) {
  const { axis, angle } = rToAxisAngle(R);
  return axis.map(v => v * angle);
}

/* ─── Normalization helpers ───────────────────────────────────────────────── */

/**
 * Normalize a 3-vector to unit length.
 * @param {number[]} v
 * @returns {number[]}
 */
function normalizeAxis(v) {
  assert(v.length === 3, "normalizeAxis: expected length-3 array");
  const n = norm3(v);
  assert(n > 1e-12, "normalizeAxis: cannot normalize zero vector");
  return v.map(x => x / n);
}

/**
 * Normalize a quaternion to unit length.
 * @param {number[]} q  [w, x, y, z]
 * @returns {number[]}
 */
function normalizeQuaternion(q) {
  assert(q.length === 4, "normalizeQuaternion: expected length-4 array");
  const n = Math.sqrt(q.reduce((s, v) => s + v*v, 0));
  assert(n > 1e-12, "normalizeQuaternion: cannot normalize zero quaternion");
  return q.map(v => v / n);
}

/* ─── Degree / radian utilities ──────────────────────────────────────────── */

/** Convert degrees to radians. */
function deg2rad(d) { return d * Math.PI / 180; }

/** Convert radians to degrees. */
function rad2deg(r) { return r * 180 / Math.PI; }

/* ─── High-level converter ─────────────────────────────────────────────────
 *
 * convert(input, fromRep) → { R, quaternion, axisAngle, eulerZYX, expCoord }
 *
 * fromRep:  'R' | 'quaternion' | 'axisAngle' | 'eulerZYX' | 'expCoord'
 * ─────────────────────────────────────────────────────────────────────────── */

/**
 * Convert from any rotation representation to all others.
 *
 * @param {object} input   — data for the source representation (see below)
 * @param {string} fromRep — one of 'R' | 'quaternion' | 'axisAngle' | 'eulerZYX' | 'expCoord'
 * @returns {{
 *   R:          number[],                           // 9-element row-major
 *   quaternion: number[],                           // [w, x, y, z]
 *   axisAngle:  { axis: number[], angle: number },
 *   eulerZYX:   { psi: number, theta: number, phi: number, gimbalLock: boolean },
 *   expCoord:   number[]                            // [ωx, ωy, ωz]
 * }}
 *
 * input shapes:
 *   fromRep='R':          input = number[9]  (row-major)
 *   fromRep='quaternion': input = [w, x, y, z]
 *   fromRep='axisAngle':  input = { axis: [nx,ny,nz], angle: θ }
 *   fromRep='eulerZYX':   input = { psi, theta, phi }  (radians)
 *   fromRep='expCoord':   input = [ωx, ωy, ωz]
 */
function convert(input, fromRep) {
  const reps = ['R', 'quaternion', 'axisAngle', 'eulerZYX', 'expCoord'];
  assert(reps.includes(fromRep), `convert: unknown representation '${fromRep}'`);

  // Step 1: normalise input to rotation matrix
  let R;
  switch (fromRep) {
    case 'R':
      assert(input.length === 9, "convert: R input must be length-9 array");
      R = [...input];
      break;
    case 'quaternion':
      R = quaternionToR(normalizeQuaternion(input));
      break;
    case 'axisAngle': {
      const ax = normalizeAxis(input.axis);
      R = axisAngleToR(ax, input.angle);
      break;
    }
    case 'eulerZYX':
      R = eulerZYXToR(input.psi, input.theta, input.phi);
      break;
    case 'expCoord':
      R = expCoordToR(input);
      break;
  }

  // Step 2: extract all representations from R
  const quaternion = rToQuaternion(R);
  const axisAngle  = rToAxisAngle(R);
  const eulerZYX   = rToEulerZYX(R);
  const expCoord   = rToExpCoord(R);

  return { R, quaternion, axisAngle, eulerZYX, expCoord };
}

/* ─── Exports ─────────────────────────────────────────────────────────────── */

const RotationConverter = {
  // Core math
  skew,
  axisAngleToR,
  rToAxisAngle,
  quaternionToR,
  rToQuaternion,
  eulerZYXToR,
  rToEulerZYX,
  expCoordToR,
  rToExpCoord,
  // Validation
  validateR,
  validateQuaternion,
  // Normalization
  normalizeAxis,
  normalizeQuaternion,
  // Utilities
  deg2rad,
  rad2deg,
  norm3,
  // High-level
  convert,
  // Constants (for tests)
  UNIT_TOL,
  ORTHOG_TOL,
  ANGLE_ZERO,
};

// Browser global
if (typeof window !== "undefined") window.RotationConverter = RotationConverter;

// CommonJS / Node (for Jest)
if (typeof module !== "undefined") module.exports = RotationConverter;
