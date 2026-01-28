/**
 * Utility Functions Module
 * Common helper functions used throughout the application
 */

/**
 * Debounce function execution
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
export function debounce(func, wait) {
  let timeout;
  return function (...args) {
    const context = this;
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(context, args), wait);
  };
}

/**
 * Run callback when DOM is ready
 * @param {Function} callback - Function to execute
 */
export function runOnDomReady(callback) {
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", callback);
  } else {
    callback();
  }
}

/**
 * Run non-critical tasks when idle
 * @param {Function} callback - Function to execute
 */
export function runWhenIdle(callback) {
  if (typeof requestIdleCallback !== "undefined") {
    requestIdleCallback(callback);
  } else {
    setTimeout(callback, 0);
  }
}

/**
 * Get scroll offset from CSS variable
 * @returns {number} Scroll offset in pixels
 */
export function getScrollOffset() {
  if (typeof window !== "undefined") {
    const value = getComputedStyle(document.documentElement).getPropertyValue(
      "--scroll-offset",
    );
    return value ? parseInt(value) : 140;
  }
  return 140;
}

/**
 * Generate unique ID from text
 * @param {string} text - Text to convert to ID
 * @param {Set} usedIds - Set of already used IDs
 * @returns {string} Unique ID
 */
export function generateUniqueId(text, usedIds) {
  const MAX_ATTEMPTS = 100;
  
  let baseId = text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
  
  if (!baseId) baseId = "section";

  let id = baseId;
  let counter = 1;

  const exists = (candidateId) => {
    return (
      usedIds.has(candidateId) || document.getElementById(candidateId) !== null
    );
  };

  if (!exists(id)) {
    return id;
  }

  while (exists(id) && counter < MAX_ATTEMPTS) {
    id = `${baseId}-${counter}`;
    counter++;
  }

  if (usedIds.has(id)) {
    id = `${baseId}-${Date.now()}`;
  }

  return id;
}

/**
 * Smooth scroll to element
 * @param {HTMLElement} element - Element to scroll to
 * @param {number} offset - Offset from top in pixels
 */
export function smoothScrollTo(element, offset = 140) {
  const targetPosition = element.getBoundingClientRect().top + window.pageYOffset - offset;
  
  window.scrollTo({
    top: targetPosition,
    behavior: 'smooth'
  });
}
