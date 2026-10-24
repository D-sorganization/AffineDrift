const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');

describe('page head performance (#5165)', () => {
  test('site-head inlines theme preflight and does not block on dark-mode-toggle.js', () => {
    const siteHead = fs.readFileSync(path.join(ROOT, '_includes', 'site-head.html'), 'utf8');
    expect(siteHead).toMatch(/data-bs-theme/);
    expect(siteHead).not.toMatch(/<script[^>]+src="\/js\/dark-mode-toggle\.js"/);
  });

  test('dark-mode-toggle.js loads deferred after the body', () => {
    const afterBody = fs.readFileSync(
      path.join(ROOT, '_includes', 'site-after-body.html'),
      'utf8',
    );
    expect(afterBody).toMatch(/<script src="\/js\/dark-mode-toggle\.js" defer><\/script>/);
  });
});
