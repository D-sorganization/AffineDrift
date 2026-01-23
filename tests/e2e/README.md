# End-to-End Tests

This directory contains end-to-end tests for the AffineDrift website using Playwright.

## Setup

Install dependencies:

```bash
npm install
npx playwright install
```

## Running Tests

### Run all tests

```bash
npm run test:e2e
```

### Run tests with UI

```bash
npm run test:e2e:ui
```

### Run tests in headed mode (see browser)

```bash
npm run test:e2e:headed
```

### Run specific test file

```bash
npx playwright test tests/e2e/homepage.spec.js
```

### Run tests in specific browser

```bash
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
```

## Test Structure

### Homepage Tests (`homepage.spec.js`)
- Page loads successfully
- Navigation works
- Logo has alt text
- Mobile responsive
- No console errors

### Navigation Tests (`navigation.spec.js`)
- Navigate between pages
- Table of contents works
- Smooth scrolling to anchors
- Active section highlighting

### Accessibility Tests (`accessibility.spec.js`)
- Proper heading hierarchy
- Alt text on all images
- ARIA labels on navigation
- Keyboard navigation
- Color contrast
- Lang attribute
- Skip to main content

### Search Tests (`search.spec.js`)
- Search button/input exists
- Search modal opens
- Keyboard shortcut works

## Configuration

Tests are configured in `playwright.config.js`:

- **Base URL**: https://affinedrift.com (production)
- **Local testing**: Starts local server on port 8000
- **Browsers**: Chromium, Firefox, WebKit
- **Mobile**: Pixel 5, iPhone 12
- **Screenshots**: On failure only
- **Traces**: On first retry

## CI/CD Integration

Tests run automatically in CI with:
- 2 retries on failure
- Single worker for stability
- HTML report generation

## Writing New Tests

Follow this pattern:

```javascript
const { test, expect } = require('@playwright/test');

test.describe('Feature Name', () => {
  test('should do something', async ({ page }) => {
    await page.goto('/');
    
    // Your test code
    const element = page.locator('selector');
    await expect(element).toBeVisible();
  });
});
```

## Best Practices

1. **Use semantic selectors**: Prefer `role`, `aria-label`, and text content over CSS classes
2. **Wait for network idle**: Use `waitForLoadState('networkidle')` after navigation
3. **Handle optional elements**: Check `count()` before interacting
4. **Mobile testing**: Test on both desktop and mobile viewports
5. **Accessibility**: Include accessibility checks in all test suites

## Debugging

### View test report

```bash
npx playwright show-report
```

### Debug specific test

```bash
npx playwright test --debug tests/e2e/homepage.spec.js
```

### Generate trace

```bash
npx playwright test --trace on
```

## Coverage

Current test coverage:
- Homepage: 5 tests
- Navigation: 5 tests
- Accessibility: 7 tests
- Search: 3 tests

**Total: 20 end-to-end tests**

## Future Enhancements

- [ ] Add tests for article pages
- [ ] Add tests for bibliography
- [ ] Add tests for models pages
- [ ] Add performance tests
- [ ] Add visual regression tests
- [ ] Add API tests for search
