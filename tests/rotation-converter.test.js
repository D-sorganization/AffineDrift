/**
 * TDD test suite for js/rotation-converter.js
 *
 * Coverage:
 *   - Identity rotation in all representations
 *   - 90° and 180° rotations about each principal axis
 *   - Arbitrary rotation (n̂=[1,1,1]/√3, θ=47.3°)
 *   - Round-trip conversions (error < 1e-9)
 *   - Degenerate cases (θ→0, θ=π, gimbal lock)
 *   - DbC violations (bad inputs throw)
 *   - Utility functions (skew, normalise, deg2rad)
 */

"use strict";

const RC = require("../js/rotation-converter");

/* ─── Numeric helpers ─────────────────────────────────────────────────────── */

const ATOL = 1e-9;

/** Max absolute element-wise difference between two arrays. */
function maxAbsDiff(a, b) {
  return Math.max(...a.map((v, i) => Math.abs(v - b[i])));
}

function expectNear(received, expected, tol = ATOL, label = "") {
  const err = Array.isArray(received)
    ? maxAbsDiff(received, expected)
    : Math.abs(received - expected);
  if (err > tol) {
    throw new Error(
      `${label} — expected near ${JSON.stringify(expected)}, got ${JSON.stringify(received)}, error=${err.toExponential(2)}`
    );
  }
}

/* ─── Known rotation matrices ─────────────────────────────────────────────── */

const I3 = [1,0,0, 0,1,0, 0,0,1];

// Rx(90°)
const Rx90 = [1,0,0, 0,0,-1, 0,1,0];
// Ry(90°)
const Ry90 = [0,0,1, 0,1,0, -1,0,0];
// Rz(90°)
const Rz90 = [0,-1,0, 1,0,0, 0,0,1];

// Rz(180°)
const Rz180 = [-1,0,0, 0,-1,0, 0,0,1];

// Arbitrary: n̂ = [1,1,1]/√3, θ = 47.3°
const SQ3 = 1 / Math.sqrt(3);
const TH  = 47.3 * Math.PI / 180;
const R_arb = RC.axisAngleToR([SQ3, SQ3, SQ3], TH);

/* ═══════════════════════════════════════════════════════════════════════════ */
describe("skew", () => {
  test("produces antisymmetric matrix for canonical basis vectors", () => {
    const K = RC.skew([0, 0, 1]);
    // [e₃]× = [[0,-1,0],[1,0,0],[0,0,0]]
    expectNear(K, [0,-1,0, 1,0,0, 0,0,0]);
  });

  test("skew([a,b,c]) satisfies K + Kᵀ = 0", () => {
    const K = RC.skew([2, -3, 5]);
    const err = Math.max(...K.map((v, i) => Math.abs(v + K[3*(i%3) + Math.floor(i/3)])));
    expect(err).toBeLessThan(ATOL);
  });

  test("throws on wrong length", () => {
    expect(() => RC.skew([1, 2])).toThrow("length-3");
  });

  test("throws on non-finite component", () => {
    expect(() => RC.skew([1, NaN, 3])).toThrow("finite");
  });
});

/* ─────────────────────────────────────────────────────────────────────────── */
describe("validateR", () => {
  test("identity passes", () => {
    const { valid } = RC.validateR(I3);
    expect(valid).toBe(true);
  });

  test("Rx90 passes", () => {
    expect(RC.validateR(Rx90).valid).toBe(true);
  });

  test("scrambled matrix fails", () => {
    const { valid } = RC.validateR([1,1,1, 1,1,1, 1,1,1]);
    expect(valid).toBe(false);
  });
});

/* ─────────────────────────────────────────────────────────────────────────── */
describe("axisAngleToR", () => {
  test("zero angle → identity", () => {
    const R = RC.axisAngleToR([0, 0, 1], 0);
    expectNear(R, I3);
  });

  test("Rz(90°)", () => {
    const R = RC.axisAngleToR([0, 0, 1], Math.PI / 2);
    expectNear(R, Rz90);
  });

  test("Rx(90°)", () => {
    const R = RC.axisAngleToR([1, 0, 0], Math.PI / 2);
    expectNear(R, Rx90);
  });

  test("Ry(90°)", () => {
    const R = RC.axisAngleToR([0, 1, 0], Math.PI / 2);
    expectNear(R, Ry90);
  });

  test("Rz(180°)", () => {
    const R = RC.axisAngleToR([0, 0, 1], Math.PI);
    expectNear(R, Rz180);
  });

  test("result passes validateR", () => {
    expect(RC.validateR(R_arb).valid).toBe(true);
  });

  test("throws if axis not unit", () => {
    expect(() => RC.axisAngleToR([1, 1, 0], Math.PI / 4)).toThrow("unit vector");
  });

  test("throws if angle not finite", () => {
    expect(() => RC.axisAngleToR([0, 0, 1], Infinity)).toThrow("finite");
  });
});

