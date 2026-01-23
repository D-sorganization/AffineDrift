/**
 * AffineDrift Startup Launcher
 * Professional startup experience with splash screen, performance metrics,
 * skeleton loading, and smooth transitions.
 *
 * Features:
 * - Branded splash screen with logo animation
 * - Progress indicator with real loading states
 * - Performance timing metrics (First Paint, Time to Interactive)
 * - Skeleton loading placeholders
 * - Smooth page reveal transitions
 * - Reduced motion support
 * - Startup optimization hints
 */

(function () {
  'use strict';

  // Configuration
  const CONFIG = {
    MINIMUM_SPLASH_DURATION: 800,    // Minimum time to show splash (ms)
    MAXIMUM_SPLASH_DURATION: 5000,   // Maximum time before force-hiding splash (ms)
    PROGRESS_ANIMATION_SPEED: 50,    // Progress bar animation interval (ms)
    ENABLE_METRICS: true,            // Log performance metrics to console
    ENABLE_SKELETON: true,           // Enable skeleton loading placeholders
    SPLASH_FADE_DURATION: 400,       // Splash screen fade out duration (ms)
    DEBUG_MODE: false                // Enable verbose logging
  };

  // Performance metrics storage
  const metrics = {
    navigationStart: 0, // performance.now() is relative to navigation start
    splashShown: null,
    domContentLoaded: null,
    resourcesLoaded: null,
    firstPaint: null,
    firstContentfulPaint: null,
    timeToInteractive: null,
    splashHidden: null,
    fullyLoaded: null
  };

  // State management
  const state = {
    splashElement: null,
    progressElement: null,
    progressValue: 0,
    targetProgress: 0,
    isReady: false,
    resourcesLoaded: false,
    domReady: false,
    criticalResourcesLoaded: false,
    progressInterval: null
  };

  // Check for reduced motion preference
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /**
   * Initialize the startup launcher
   * This runs immediately when the script loads
   */
  function init() {
    metrics.splashShown = performance.now();

    // Create and inject splash screen immediately
    createSplashScreen();

    // Start progress animation
    startProgressAnimation();

    // Set up event listeners
    setupEventListeners();

    // Capture paint timing
    capturePaintMetrics();

    // Set up skeleton loading if enabled
    if (CONFIG.ENABLE_SKELETON) {
      setupSkeletonLoading();
    }

    // Safety timeout - hide splash after maximum duration
    setTimeout(forceHideSplash, CONFIG.MAXIMUM_SPLASH_DURATION);

    log('Startup launcher initialized');
  }

  /**
   * Create the splash screen DOM structure
   */
  function createSplashScreen() {
    // Don't create if already exists
    if (document.getElementById('ad-splash-screen')) {
      state.splashElement = document.getElementById('ad-splash-screen');
      state.progressElement = document.getElementById('ad-splash-progress-bar');
      return;
    }

    const splash = document.createElement('div');
    splash.id = 'ad-splash-screen';
    splash.className = 'ad-splash-screen';
    splash.setAttribute('role', 'progressbar');
    splash.setAttribute('aria-label', 'Loading AffineDrift');
    splash.setAttribute('aria-valuenow', '0');
    splash.setAttribute('aria-valuemin', '0');
    splash.setAttribute('aria-valuemax', '100');

    splash.innerHTML = `
      <div class="ad-splash-content">
        <div class="ad-splash-logo-container">
          <div class="ad-splash-logo">
            <svg class="ad-splash-logo-svg" viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
              <!-- Outer ring - rotates -->
              <circle class="ad-splash-ring ad-splash-ring-outer" cx="60" cy="60" r="54" fill="none" stroke-width="2"/>
              <!-- Inner ring - counter-rotates -->
              <circle class="ad-splash-ring ad-splash-ring-inner" cx="60" cy="60" r="42" fill="none" stroke-width="2"/>
              <!-- Center dot - pulses -->
              <circle class="ad-splash-center-dot" cx="60" cy="60" r="8"/>
              <!-- Dynamic path - draws in -->
              <path class="ad-splash-path" d="M30 90 Q60 30 90 90" fill="none" stroke-width="3"/>
            </svg>
          </div>
          <h1 class="ad-splash-title">AffineDrift</h1>
          <p class="ad-splash-tagline">Control Theory Meets Biomechanics</p>
        </div>

        <div class="ad-splash-progress-container">
          <div class="ad-splash-progress-track">
            <div class="ad-splash-progress-bar" id="ad-splash-progress-bar"></div>
          </div>
          <div class="ad-splash-status" id="ad-splash-status">Initializing...</div>
        </div>

        <div class="ad-splash-hints" id="ad-splash-hints">
          <span class="ad-splash-hint">Loading resources</span>
        </div>
      </div>
    `;

    // Insert at the very beginning of body
    if (document.body) {
      document.body.prepend(splash);
    } else {
      // If body not ready, wait for it
      document.addEventListener('DOMContentLoaded', function () {
        document.body.prepend(splash);
      });
    }

    state.splashElement = splash;
    state.progressElement = splash.querySelector('#ad-splash-progress-bar');

    // Add body class to prevent scrolling during splash
    document.documentElement.classList.add('ad-splash-active');

    log('Splash screen created');
  }

  /**
   * Set up event listeners for tracking load progress
   */
  function setupEventListeners() {
    // DOM Content Loaded
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', onDOMContentLoaded);
    } else {
      onDOMContentLoaded();
    }

    // Window Load (all resources)
    if (document.readyState === 'complete') {
      onWindowLoad();
    } else {
      window.addEventListener('load', onWindowLoad);
    }

    // Track critical resources (fonts, CSS)
    trackCriticalResources();
  }

  /**
   * Handle DOM Content Loaded event
   */
  function onDOMContentLoaded() {
    metrics.domContentLoaded = performance.now();
    state.domReady = true;
    updateProgress(40, 'Preparing content...');
    log('DOM Content Loaded', metrics.domContentLoaded - metrics.navigationStart, 'ms');
    checkReadyState();
  }

  /**
   * Handle Window Load event
   */
  function onWindowLoad() {
    metrics.resourcesLoaded = performance.now();
    state.resourcesLoaded = true;
    updateProgress(80, 'Finalizing...');
    log('All resources loaded', metrics.resourcesLoaded - metrics.navigationStart, 'ms');
    checkReadyState();
  }

  /**
   * Track critical resources (fonts, stylesheets)
   */
  function trackCriticalResources() {
    // Check for font loading
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(function () {
        state.criticalResourcesLoaded = true;
        updateProgress(60, 'Loading fonts...');
        log('Fonts loaded');
        checkReadyState();
      });
    } else {
      // Fallback for browsers without font loading API
      state.criticalResourcesLoaded = true;
    }
  }

  /**
   * Capture paint timing metrics
   */
  function capturePaintMetrics() {
    if (window.PerformanceObserver) {
      try {
        const paintObserver = new PerformanceObserver(function (list) {
          for (const entry of list.getEntries()) {
            if (entry.name === 'first-paint') {
              metrics.firstPaint = entry.startTime;
              log('First Paint:', metrics.firstPaint.toFixed(2), 'ms');
            }
            if (entry.name === 'first-contentful-paint') {
              metrics.firstContentfulPaint = entry.startTime;
              log('First Contentful Paint:', metrics.firstContentfulPaint.toFixed(2), 'ms');
            }
          }
        });
        paintObserver.observe({ entryTypes: ['paint'] });
      } catch (e) {
        log('Paint observer not supported');
      }
    }
  }

  /**
   * Start the progress bar animation
   */
  function startProgressAnimation() {
    // Initial progress
    state.progressValue = 0;
    state.targetProgress = 20;

    state.progressInterval = setInterval(function () {
      if (state.progressValue < state.targetProgress) {
        // Smooth easing toward target
        const diff = state.targetProgress - state.progressValue;
        const increment = Math.max(0.5, diff * 0.1);
        state.progressValue = Math.min(state.progressValue + increment, state.targetProgress);

        if (state.progressElement) {
          state.progressElement.style.width = state.progressValue + '%';
        }

        if (state.splashElement) {
          state.splashElement.setAttribute('aria-valuenow', Math.round(state.progressValue));
        }
      }
    }, CONFIG.PROGRESS_ANIMATION_SPEED);
  }

  /**
   * Update progress to a new target value
   */
  function updateProgress(target, statusText) {
    // Only update status and progress if we're moving forward
    if (target > state.targetProgress) {
      state.targetProgress = target;

      const statusElement = document.getElementById('ad-splash-status');
      if (statusElement && statusText) {
        statusElement.textContent = statusText;
      }
    }
  }

  /**
   * Check if we're ready to hide the splash screen
   */
  function checkReadyState() {
    if (state.domReady && state.resourcesLoaded && state.criticalResourcesLoaded) {
      updateProgress(100, 'Ready!');

      // Ensure minimum splash duration for branding
      const elapsed = performance.now() - metrics.splashShown;
      const remainingTime = Math.max(0, CONFIG.MINIMUM_SPLASH_DURATION - elapsed);

      setTimeout(hideSplash, remainingTime);
    }
  }

  /**
   * Hide the splash screen with animation
   */
  function hideSplash() {
    if (!state.splashElement || state.splashElement.classList.contains('ad-splash-hidden')) {
      return;
    }

    metrics.splashHidden = performance.now();
    metrics.timeToInteractive = metrics.splashHidden - metrics.navigationStart;

    // Clear progress interval
    if (state.progressInterval) {
      clearInterval(state.progressInterval);
    }

    // Add exit animation class
    state.splashElement.classList.add('ad-splash-exit');

    // Handle reduced motion
    const fadeDuration = prefersReducedMotion ? 0 : CONFIG.SPLASH_FADE_DURATION;

    setTimeout(function () {
      state.splashElement.classList.add('ad-splash-hidden');
      document.documentElement.classList.remove('ad-splash-active');

      // Trigger page reveal animation
      revealPage();

      // Log final metrics
      logFinalMetrics();

      // Clean up splash screen from DOM after animation
      setTimeout(function () {
        if (state.splashElement && state.splashElement.parentNode) {
          state.splashElement.parentNode.removeChild(state.splashElement);
        }
      }, 500);
    }, fadeDuration);

    log('Splash hidden after', metrics.timeToInteractive.toFixed(2), 'ms');
  }

  /**
   * Force hide splash screen (safety timeout)
   */
  function forceHideSplash() {
    if (!state.splashElement || state.splashElement.classList.contains('ad-splash-hidden')) {
      return;
    }
    log('Force hiding splash screen (timeout)');
    hideSplash();
  }

  /**
   * Trigger page reveal animation
   */
  function revealPage() {
    state.isReady = true;
    document.documentElement.classList.add('ad-page-revealed');

    // Dispatch custom event for other scripts
    const event = new CustomEvent('affinedrift:ready', {
      detail: {
        metrics: { ...metrics },
        loadTime: metrics.timeToInteractive
      }
    });
    document.dispatchEvent(event);
  }

  /**
   * Set up skeleton loading placeholders
   */
  function setupSkeletonLoading() {
    // Add skeleton class to main content areas
    document.addEventListener('DOMContentLoaded', function () {
      const contentAreas = document.querySelectorAll(
        '.main-content-area, #quarto-document-content, .home-content'
      );

      contentAreas.forEach(function (area) {
        if (!area.classList.contains('ad-skeleton-ready')) {
          area.classList.add('ad-skeleton-container');
        }
      });

      // Remove skeleton loading after page is revealed
      document.addEventListener('affinedrift:ready', function () {
        contentAreas.forEach(function (area) {
          area.classList.remove('ad-skeleton-container');
          area.classList.add('ad-skeleton-ready');
        });
      });
    });
  }

  /**
   * Log final performance metrics
   */
  function logFinalMetrics() {
    if (!CONFIG.ENABLE_METRICS) return;

    metrics.fullyLoaded = performance.now();

    const summary = {
      'Navigation Start to DOM Ready': metrics.domContentLoaded ? (metrics.domContentLoaded - metrics.navigationStart).toFixed(2) + 'ms' : 'N/A',
      'Navigation Start to All Resources': metrics.resourcesLoaded ? (metrics.resourcesLoaded - metrics.navigationStart).toFixed(2) + 'ms' : 'N/A',
      'Time to Interactive': metrics.timeToInteractive.toFixed(2) + 'ms',
      'First Paint': metrics.firstPaint ? metrics.firstPaint.toFixed(2) + 'ms' : 'N/A',
      'First Contentful Paint': metrics.firstContentfulPaint ? metrics.firstContentfulPaint.toFixed(2) + 'ms' : 'N/A',
      'Splash Duration': (metrics.splashHidden - metrics.splashShown).toFixed(2) + 'ms'
    };

    console.group('%c AffineDrift Performance Metrics', 'color: #3282b8; font-weight: bold;');
    Object.entries(summary).forEach(function ([key, value]) {
      console.log(`%c${key}: %c${value}`, 'color: #666;', 'color: #0f4c75; font-weight: bold;');
    });
    console.groupEnd();

    // Store metrics in window for debugging
    window.AffineDriftMetrics = { ...metrics, summary };
  }

  /**
   * Debug logging helper
   */
  function log(...args) {
    if (CONFIG.DEBUG_MODE) {
      console.log('[AffineDrift Startup]', ...args);
    }
  }

  // Expose API for external use
  window.AffineDriftStartup = {
    getMetrics: function () { return { ...metrics }; },
    isReady: function () { return state.isReady; },
    forceHide: forceHideSplash
  };

  // Initialize immediately
  init();

})();
