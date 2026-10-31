# Widget URL-Hash State Contract (`#state=`, #5255)

## 1. Purpose and Isolation Boundary

Defines the versioned, bounded, validated URL-hash state contract (`#state=<url-encoded-json>`) for interactive widgets under epic `#5171` (panel `th_0692a05b4cc8`, Idea 10). Each hash envelope targets a single named widget (`w`) and is strictly isolated: no shared cross-widget event bus is introduced.

## 2. Envelope Specification (`schemas/widgets/widget-url-state-v1.schema.json`)

- **Prefix**: `#state=` (or `state=` when normalized without the leading `#`).
- **Maximum raw hash length**: `512` characters (`MAX_STATE_HASH_LENGTH = 512`), checked **before** URI decoding or JSON parsing so oversized hashes are rejected in $O(1)$ time without throwing.
- **JSON Envelope (`v = 1`)**:
  - `v` (`integer`, required): Schema version, must equal `1`.
  - `w` (`string`, required): Widget identifier matching `^[a-z0-9-]{1,40}$` (e.g. `"dcr-visualizer"`). Any mismatch with the active widget is rejected without side effects.
  - `p` (`object`, required): Flat parameter map with no unknown keys and no prototype-pollution keys (`__proto__`, `constructor`, `prototype`).

## 3. Reference Implementation (`dcr-visualizer`)

Implemented in `js/dcr-visualizer.js` (`encodeWidgetStateHash`, `decodeWidgetStateHash`, `DCR_STATE_DEFAULTS`) and bound in `js/dcr-visualizer-ui.js`:

| Parameter | Default | Bounds | Contract |
| --- | --- | --- | --- |
| `x0` | `1` | `[-100, 100]`, `x0 !== 0` | Finite nonzero initial scalar state |
| `ubar` | `1` | `(0, 100]` | Finite positive control bound |
| `horizon` | `1` | `[0, 20]` | Finite nonnegative time horizon |
| `phase` | `0.5` | `[0, 1]` | Finite normalized phase fraction |

### Fallback Policy

`decodeWidgetStateHash(rawHash, defaults)` never throws: if `rawHash` is empty, exceeds 512 characters, has invalid percent-encoding or JSON syntax, specifies an unsupported version `v` or mismatched widget `w`, contains extra keys, or violates parameter bounds, it returns `{ valid: false, state: { ...defaults }, reason }`.
