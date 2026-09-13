const {
  generateTableOfContents,
  initScrollSpy,
  initSmoothScroll,
  getDocumentOffsetTop,
  patchTocSectionsOffsetTop,
} = require('../js/navigation.js');


describe('generated table of contents', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
  });

  test('does not duplicate an authored table of contents', () => {
    document.body.innerHTML = `
      <aside class="left-sidebar">
        <nav class="toc-nav"><ul><li><a href="#overview">Overview</a></li></ul></nav>
      </aside>
      <main><section id="overview"><h2>Overview</h2></section></main>
    `;

    generateTableOfContents();

    expect(document.querySelectorAll('.toc-nav')).toHaveLength(1);
    expect(document.querySelectorAll('.sidebar-toc')).toHaveLength(0);
  });
});

describe('nested positioned sections and document-relative TOC highlighting (issue #4370)', () => {
  let originalInnerHeight;
  let originalInnerWidth;

  beforeEach(() => {
    document.body.innerHTML = '';
    document.documentElement.removeAttribute('data-theme');
    originalInnerHeight = window.innerHeight;
    originalInnerWidth = window.innerWidth;
    window.innerHeight = 800;
    window.innerWidth = 1440;
    window.pageYOffset = 0;
    window.scrollY = 0;
    window.scrollTo = jest.fn((options) => {
      if (typeof options === 'object' && options !== null && typeof options.top === 'number') {
        window.pageYOffset = options.top;
        window.scrollY = options.top;
      }
    });
  });

  afterEach(() => {
    window.innerHeight = originalInnerHeight;
    window.innerWidth = originalInnerWidth;
  });

  function setupChapter16Fixture() {
    document.body.innerHTML = `
      <nav id="TOC" role="doc-toc" class="toc-active">
        <h2 id="toc-title">On this page</h2>
        <ul>
          <li><a id="link-early" href="#sec-early" data-scroll-target="#sec-early">Early Section</a></li>
          <li><a id="link-jacobian" href="#sec-muscle-jacobian" data-scroll-target="#sec-muscle-jacobian">The Muscle Jacobian</a></li>
          <li><a id="link-grip-forces" href="#sec-grip-forces" data-scroll-target="#sec-grip-forces">The Golf Grip</a>
            <ul>
              <li><a id="link-grip-impact" href="#grip-stiffness-and-impact" data-scroll-target="#grip-stiffness-and-impact">Grip Stiffness and Impact</a></li>
            </ul>
          </li>
        </ul>
      </nav>
      <main id="quarto-document-content">
        <section id="sec-early">
          <h2>Early Section</h2>
        </section>
        <section id="sec-muscle-jacobian">
          <h2>The Muscle Jacobian: From Muscle Space to Joint Space</h2>
        </section>
        <section id="sec-grip-forces" class="level2" style="position: relative;">
          <h2>Practical Example: The Golf Grip</h2>
          <section id="grip-stiffness-and-impact" class="level3">
            <h3>Grip Stiffness and Impact</h3>
          </section>
        </section>
      </main>
    `;

    const secEarly = document.getElementById('sec-early');
    const secJacobian = document.getElementById('sec-muscle-jacobian');
    const secGripForces = document.getElementById('sec-grip-forces');
    const secGripImpact = document.getElementById('grip-stiffness-and-impact');

    // Simulate real browser layout:
    // secEarly is at document Y = 500
    // secJacobian is at document Y = 2000
    // secGripForces is at document Y = 16243
    // secGripImpact is nested in secGripForces with parent-relative offsetTop = 2037 (doc Y = 18280)
    Object.defineProperty(secEarly, 'offsetParent', { value: document.body, configurable: true });
    Object.defineProperty(secEarly, 'offsetTop', { value: 500, configurable: true, writable: true });
    secEarly.getBoundingClientRect = () => {
      const scrollY = window.pageYOffset || 0;
      return { top: 500 - scrollY, bottom: 1200 - scrollY, height: 700, width: 800, left: 0, right: 800 };
    };

    Object.defineProperty(secJacobian, 'offsetParent', { value: document.body, configurable: true });
    Object.defineProperty(secJacobian, 'offsetTop', { value: 2000, configurable: true, writable: true });
    secJacobian.getBoundingClientRect = () => {
      const scrollY = window.pageYOffset || 0;
      return { top: 2000 - scrollY, bottom: 4000 - scrollY, height: 2000, width: 800, left: 0, right: 800 };
    };

    Object.defineProperty(secGripForces, 'offsetParent', { value: document.body, configurable: true });
    Object.defineProperty(secGripForces, 'offsetTop', { value: 16243, configurable: true, writable: true });
    secGripForces.getBoundingClientRect = () => {
      const scrollY = window.pageYOffset || 0;
      return { top: 16243 - scrollY, bottom: 22000 - scrollY, height: 5757, width: 800, left: 0, right: 800 };
    };

    Object.defineProperty(secGripImpact, 'offsetParent', { value: secGripForces, configurable: true });
    Object.defineProperty(secGripImpact, 'offsetTop', { value: 2037, configurable: true, writable: true });
    secGripImpact.getBoundingClientRect = () => {
      const scrollY = window.pageYOffset || 0;
      return { top: 18280 - scrollY, bottom: 20000 - scrollY, height: 1720, width: 800, left: 0, right: 800 };
    };

    return { secEarly, secJacobian, secGripForces, secGripImpact };
  }

  test('reproduces premature selection defect when using raw offsetTop on nested sections', () => {
    const { secEarly, secJacobian, secGripForces, secGripImpact } = setupChapter16Fixture();
    const sections = [secEarly, secJacobian, secGripForces, secGripImpact];
    const sectionMargin = 200;

    // Simulate Quarto's native unpatched updateActiveLink at scroll position 2000
    // (user viewing "The Muscle Jacobian: From Muscle Space to Joint Space")
    window.pageYOffset = 2000;

    const unpatchedSectionIndex = [...sections].reverse().findIndex((section) => {
      return window.pageYOffset >= section.offsetTop - sectionMargin;
    });
    const unpatchedCurrent = sections.length - unpatchedSectionIndex - 1;

    // With raw offsetTop, secGripImpact has offsetTop = 2037 <= 2000 + 200 = 2200,
    // so reverse().findIndex matches secGripImpact (index 3) instead of secJacobian (index 1)!
    expect(unpatchedCurrent).toBe(3);
    expect(sections[unpatchedCurrent].id).toBe('grip-stiffness-and-impact');
  });

  test('patchTocSectionsOffsetTop calculates true document-relative offsetTop', () => {
    const { secEarly, secJacobian, secGripForces, secGripImpact } = setupChapter16Fixture();
    const sections = [secEarly, secJacobian, secGripForces, secGripImpact];

    patchTocSectionsOffsetTop(sections);

    expect(secEarly.offsetTop).toBe(500);
    expect(secJacobian.offsetTop).toBe(2000);
    expect(secGripForces.offsetTop).toBe(16243);
    // Nested child offsetTop is now document-relative (18280), not parent-relative (2037)
    expect(secGripImpact.offsetTop).toBe(18280);
  });

  test('Quarto vendor algorithm selects correct middle section after offsetTop is patched', () => {
    const { secEarly, secJacobian, secGripForces, secGripImpact } = setupChapter16Fixture();
    const sections = [secEarly, secJacobian, secGripForces, secGripImpact];
    const sectionMargin = 200;

    patchTocSectionsOffsetTop(sections);

    // Scroll to The Muscle Jacobian (top 2000)
    window.pageYOffset = 2000;

    const patchedSectionIndex = [...sections].reverse().findIndex((section) => {
      return window.pageYOffset >= section.offsetTop - sectionMargin;
    });
    const patchedCurrent = sections.length - patchedSectionIndex - 1;

    // Now reverse().findIndex correctly skips grip-stiffness-and-impact (18280)
    // and selects The Muscle Jacobian (index 1)!
    expect(patchedCurrent).toBe(1);
    expect(sections[patchedCurrent].id).toBe('sec-muscle-jacobian');
  });

  test('settles active selection at early, middle, and late headings with ARIA attributes', () => {
    jest.useFakeTimers();
    try {
      setupChapter16Fixture();
      initScrollSpy();

      const linkEarly = document.getElementById('link-early');
      const linkJacobian = document.getElementById('link-jacobian');
      const linkGripImpact = document.getElementById('link-grip-impact');

      // 1. Early heading (Y = 500)
      window.pageYOffset = 500;
      window.dispatchEvent(new Event('scroll'));
      jest.advanceTimersByTime(20);

      expect(linkEarly.classList.contains('active')).toBe(true);
      expect(linkEarly.getAttribute('aria-current')).toBe('location');
      expect(linkJacobian.classList.contains('active')).toBe(false);
      expect(linkGripImpact.classList.contains('active')).toBe(false);

      // 2. Middle heading (Y = 2000) - Chapter 16 Muscle Jacobian route
      window.pageYOffset = 2000;
      window.dispatchEvent(new Event('scroll'));
      jest.advanceTimersByTime(20);

      expect(linkJacobian.classList.contains('active')).toBe(true);
      expect(linkJacobian.getAttribute('aria-current')).toBe('location');
      expect(linkEarly.classList.contains('active')).toBe(false);
      expect(linkEarly.hasAttribute('aria-current')).toBe(false);
      expect(linkGripImpact.classList.contains('active')).toBe(false);
      expect(linkGripImpact.hasAttribute('aria-current')).toBe(false);

      // 3. Late heading (Y = 18300) - Grip Stiffness and Impact
      window.pageYOffset = 18300;
      window.dispatchEvent(new Event('scroll'));
      jest.advanceTimersByTime(20);

      expect(linkGripImpact.classList.contains('active')).toBe(true);
      expect(linkGripImpact.getAttribute('aria-current')).toBe('location');
      expect(linkJacobian.classList.contains('active')).toBe(false);
      expect(linkJacobian.hasAttribute('aria-current')).toBe(false);
    } finally {
      jest.useRealTimers();
    }
  });

  test('functions identically under light and dark themes', () => {
    setupChapter16Fixture();

    const linkJacobian = document.getElementById('link-jacobian');
    const linkGripImpact = document.getElementById('link-grip-impact');

    for (const theme of ['light', 'dark']) {
      document.documentElement.setAttribute('data-theme', theme);
      initScrollSpy();

      window.pageYOffset = 2000;
      window.dispatchEvent(new Event('scroll'));

      expect(linkJacobian.classList.contains('active')).toBe(true);
      expect(linkJacobian.getAttribute('aria-current')).toBe('location');
      expect(linkGripImpact.classList.contains('active')).toBe(false);
    }
  });

  test('functions accurately in narrow viewport', () => {
    setupChapter16Fixture();
    window.innerWidth = 375;
    window.innerHeight = 667;

    initScrollSpy();

    const linkJacobian = document.getElementById('link-jacobian');
    const linkGripImpact = document.getElementById('link-grip-impact');

    window.pageYOffset = 2000;
    window.dispatchEvent(new Event('scroll'));

    expect(linkJacobian.classList.contains('active')).toBe(true);
    expect(linkJacobian.getAttribute('aria-current')).toBe('location');
    expect(linkGripImpact.classList.contains('active')).toBe(false);
  });

  test('maintains keyboard navigation and anchor destinations intact', () => {
    setupChapter16Fixture();
    initSmoothScroll();
    initScrollSpy();

    const linkJacobian = document.getElementById('link-jacobian');
    const targetSection = document.getElementById('sec-muscle-jacobian');

    // Click anchor link
    linkJacobian.click();

    // Target section receives programmatic focus and target-highlight
    expect(targetSection.getAttribute('tabindex')).toBe('-1');
    expect(targetSection.classList.contains('target-highlight')).toBe(true);
  });

  test('is idempotent across repeated calls', () => {
    const { secGripImpact } = setupChapter16Fixture();

    initScrollSpy();
    initScrollSpy();
    initScrollSpy();

    expect(secGripImpact.offsetTop).toBe(18280);
  });
});


