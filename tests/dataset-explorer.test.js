/** Pure logic for the Fixture and Dataset Explorer (#4541): hashing, schema
 * validation, and table flattening. No DOM; exercised directly against the
 * real ztcf fixtures and schema checked into data/ztcf.
 */
const fs = require('fs');
const path = require('path');
const {
  utf8Encode,
  sha256Hex,
  validateAgainstSchema,
  flattenToRows,
  describeSchemaStatus,
} = require('../js/dataset-explorer');

const DATA_ROOT = path.join(__dirname, '..', 'data');

function loadJson(relPath) {
  return JSON.parse(fs.readFileSync(path.join(DATA_ROOT, relPath), 'utf8'));
}

const ztcfSchema = loadJson('ztcf/ztcf_intervention_v1.schema.json');
const fixtureV1 = loadJson('ztcf/planar_golf_forward_fixture_v1.json');
const fixtureV2 = loadJson('ztcf/planar_golf_forward_fixture_v2.json');

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

describe('sha256Hex', () => {
  test.each([
    ['', 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'],
    ['abc', 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'],
    [
      'The quick brown fox jumps over the lazy dog',
      'd7a8fbb307d7809469ca9abcb0082e4f8d5651e46d3cdb762d02d0bf37c9e592',
    ],
  ])('matches the known digest for %p', (input, expected) => {
    expect(sha256Hex(utf8Encode(input))).toBe(expected);
  });

  test('is deterministic and content-sensitive', () => {
    const a = sha256Hex(utf8Encode(JSON.stringify(fixtureV1)));
    const b = sha256Hex(utf8Encode(JSON.stringify(fixtureV1)));
    const c = sha256Hex(utf8Encode(JSON.stringify(fixtureV2)));
    expect(a).toBe(b);
    expect(a).not.toBe(c);
    expect(a).toMatch(/^[0-9a-f]{64}$/);
  });

  test('rejects non-byte input instead of silently hashing garbage', () => {
    expect(() => sha256Hex('abc')).toThrow(/Uint8Array/);
  });
});

describe('validateAgainstSchema against the real ztcf schema', () => {
  test('accepts both checked-in fixtures', () => {
    expect(validateAgainstSchema(ztcfSchema, fixtureV1)).toEqual({ valid: true, errors: [] });
    expect(validateAgainstSchema(ztcfSchema, fixtureV2)).toEqual({ valid: true, errors: [] });
  });

  test('rejects a missing required field', () => {
    const broken = clone(fixtureV1);
    delete broken.model.id;
    const result = validateAgainstSchema(ztcfSchema, broken);
    expect(result.valid).toBe(false);
    expect(result.errors.join(' ')).toMatch(/model\.id/);
  });

  test('rejects a const violation', () => {
    const broken = clone(fixtureV1);
    broken.state.position_units = 'deg';
    const result = validateAgainstSchema(ztcfSchema, broken);
    expect(result.valid).toBe(false);
    expect(result.errors.join(' ')).toMatch(/state\.position_units/);
  });

  test('rejects a pattern violation on source_revision', () => {
    const broken = clone(fixtureV1);
    broken.model.source_revision = 'not-a-sha';
    const result = validateAgainstSchema(ztcfSchema, broken);
    expect(result.valid).toBe(false);
    expect(result.errors.join(' ')).toMatch(/source_revision/);
  });

  test('rejects steps below the minimum', () => {
    const broken = clone(fixtureV1);
    broken.integration.steps = 0;
    const result = validateAgainstSchema(ztcfSchema, broken);
    expect(result.valid).toBe(false);
  });

  test('rejects an enum violation on parity.status', () => {
    const broken = clone(fixtureV1);
    broken.parity.status = 'confirmed';
    const result = validateAgainstSchema(ztcfSchema, broken);
    expect(result.valid).toBe(false);
  });

  test('rejects a zeroed_input.values entry that is not exactly zero', () => {
    const broken = clone(fixtureV1);
    broken.zeroed_input.values = [0, 0, 1];
    const result = validateAgainstSchema(ztcfSchema, broken);
    expect(result.valid).toBe(false);
  });

  test('enforces the if/then/else branch: unavailable status requires null expected', () => {
    const broken = clone(fixtureV1);
    broken.status = 'unavailable';
    broken.failure = { code: 'engine_unavailable', message: 'not installed' };
    // expected is left populated, which the else-branch forbids.
    const result = validateAgainstSchema(ztcfSchema, broken);
    expect(result.valid).toBe(false);
  });

  test('accepts a fully valid unavailable-status record', () => {
    const record = clone(fixtureV1);
    record.status = 'unavailable';
    record.expected = null;
    record.failure = { code: 'engine_unavailable', message: 'not installed' };
    const result = validateAgainstSchema(ztcfSchema, record);
    expect(result).toEqual({ valid: true, errors: [] });
  });
});

describe('flattenToRows', () => {
  test('produces one row per leaf value with a dotted path', () => {
    const rows = flattenToRows({ a: 1, b: { c: 'x', d: [true, false] } });
    const paths = rows.map((row) => row.path);
    expect(paths).toEqual(expect.arrayContaining(['a', 'b.c', 'b.d[0]', 'b.d[1]']));
    expect(rows.find((row) => row.path === 'a').value).toBe(1);
  });

  test('truncates pathologically large documents instead of hanging the page', () => {
    const huge = {};
    for (let i = 0; i < 5000; i += 1) huge[`key_${i}`] = i;
    const rows = flattenToRows(huge, { maxRows: 200 });
    expect(rows.length).toBe(201); // 200 leaf rows + one truncation marker row
    expect(rows[rows.length - 1].truncated).toBe(true);
  });
});

describe('describeSchemaStatus', () => {
  test('reports unavailable, never fabricated, when no schema is published', () => {
    const status = describeSchemaStatus({
      declaredSchemaVersion: 'affinedrift.population-generalization-report/v1',
      schema: null,
      instance: { schema_version: 'affinedrift.population-generalization-report/v1' },
    });
    expect(status.state).toBe('unavailable');
    expect(status.summary).toMatch(/affinedrift\.population-generalization-report\/v1/);
  });

  test('reports valid when a published schema accepts the instance', () => {
    const status = describeSchemaStatus({
      declaredSchemaVersion: fixtureV1.schema_version,
      schema: ztcfSchema,
      instance: fixtureV1,
    });
    expect(status.state).toBe('valid');
    expect(status.errors).toEqual([]);
  });

  test('reports invalid with the underlying errors when validation fails', () => {
    const broken = clone(fixtureV1);
    delete broken.model.id;
    const status = describeSchemaStatus({
      declaredSchemaVersion: broken.schema_version,
      schema: ztcfSchema,
      instance: broken,
    });
    expect(status.state).toBe('invalid');
    expect(status.errors.length).toBeGreaterThan(0);
  });
});
