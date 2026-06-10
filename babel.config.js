// Babel config used by Jest (via babel-jest) so the ESM-authored browser
// modules under js/ (which use `import`/`export`) can be unit-tested under
// jsdom. Production serving is unaffected — the browser loads the ESM source
// directly; this transform applies only to the test run.
module.exports = {
  presets: [
    [
      '@babel/preset-env',
      {
        targets: { node: 'current' },
      },
    ],
  ],
};
