const { test, expect } = require('@playwright/test');

/**
 * Touch Target Size Compliance Test (WCAG 2.5.5)
 *
 * Validates that all interactive elements meet the minimum 44×44px
 * touch target size requirement for accessibility on mobile devices.
 *
 * Reference: https://www.w3.org/WAI/WCAG21/Understanding/target-size.html
 */

test.describe('Touch Target Compliance (WCAG 2.5.5)', () => {
  const MIN_TOUCH_TARGET = 44; // pixels

  /**
   * Helper function to check if an element meets touch target requirements
   */
  const checkTouchTarget = async (page, selector, elementName) => {
    const elements = await page.locator(selector).all();

    if (elements.length === 0) {
      return { skipped: true, count: 0, elementName };
    }

    const results = [];
    for (const element of elements) {
      const boundingBox = await element.boundingBox();

      if (!boundingBox) {
        results.push({
          element: elementName,
          selector: selector,
          compliant: false,
          error: 'Element not visible/no bounding box',
          height: null,
          width: null,
        });
        continue;
      }

      const { height, width } = boundingBox;
      const compliant = height >= MIN_TOUCH_TARGET && width >= MIN_TOUCH_TARGET;

      if (!compliant) {
        results.push({
          element: elementName,
          selector: selector,
          compliant: false,
          height: Math.round(height),
          width: Math.round(width),
          minRequired: MIN_TOUCH_TARGET,
        });
      } else {
        results.push({
          element: elementName,
          selector: selector,
          compliant: true,
          height: Math.round(height),
          width: Math.round(width),
        });
      }
    }

    return { results, count: elements.length };
  };

  test('should validate button touch targets', async ({ page }) => {
    await page.goto('/');

    const buttonTests = [
      { selector: 'button.btn-primary', name: 'Primary buttons' },
      { selector: 'button.copy-btn', name: 'Copy buttons' },
      { selector: 'button.sort-btn', name: 'Sort buttons' },
      { selector: '.copy-email-btn', name: 'Copy email buttons' },
      { selector: 'button[type="submit"]', name: 'Submit buttons' },
    ];

    for (const test of buttonTests) {
      const { results, count, skipped } = await checkTouchTarget(
        page,
        test.selector,
        test.name
      );

      if (skipped) {
        console.log(`✓ ${test.name}: No elements found (skipped)`);
        continue;
      }

      const nonCompliant = results.filter(r => !r.compliant);
      if (nonCompliant.length > 0) {
        console.warn(`✗ ${test.name}: ${nonCompliant.length}/${count} undersized`);
        nonCompliant.forEach(r => {
          console.warn(
            `  - ${r.height}×${r.width}px (needs ${r.minRequired}×${r.minRequired}px)`
          );
        });
      }

      expect(nonCompliant.length).toBe(0);
    }
  });

  test('should validate form input touch targets', async ({ page }) => {
    await page.goto('/contact');

    const formTests = [
      { selector: 'input[type="text"]', name: 'Text inputs' },
      { selector: 'input[type="email"]', name: 'Email inputs' },
      { selector: 'textarea', name: 'Text areas' },
      { selector: 'input[type="checkbox"]', name: 'Checkboxes' },
      { selector: 'input[type="radio"]', name: 'Radio buttons' },
    ];

    for (const test of formTests) {
      const { results, count, skipped } = await checkTouchTarget(
        page,
        test.selector,
        test.name
      );

      if (skipped) {
        console.log(`✓ ${test.name}: No elements found (skipped)`);
        continue;
      }

      const nonCompliant = results.filter(r => !r.compliant);
      if (nonCompliant.length > 0) {
        console.warn(`✗ ${test.name}: ${nonCompliant.length}/${count} undersized`);
        nonCompliant.forEach(r => {
          console.warn(
            `  - ${r.height}×${r.width}px (needs ${r.minRequired}×${r.minRequired}px)`
          );
        });
      }

      expect(nonCompliant.length).toBe(0);
    }
  });

  test('should validate link touch targets', async ({ page }) => {
    await page.goto('/');

    const linkTests = [
      { selector: '.nav-link', name: 'Navigation links' },
      { selector: '.resource-link', name: 'Resource links' },
      { selector: 'a.social-link', name: 'Social links' },
      { selector: '.resources-nav-links a', name: 'Resource nav links' },
    ];

    for (const test of linkTests) {
      const { results, count, skipped } = await checkTouchTarget(
        page,
        test.selector,
        test.name
      );

      if (skipped) {
        console.log(`✓ ${test.name}: No elements found (skipped)`);
        continue;
      }

      const nonCompliant = results.filter(r => !r.compliant);
      if (nonCompliant.length > 0) {
        console.warn(`✗ ${test.name}: ${nonCompliant.length}/${count} undersized`);
        nonCompliant.forEach(r => {
          console.warn(
            `  - ${r.height}×${r.width}px (needs ${r.minRequired}×${r.minRequired}px)`
          );
        });
      }

      expect(nonCompliant.length).toBe(0);
    }
  });

  test('should validate accordion/expand controls', async ({ page }) => {
    await page.goto('/');

    const expandTests = [
      { selector: '.accordion-header', name: 'Accordion headers' },
      { selector: '.critics-corner-header', name: 'Critics corner header' },
      { selector: '.laymans-terms-header', name: 'Laymans terms header' },
    ];

    for (const test of expandTests) {
      const { results, count, skipped } = await checkTouchTarget(
        page,
        test.selector,
        test.name
      );

      if (skipped) {
        console.log(`✓ ${test.name}: No elements found (skipped)`);
        continue;
      }

      const nonCompliant = results.filter(r => !r.compliant);
      if (nonCompliant.length > 0) {
        console.warn(`✗ ${test.name}: ${nonCompliant.length}/${count} undersized`);
        nonCompliant.forEach(r => {
          console.warn(
            `  - ${r.height}×${r.width}px (needs ${r.minRequired}×${r.minRequired}px)`
          );
        });
      }

      expect(nonCompliant.length).toBe(0);
    }
  });

  test('should validate mobile menu button', async ({ page }) => {
    await page.goto('/');

    // Mobile menu toggle is Quarto's navbar-toggler (the custom
    // .mobile-menu-toggle was removed in #3327).
    const { results, count } = await checkTouchTarget(
      page,
      '.navbar-toggler',
      'Mobile menu buttons'
    );

    if (count === 0) {
      console.log('✓ Mobile menu buttons: Not found on desktop');
      return;
    }

    const nonCompliant = results.filter(r => !r.compliant);
    if (nonCompliant.length > 0) {
      console.warn(`✗ Mobile menu buttons: ${nonCompliant.length}/${count} undersized`);
      nonCompliant.forEach(r => {
        console.warn(
          `  - ${r.height}×${r.width}px (needs ${r.minRequired}×${r.minRequired}px)`
        );
      });
    }

    expect(nonCompliant.length).toBe(0);
  });

  test('should provide summary of all compliant elements', async ({ page }) => {
    await page.goto('/');

    const allTests = [
      { selector: 'button', name: 'All buttons' },
      { selector: 'a', name: 'All links' },
      { selector: 'input', name: 'All inputs' },
    ];

    const summary = {
      total: 0,
      compliant: 0,
      nonCompliant: 0,
      details: [],
    };

    for (const test of allTests) {
      const { results, count, skipped } = await checkTouchTarget(
        page,
        test.selector,
        test.name
      );

      if (skipped) continue;

      const compliant = results.filter(r => r.compliant).length;
      const nonCompliant = results.filter(r => !r.compliant).length;

      summary.total += count;
      summary.compliant += compliant;
      summary.nonCompliant += nonCompliant;
      summary.details.push({
        type: test.name,
        total: count,
        compliant,
        nonCompliant,
      });
    }

    console.log('\n=== Touch Target Compliance Summary ===');
    console.log(`Total interactive elements: ${summary.total}`);
    console.log(`Compliant (≥44×44px): ${summary.compliant}`);
    console.log(`Non-compliant: ${summary.nonCompliant}`);
    console.log('');
    summary.details.forEach(detail => {
      console.log(
        `${detail.type}: ${detail.compliant}/${detail.total} compliant`
      );
    });

    // All interactive elements should be compliant
    expect(summary.nonCompliant).toBe(0);
  });
});
