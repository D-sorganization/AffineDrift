/**
 * AffineDrift - Main JavaScript Entry Point
 * Modular architecture for better maintainability and testing
 */

import { runOnDomReady, runWhenIdle } from './modules/utils.js';
import { initAriaLabels, addHeadingIds, setupKeyboardNav } from './modules/accessibility.js';
import { 
  setupSmoothScrolling, 
  setupTocHighlighting, 
  setupNavigationMenu,
  setupBackToTop 
} from './modules/navigation.js';
import { initSearch, setupSearchAutocomplete } from './modules/search.js';

/**
 * Initialize all features when DOM is ready
 */
runOnDomReady(() => {
  // Critical features - run immediately
  initAriaLabels();
  addHeadingIds();
  setupKeyboardNav();
  setupSmoothScrolling();
  setupNavigationMenu();

  // Non-critical features - run when idle
  runWhenIdle(() => {
    setupTocHighlighting();
    setupBackToTop();
    initSearch();

    // Load search index if available
    if (window.searchIndex) {
      setupSearchAutocomplete(window.searchIndex);
    }
  });
});

// Export for testing
export {
  initAriaLabels,
  addHeadingIds,
  setupKeyboardNav,
  setupSmoothScrolling,
  setupTocHighlighting,
  setupNavigationMenu,
  setupBackToTop,
  initSearch,
  setupSearchAutocomplete
};
