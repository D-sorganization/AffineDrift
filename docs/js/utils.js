/**
 * AffineDrift - Core Utilities Module
 * Shared utility functions used across all modules
 */

// Constants for scroll offsets
export const MAX_ID_GENERATION_ATTEMPTS = 100;
export const MATHJAX_RENDER_DELAY_MS = 100;
export const CRITICS_CORNER_PADDING_OFFSET = 50;

// Lazy initialize to avoid synchronous layout thrashing
export let HEADER_OFFSET = 140;
export let TOC_SCROLL_OFFSET = 140;

/**
 * Get scroll offset from CSS variable
 * @returns {number} Scroll offset value
 */
export const getScrollOffset = () => {
    if (typeof window !== "undefined") {
        const value = getComputedStyle(document.documentElement).getPropertyValue(
            "--scroll-offset"
        );
        return value ? parseInt(value) : 140;
    }
    return 140;
};

/**
 * Run callback when DOM is ready
 * @param {Function} callback - Function to run
 */
export const runOnDomReady = (callback) => {
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", callback);
    } else {
        callback();
    }
};

/**
 * Debounce function to limit event handler calls
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
 * Run non-critical tasks when browser is idle
 * @param {Function} callback - Function to run when idle
 */
export function runWhenIdle(callback) {
    if (typeof requestIdleCallback !== "undefined") {
        requestIdleCallback(callback);
    } else {
        setTimeout(callback, 0);
    }
}

/**
 * Generate unique ID for element
 * @param {string} text - Base text for ID
 * @param {Set} usedIds - Set of already used IDs
 * @returns {string} Unique ID
 */
export function generateUniqueId(text, usedIds) {
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

    while (exists(id) && counter < MAX_ID_GENERATION_ATTEMPTS) {
        id = `${baseId}-${counter}`;
        counter++;
    }

    if (usedIds.has(id)) {
        id = `${baseId}-${Date.now()}`;
    }

    return id;
}

/**
 * Scroll to top of page smoothly
 */
export function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: "smooth",
    });
}

/**
 * Update offset values from CSS variables
 */
export function updateOffsets() {
    HEADER_OFFSET = getScrollOffset();
    TOC_SCROLL_OFFSET = HEADER_OFFSET;
}
