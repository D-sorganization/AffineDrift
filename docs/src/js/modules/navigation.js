/**
 * Navigation Module
 * Handles smooth scrolling, TOC highlighting, and navigation interactions
 */

import { debounce, smoothScrollTo, getScrollOffset } from './utils.js';

/**
 * Setup smooth scrolling for anchor links
 */
export function setupSmoothScrolling() {
  const offset = getScrollOffset();

  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener('click', function (e) {
      const href = this.getAttribute('href');
      
      // Skip if it's just "#"
      if (href === '#') return;

      const targetId = href.substring(1);
      const targetElement = document.getElementById(targetId);

      if (targetElement) {
        e.preventDefault();
        smoothScrollTo(targetElement, offset);
        
        // Update URL without jumping
        history.pushState(null, null, href);
      }
    });
  });
}

/**
 * Highlight active section in TOC
 */
export function setupTocHighlighting() {
  const toc = document.getElementById('TOC');
  if (!toc) return;

  const tocLinks = toc.querySelectorAll('a[href^="#"]');
  if (tocLinks.length === 0) return;

  const sections = Array.from(tocLinks).map((link) => {
    const href = link.getAttribute('href');
    const id = href.substring(1);
    return document.getElementById(id);
  }).filter(Boolean);

  if (sections.length === 0) return;

  const updateActiveSection = debounce(() => {
    const scrollPosition = window.pageYOffset + 150;

    let activeSection = null;
    for (const section of sections) {
      const sectionTop = section.offsetTop;
      if (scrollPosition >= sectionTop) {
        activeSection = section;
      }
    }

    // Remove all active classes
    tocLinks.forEach((link) => link.classList.remove('active'));

    // Add active class to current section
    if (activeSection) {
      const activeLink = toc.querySelector(`a[href="#${activeSection.id}"]`);
      if (activeLink) {
        activeLink.classList.add('active');
      }
    }
  }, 100);

  window.addEventListener('scroll', updateActiveSection);
  updateActiveSection(); // Initial call
}

/**
 * Setup navigation menu interactions
 */
export function setupNavigationMenu() {
  // Mobile menu toggle
  const menuToggle = document.querySelector('.navbar-toggler, .menu-toggle');
  const navMenu = document.querySelector('.navbar-collapse, .nav-menu');

  if (menuToggle && navMenu) {
    menuToggle.addEventListener('click', () => {
      navMenu.classList.toggle('show');
      const isExpanded = navMenu.classList.contains('show');
      menuToggle.setAttribute('aria-expanded', isExpanded);
    });
  }

  // Close menu when clicking outside
  document.addEventListener('click', (e) => {
    if (navMenu && navMenu.classList.contains('show')) {
      if (!navMenu.contains(e.target) && !menuToggle.contains(e.target)) {
        navMenu.classList.remove('show');
        menuToggle.setAttribute('aria-expanded', 'false');
      }
    }
  });
}

/**
 * Setup back to top button
 */
export function setupBackToTop() {
  const backToTopButton = document.querySelector('.back-to-top');
  if (!backToTopButton) return;

  const toggleVisibility = debounce(() => {
    if (window.pageYOffset > 300) {
      backToTopButton.classList.add('visible');
    } else {
      backToTopButton.classList.remove('visible');
    }
  }, 100);

  window.addEventListener('scroll', toggleVisibility);

  backToTopButton.addEventListener('click', (e) => {
    e.preventDefault();
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  });
}