/* ─────────────────────────────────────────────────────────────────────────── */
describe("rToAxisAngle", () => {
  test("identity → angle 0", () => {
    const { angle } = RC.rToAxisAngle(I3);
    expect(Math.abs(angle)).toBeLessThan(ATOL);
  });

  test("Rz(90°) → axis=[0,0,1], angle=90°", () => {
    const { axis, angle } = RC.rToAxisAngle(Rz90);
    expectNear(Math.abs(axis[2]), 1);                // z-component ≈ ±1
    expectNear(angle, Math.PI / 2);
  });

  test("180° rotation round-trip", () => {
    const R = RC.axisAngleToR([0, 0, 1], Math.PI);
    const { axis, angle } = RC.rToAxisAngle(R);
    expectNear(Math.abs(angle), Math.PI);
    expectNear(RC.norm3(axis), 1);
  });

  test("arbitrary round-trip — angle", () => {
    const { angle } = RC.rToAxisAngle(R_arb);
    expectNear(angle, TH);
  });

  test("arbitrary round-trip — axis direction", () => {
    const { axis } = RC.rToAxisAngle(R_arb);
    // Axis may be negated (cos-sign ambiguity for axis); test |axis · n̂_orig| ≈ 1
    const dot = Math.abs(RC.norm3([axis[0]-SQ3, axis[1]-SQ3, axis[2]-SQ3]));
    // Either axis ≈ [SQ3,SQ3,SQ3] or axis ≈ -[SQ3,SQ3,SQ3]
    const axisDot = Math.abs(axis[0]*SQ3 + axis[1]*SQ3 + axis[2]*SQ3);
    expectNear(axisDot, 1);
  });
});

/* ─────────────────────────────────────────────────────────────────────────── */
describe("quaternionToR", () => {
  test("identity quaternion [1,0,0,0] → identity matrix", () => {
    expectNear(RC.quaternionToR([1,0,0,0]), I3);
  });

  test("Rz(90°) quaternion", () => {
    const q = [Math.cos(Math.PI/4), 0, 0, Math.sin(Math.PI/4)];
    expectNear(RC.quaternionToR(q), Rz90);
  });

  test("antipodal quaternion gives same R", () => {
    const q = [Math.cos(Math.PI/4), 0, 0, Math.sin(Math.PI/4)];
    const qn = q.map(v => -v);
    expectNear(RC.quaternionToR(q), RC.quaternionToR(qn));
  });

  test("throws if not unit", () => {
    expect(() => RC.quaternionToR([1, 1, 0, 0])).toThrow("unit");
  });
});

/* ─────────────────────────────────────────────────────────────────────────── */
describe("rToQuaternion", () => {
  test("identity → [1,0,0,0]", () => {
    const q = RC.rToQuaternion(I3);
    expectNear(q, [1, 0, 0, 0]);
  });

  test("Rz(90°) → correct quaternion", () => {
    const q = RC.rToQuaternion(Rz90);
    // w=cos(45°), z=sin(45°)
    expectNear(q[0], Math.cos(Math.PI/4));
    expectNear(Math.abs(q[3]), Math.sin(Math.PI/4));
  });

  test("result is unit quaternion", () => {
    const q = RC.rToQuaternion(R_arb);
    const norm = Math.sqrt(q.reduce((s,v)=>s+v*v,0));
    expectNear(norm, 1);
  });

  test("arbitrary round-trip: R→q→R", () => {
    const q = RC.rToQuaternion(R_arb);
    const R2 = RC.quaternionToR(q);
    expectNear(R2, R_arb);
  });

  test("180° case: Rz(180°)", () => {
    const q = RC.rToQuaternion(Rz180);
    const norm = Math.sqrt(q.reduce((s,v)=>s+v*v,0));
    expectNear(norm, 1);
    // Reconstruct and compare
    const R2 = RC.quaternionToR(q);
    expectNear(R2, Rz180);
  });
});

