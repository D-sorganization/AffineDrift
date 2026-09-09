/** Right-handed active SO(3): column vectors, Hamilton [w,x,y,z], radians.
 * Matrices are row-major. Tolerance accepts rounding, not arbitrary data fitting.
 * The paired Rotation Representations Reference derives the conventions/limits.
 */
'use strict';
const UNIT_TOL = 1e-6;
const ORTHOG_TOL = 1e-5; // Maximum entry residual and absolute determinant error.
const ANGLE_ZERO = 1e-10; // Display only; small rotations are retained.
const GIMBAL_TOL = 1e-12; // |cos(pitch)| below which roll is set to zero.

function assert(condition, message) {
  if (!condition) throw new Error(`[rotation-converter] Contract violation: ${message}`);
}

/** Require a fixed-size numeric array without string coercion or nonfinite values. */
function finiteVector(value, size, name) {
  assert((Array.isArray(value) || ArrayBuffer.isView(value)) && value.length === size,
    `${name}: expected length-${size} array`);
  assert(Array.from(value).every(Number.isFinite), `${name}: components must be finite numbers`);
  return Array.from(value);
}

/** Scale first to normalize very large or very small finite inputs safely. */
function unitVector(value, size, name) {
  const vector = finiteVector(value,size,name);
  const scale = Math.max(...vector.map(Math.abs));
  assert(scale > 0, `${name}: cannot normalize zero vector`);
  const scaled = vector.map(x => x/scale);
  const norm = Math.hypot(...scaled);
  return scaled.map(x => x/norm);
}

function norm3(value) { return Math.hypot(...finiteVector(value,3,'norm3')); }

/** skew(v) u = v cross u. */
function skew(value) {
  const [x,y,z] = finiteVector(value,3,'skew');
  return [0,-z,y, z,0,-x, -y,x,0];
}

/** Validate an approximate matrix without projecting it onto SO(3). */
function validateR(value) {
  const R = finiteVector(value,9,'validateR');
  let orthogError = 0;
  for (let i = 0; i < 3; i++) {
    for (let j = 0; j < 3; j++) {
      const product = R[i]*R[j]+R[3+i]*R[3+j]+R[6+i]*R[6+j];
      orthogError = Math.max(orthogError,Math.abs(product-Number(i === j)));
    }
  }
  const det = R[0]*(R[4]*R[8]-R[5]*R[7])-R[1]*(R[3]*R[8]-R[5]*R[6])
    +R[2]*(R[3]*R[7]-R[4]*R[6]);
  const detError = Math.abs(det-1);
  return {valid: orthogError < ORTHOG_TOL && detError < ORTHOG_TOL, orthogError,detError};
}

function checkedR(value) {
  const matrix = finiteVector(value,9,'rotation matrix');
  assert(validateR(matrix).valid,'matrix must be a proper rotation in SO(3)');
  return matrix;
}

function validateQuaternion(value) {
  const quaternion = finiteVector(value,4,'validateQuaternion');
  const normError = Math.abs(Math.hypot(...quaternion)-1);
  return {valid: normError < UNIT_TOL,normError};
}

function normalizeAxis(value) { return unitVector(value,3,'normalizeAxis'); }
function normalizeQuaternion(value) { return unitVector(value,4,'normalizeQuaternion'); }
function deg2rad(value) { return value*(Math.PI/180); }
function rad2deg(value) { return value*(180/Math.PI); }

/** Hamilton unit quaternion to matrix; normalize only within unit tolerance. */
function quaternionToR(value) {
  assert(validateQuaternion(value).valid,'quaternionToR: quaternion must be unit');
  const [w,x,y,z] = normalizeQuaternion(value);
  return [1-2*(y*y+z*z),2*(x*y-w*z),2*(x*z+w*y),
    2*(x*y+w*z),1-2*(x*x+z*z),2*(y*z-w*x),
    2*(x*z-w*y),2*(y*z+w*x),1-2*(x*x+y*y)];
}

/** Equivalent half-angle Rodrigues formula, retaining tiny nonzero angles. */
function axisAngleToR(axis,angle) {
  const vector = finiteVector(axis,3,'axisAngleToR');
  assert(Number.isFinite(angle),'axisAngleToR: angle must be finite');
  assert(Math.abs(norm3(vector)-1) < UNIT_TOL,'axisAngleToR: axis must be unit vector');
  return quaternionToR([Math.cos(angle/2),
    ...normalizeAxis(vector).map(x => Math.sin(angle/2)*x)]);
}

/** Largest-component extraction avoids a small denominator near 180 degrees.
 * Choose w >= 0 for a principal angle. At pi the axis sign is conventional.
 */
