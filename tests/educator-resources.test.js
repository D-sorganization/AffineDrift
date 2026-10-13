/**
 * Widget-backed answers on the Educator Resources page (WEB-14.7, #4609).
 *
 * The page's widget exercises must be reproducible from the widgets
 * themselves. These tests recompute each stated answer with the widget's own
 * code -- the rotation converter's engine and the Cardan demonstration's
 * inline functions -- and require the page to state the value to four
 * decimal places, so a widget change cannot leave a stale answer behind.
 */

"use strict";

const fs = require("fs");
const path = require("path");
const RC = require("../js/rotation-converter");

const ROOT = path.join(__dirname, "..");
const PAGE = fs
  .readFileSync(path.join(ROOT, "resources/educator-resources.qmd"), "utf8")
  .replace(/\s+/g, " ");
const CARDAN_HTML = fs.readFileSync(
  path.join(ROOT, "src/tools/wrist_universal_joint/grip_angle_simulator.html"),
  "utf8",
);
const DEG = Math.PI / 180;

/** Require |value| rounded to four places to appear on the page. */
function expectStated(value) {
  const text = Math.abs(value).toFixed(4);
  expect(PAGE).toContain(text);
}

/** Extract a named top-level function from the widget's inline script. */
function widgetFunction(name) {
  const start = CARDAN_HTML.indexOf(`function ${name}(`);
  expect(start).toBeGreaterThan(-1);
  let depth = 0;
  for (let i = CARDAN_HTML.indexOf("{", start); i < CARDAN_HTML.length; i += 1) {
    if (CARDAN_HTML[i] === "{") depth += 1;
    if (CARDAN_HTML[i] === "}") depth -= 1;
    if (depth === 0) {
      // eslint-disable-next-line no-new-func
      return new Function(`${CARDAN_HTML.slice(start, i + 1)}; return ${name};`)();
    }
  }
  throw new Error(`unterminated function ${name}`);
}

describe("Module 1: rotation converter answers", () => {
  test("Rz(90 deg) preset in every representation", () => {
    const result = RC.convert({ axis: [0, 0, 1], angle: 90 * DEG }, "axisAngle");
    expectStated(result.quaternion[0]);
    expectStated(result.quaternion[3]);
    expectStated(result.expCoord[2]);
    expect(result.eulerZYX.psi / DEG).toBeCloseTo(90, 9);
  });

  test("half-turn quaternion sign convention", () => {
    const result = RC.convert([0, 0, 0, -1], "quaternion");
    expect(result.quaternion[3]).toBeCloseTo(1, 12);
    expect(PAGE).toContain("(0,0,0,1)");
  });

  test("arbitrary preset: diagonal, quaternion and rotation vector", () => {
    const result = RC.convert({ axis: [1, 1, 1], angle: 47.3 * DEG }, "axisAngle");
    const trace = result.R[0] + result.R[4] + result.R[8];
    expectStated(trace);
    expectStated(result.R[0]);
    expectStated(result.R[1]);
    expectStated(result.R[2]);
    expectStated(result.quaternion[0]);
    expectStated(result.quaternion[1]);
    expectStated(result.axisAngle.angle);
    expectStated(result.expCoord[0]);
  });

  test("gimbal lock keeps only yaw minus roll", () => {
    const entered = RC.convert({ psi: 30 * DEG, theta: 90 * DEG, phi: 10 * DEG }, "eulerZYX");
    const reduced = RC.convert({ psi: 20 * DEG, theta: 90 * DEG, phi: 0 }, "eulerZYX");
    entered.R.forEach((entry, index) => expect(entry).toBeCloseTo(reduced.R[index], 12));
    const recovered = RC.rToEulerZYX(entered.R);
    expect(recovered.gimbalLock).toBe(true);
    expect(recovered.psi / DEG).toBeCloseTo(20, 9);
    expect(recovered.phi).toBe(0);
    expectStated(entered.R[1]);
    expectStated(entered.R[2]);
  });
});

describe("Module 2: Cardan demonstration answers", () => {
  const ratio = widgetFunction("universalJointTransmissionRatio");
  const inertia = widgetFunction("calculateInertia");

  test.each([0, 60])("speed and torque ratios at phase %d deg", (phase) => {
    const { omega_ratio: omegaRatio, tau_ratio: tauRatio } = ratio(phase * DEG, 30 * DEG);
    expect(omegaRatio * tauRatio).toBeCloseTo(1, 12);
    expectStated(omegaRatio);
    expectStated(tauRatio);
  });

  test("default club properties give the stated transverse inertia", () => {
    const [transverse, illustrative] = inertia(200, 100, 1.0, 0.85);
    expectStated(transverse);
    expect(illustrative).toBeCloseTo(0.5 * transverse, 12);
  });
});
