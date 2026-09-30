/** DOM wiring for the Fixture and Dataset Explorer (#4541).
 * dataset-explorer.js supplies the pure hashing/validation/flatten engine;
 * this file fetches the manifest and fixtures and renders them into the page.
 */
'use strict';

(function attach() {
  function assert(condition, message) {
    if (!condition) throw new Error(`[dataset-explorer-ui] Contract violation: ${message}`);
  }

  function utf8Decode(bytes) {
    if (typeof TextDecoder !== 'undefined') return new TextDecoder('utf-8').decode(bytes);
    return Buffer.from(bytes).toString('utf8');
  }

  async function fetchJson(url) {
    const response = await fetch(url, { cache: 'no-cache' });
    if (!response.ok) throw new Error(`failed to load ${url} (${response.status})`);
    const bytes = new Uint8Array(await response.arrayBuffer());
    return { bytes, json: JSON.parse(utf8Decode(bytes)) };
  }

  function badge(state) {
    const span = document.createElement('span');
    span.className = `de-badge de-badge--${state}`;
    span.textContent = { valid: 'Valid', invalid: 'Invalid', unavailable: 'Schema unavailable' }[state];
    return span;
  }

  function buildTable(rows, caption) {
    const table = document.createElement('table');
    table.className = 'de-table';
    const captionEl = document.createElement('caption');
    captionEl.textContent = caption;
    const head = document.createElement('thead');
    head.innerHTML = '<tr><th scope="col">Field</th><th scope="col">Value</th></tr>';
    const body = document.createElement('tbody');
    for (const row of rows) {
      const tr = document.createElement('tr');
      const th = document.createElement('th');
      th.scope = 'row';
      th.textContent = row.truncated ? 'Remaining fields' : row.path;
      const td = document.createElement('td');
      td.textContent = row.truncated
        ? 'omitted (fixture is large; download the file to see every field)'
        : JSON.stringify(row.value);
      tr.append(th, td);
      body.appendChild(tr);
    }
    table.append(captionEl, head, body);
    return table;
  }

  function buildDownload(fixturePath, bytes, hash) {
    const wrap = document.createElement('div');
    wrap.className = 'de-download';
    const link = document.createElement('a');
    link.className = 'de-download__button';
    link.textContent = `Download ${fixturePath.split('/').pop()}`;
    link.download = fixturePath.split('/').pop();
    link.href = URL.createObjectURL(new Blob([bytes], { type: 'application/json' }));
    const hashEl = document.createElement('code');
    hashEl.className = 'de-download__hash';
    hashEl.textContent = `sha256:${hash}`;
    wrap.append(link, hashEl);
    return wrap;
  }

  async function renderFixture(container, fixture, family, base) {
    const card = document.createElement('article');
    card.className = 'de-card';
    const heading = document.createElement('h3');
    heading.textContent = fixture.path.split('/').pop();
    card.appendChild(heading);

    const { bytes, json } = await fetchJson(`${base}${fixture.path}`);
    const hash = window.DatasetExplorer.sha256Hex(bytes);

    const status = window.DatasetExplorer.describeSchemaStatus({
      declaredSchemaVersion: fixture.schema_version,
      schema: family.schema,
      instance: json,
    });
    const statusLine = document.createElement('p');
    statusLine.append(badge(status.state), document.createTextNode(` ${status.summary}`));
    card.appendChild(statusLine);

    if (status.errors.length > 0) {
      const list = document.createElement('ul');
      list.className = 'de-errors';
      for (const message of status.errors) {
        const item = document.createElement('li');
        item.textContent = message;
        list.appendChild(item);
      }
      card.appendChild(list);
    }

    card.appendChild(buildDownload(fixture.path, bytes, hash));

    const details = document.createElement('details');
    const summary = document.createElement('summary');
    summary.textContent = 'Data table';
    const rows = window.DatasetExplorer.flattenToRows(json);
    details.append(summary, buildTable(rows, `${fixture.path} contents`));
    card.appendChild(details);

    container.appendChild(card);
  }

  async function renderFamily(container, family, base) {
    const section = document.createElement('section');
    section.className = 'de-family';
    const heading = document.createElement('h2');
    heading.textContent = family.label;
    section.appendChild(heading);

    if (family.schema_path) {
      const { json } = await fetchJson(`${base}${family.schema_path}`);
      family.schema = json;
    }

    for (const fixture of family.fixtures) {
      // eslint-disable-next-line no-await-in-loop -- fixtures render in manifest order.
      await renderFixture(section, fixture, family, base);
    }
    container.appendChild(section);
  }

  async function init() {
    const root = document.getElementById('dataset-explorer-app');
    if (!root) return;
    const status = document.getElementById('dataset-explorer-status');
    const base = window.DATASET_EXPLORER_BASE_URL || '../';

    try {
      const { json: manifest } = await fetchJson(`${base}data/dataset_explorer_manifest.json`);
      assert(Array.isArray(manifest.families), 'manifest.families must be an array');
      for (const family of manifest.families) {
        // eslint-disable-next-line no-await-in-loop -- families render in manifest order.
        await renderFamily(root, family, base);
      }
      if (status) status.textContent = 'Fixtures loaded.';
    } catch (error) {
      if (status) status.textContent = `Could not load the fixture explorer: ${error.message}`;
    }
  }

  if (typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', init);
  }
  if (typeof module !== 'undefined') module.exports = { init };
})();
