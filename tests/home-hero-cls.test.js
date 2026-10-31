/**
 * Tests for Home Page CLS Prevention (#5192).
 * Verifies that index.qmd and css/components/home-hero.css declare explicit
 * image dimensions and CSS aspect-ratio to prevent layout shifts.
 */

const fs = require('fs');
const path = require('path');

const indexQmdPath = path.resolve(__dirname, '../index.qmd');
const homeHeroCssPath = path.resolve(__dirname, '../css/components/home-hero.css');

describe('Home Page Hero Graphic Dimensions and Aspect Ratio Contract (#5192)', () => {
  test('index.qmd specifies width="800" and height="420" on .big-idea-graphic', () => {
    const content = fs.readFileSync(indexQmdPath, 'utf8');
    const imgRegex = /<img[^>]*class="[^"]*big-idea-graphic[^"]*"[^>]*>/;
    const match = content.match(imgRegex);
    expect(match).not.toBeNull();
    const tag = match[0];
    expect(tag).toContain('width="800"');
    expect(tag).toContain('height="420"');
  });

  test('css/components/home-hero.css declares aspect-ratio: 800 / 420 on .big-idea-graphic', () => {
    const css = fs.readFileSync(homeHeroCssPath, 'utf8');
    const ruleRegex = /\.big-idea-graphic\s*\{([^}]+)\}/;
    const match = css.match(ruleRegex);
    expect(match).not.toBeNull();
    const declarations = match[1];
    expect(declarations).toMatch(/aspect-ratio:\s*800\s*\/\s*420/);
  });
});