/* ─────────────────────────────────────────────────────────────────────────── */
describe("eulerZYXToR", () => {
  test("all-zero angles → identity", () => {
    expectNear(RC.eulerZYXToR(0, 0, 0), I3);
  });

  test("ψ=90°, θ=0, φ=0 → Rz(90°)", () => {
    expectNear(RC.eulerZYXToR(Math.PI/2, 0, 0), Rz90);
  });

  test("ψ=0, θ=0, φ=90° → Rx(90°)", () => {
    expectNear(RC.eulerZYXToR(0, 0, Math.PI/2), Rx90);
  });

  test("ψ=0, θ=90°, φ=0 → Ry(90°)", () => {
    expectNear(RC.eulerZYXToR(0, Math.PI/2, 0), Ry90);
  });

  test("throws on NaN angle", () => {
    expect(() => RC.eulerZYXToR(NaN, 0, 0)).toThrow("finite");
  });
});

/* ─────────────────────────────────────────────────────────────────────────── */
describe("rToEulerZYX", () => {
  test("identity → all zeros", () => {
    const { psi, theta, phi } = RC.rToEulerZYX(I3);
    expectNear(psi, 0); expectNear(theta, 0); expectNear(phi, 0);
  });

  test("Rz(90°) → ψ=90°, θ=φ=0", () => {
    const { psi, theta, phi } = RC.rToEulerZYX(Rz90);
    expectNear(psi, Math.PI/2); expectNear(theta, 0); expectNear(phi, 0);
  });

  test("arbitrary round-trip: R→euler→R", () => {
    const { psi, theta, phi } = RC.rToEulerZYX(R_arb);
    const R2 = RC.eulerZYXToR(psi, theta, phi);
    expectNear(R2, R_arb);
  });

  test("detects gimbal lock at θ=+90°", () => {
    const Rgl = RC.eulerZYXToR(0, Math.PI/2, 0);
    const result = RC.rToEulerZYX(Rgl);
    expect(result.gimbalLock).toBe(true);
  });

  test("detects gimbal lock at θ=−90°", () => {
    const Rgl = RC.eulerZYXToR(0, -Math.PI/2, 0);
    const result = RC.rToEulerZYX(Rgl);
    expect(result.gimbalLock).toBe(true);
  });
});

/* ─────────────────────────────────────────────────────────────────────────── */
describe("expCoordToR / rToExpCoord", () => {
  test("zero vector → identity", () => {
    expectNear(RC.expCoordToR([0, 0, 0]), I3);
  });

  test("ω = [0,0,π/2] → Rz(90°)", () => {
    expectNear(RC.expCoordToR([0, 0, Math.PI/2]), Rz90);
  });

  test("round-trip: R→ω→R (arbitrary)", () => {
    const omega = RC.rToExpCoord(R_arb);
    const R2 = RC.expCoordToR(omega);
    expectNear(R2, R_arb);
  });

  test("|ω| equals rotation angle", () => {
    const omega = RC.rToExpCoord(Rx90);
    expectNear(RC.norm3(omega), Math.PI/2);
  });
});

/* ─────────────────────────────────────────────────────────────────────────── */
describe("convert (high-level API)", () => {
  test("axisAngle→all representations and back — quaternion", () => {
    const inp = { axis: [SQ3, SQ3, SQ3], angle: TH };
    const out = RC.convert(inp, "axisAngle");
    const out2 = RC.convert(out.quaternion, "quaternion");
    expectNear(out2.R, out.R);
  });

  test("eulerZYX→all representations and back — eulerZYX", () => {
    const inp = { psi: 0.3, theta: 0.5, phi: -0.2 };
    const out = RC.convert(inp, "eulerZYX");
    const { psi, theta, phi } = out.eulerZYX;
    const out2 = RC.convert({ psi, theta, phi }, "eulerZYX");
    expectNear(out2.R, out.R);
  });

  test("throws on unknown representation", () => {
    expect(() => RC.convert([1,0,0,0], "foobar")).toThrow("unknown representation");
  });
});

/* ─────────────────────────────────────────────────────────────────────────── */
describe("normalizeAxis / normalizeQuaternion", () => {
  test("normalizeAxis: [3,0,0] → [1,0,0]", () => {
    expectNear(RC.normalizeAxis([3,0,0]), [1,0,0]);
  });

  test("normalizeAxis: throws on zero vector", () => {
    expect(() => RC.normalizeAxis([0,0,0])).toThrow();
  });

  test("normalizeQuaternion: [2,0,0,0] → [1,0,0,0]", () => {
    expectNear(RC.normalizeQuaternion([2,0,0,0]), [1,0,0,0]);
  });
});

/* ─────────────────────────────────────────────────────────────────────────── */
describe("deg2rad / rad2deg", () => {
  test("180° = π rad", () => { expectNear(RC.deg2rad(180), Math.PI); });
  test("π rad = 180°",  () => { expectNear(RC.rad2deg(Math.PI), 180); });
  test("round-trip",    () => { expectNear(RC.deg2rad(RC.rad2deg(1.23)), 1.23); });
});