function rToQuaternion(value) {
  const R = checkedR(value);
  const trace = R[0]+R[4]+R[8];
  const squares = [1+trace,1+2*R[0]-trace,1+2*R[4]-trace,1+2*R[8]-trace];
  const selected = squares.indexOf(Math.max(...squares));
  const result = [0,0,0,0];
  result[selected] = Math.sqrt(Math.max(0,squares[selected]))/2;
  const divisor = 4*result[selected];
  if (selected === 0) {
    result[1] = (R[7]-R[5])/divisor;
    result[2] = (R[2]-R[6])/divisor;
    result[3] = (R[3]-R[1])/divisor;
  } else {
    const i = selected-1,j = (i+1)%3,k = (i+2)%3;
    result[0] = (R[3*k+j]-R[3*j+k])/divisor;
    result[j+1] = (R[3*j+i]+R[3*i+j])/divisor;
    result[k+1] = (R[3*k+i]+R[3*i+k])/divisor;
  }
  const unit = normalizeQuaternion(result);
  return unit[0] < 0 ? unit.map(x => -x) : unit;
}

/** Principal angle in [0,pi]; only exact identity gets a conventional z axis. */
function rToAxisAngle(value) {
  const [w,...vector] = rToQuaternion(value);
  const sineHalf = Math.hypot(...vector);
  if (sineHalf === 0) return {axis:[0,0,1],angle:0};
  return {axis:vector.map(x => x/sineHalf),angle:2*Math.atan2(sineHalf,w)};
}

/** Intrinsic ZYX; equivalent to fixed-axis XYZ with reversed angle order. */
function eulerZYXToR(psi,theta,phi) {
  assert([psi,theta,phi].every(Number.isFinite),'eulerZYXToR: angles must be finite');
  const cp=Math.cos(psi),sp=Math.sin(psi),ct=Math.cos(theta),st=Math.sin(theta);
  const cr=Math.cos(phi),sr=Math.sin(phi);
  return [cp*ct,cp*st*sr-sp*cr,cp*st*cr+sp*sr,
    sp*ct,sp*st*sr+cp*cr,sp*st*cr-cp*sr,-st,ct*sr,ct*cr];
}

/** atan2 preserves near-lock information lost when asin's argument rounds to one. */
function rToEulerZYX(value) {
  const R=checkedR(value),cosinePitch=Math.hypot(R[0],R[3]);
  const theta=Math.atan2(-R[6],cosinePitch),gimbalLock=cosinePitch < GIMBAL_TOL;
  return {psi:gimbalLock ? Math.atan2(-R[1],R[4]) : Math.atan2(R[3],R[0]),
    theta,phi:gimbalLock ? 0 : Math.atan2(R[7],R[8]),gimbalLock};
}

/** Rotation-vector components use radians, not radians per second. */
function expCoordToR(value) {
  const vector=finiteVector(value,3,'expCoordToR'),angle=Math.hypot(...vector);
  assert(Number.isFinite(angle),'expCoordToR: rotation-vector magnitude must be finite');
  if (angle === 0) return [1,0,0,0,1,0,0,0,1];
  return axisAngleToR(vector.map(x => x/angle),angle);
}

function rToExpCoord(value) {
  const {axis,angle}=rToAxisAngle(value);
  return axis.map(x => x*angle);
}

/** Approximate matrices are retained; normalized outputs may differ by rounding.
 * This neither fits noisy data nor estimates measurement uncertainty.
 */
function convert(input,fromRep) {
  const readers={R:()=>checkedR(input),
    quaternion:()=>quaternionToR(normalizeQuaternion(input)),
    axisAngle:()=>axisAngleToR(normalizeAxis(input.axis),input.angle),
    eulerZYX:()=>eulerZYXToR(input.psi,input.theta,input.phi),
    expCoord:()=>expCoordToR(input)};
  assert(Object.hasOwn(readers,fromRep),`convert: unknown representation '${fromRep}'`);
  const R=readers[fromRep](),axisAngle=rToAxisAngle(R);
  return {R,quaternion:rToQuaternion(R),axisAngle,eulerZYX:rToEulerZYX(R),
    expCoord:axisAngle.axis.map(x=>x*axisAngle.angle)};
}

const RotationConverter={skew,norm3,axisAngleToR,rToAxisAngle,quaternionToR,
  rToQuaternion,eulerZYXToR,rToEulerZYX,expCoordToR,rToExpCoord,validateR,
  validateQuaternion,normalizeAxis,normalizeQuaternion,deg2rad,rad2deg,convert,
  UNIT_TOL,ORTHOG_TOL,ANGLE_ZERO};
if (typeof window !== 'undefined') window.RotationConverter=RotationConverter;
if (typeof module !== 'undefined') module.exports=RotationConverter;
