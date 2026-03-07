/**
 * AffineDrift - Main Entry Point
 * Orchestrates all JavaScript modules
 * 
 * Modularized from monolithic script.js (1740 lines -> 7 focused modules)
 * Each module is under 500 lines with clear separation of concerns
 */

import {
    runOnDomReady,
    runWhenIdle,
    updateOffsets,
    scrollToTop,
    debounce,
    generateUniqueId,
    getScrollOffset,
    MAX_ID_GENERATION_ATTEMPTS,
    MATHJAX_RENDER_DELAY_MS,
    CRITICS_CORNER_PADDING_OFFSET,
} from "./utils.js";

import {
    initSmoothScroll,
    initNavbarCollapse,
    generateTableOfContents,
    initAnchorLinks,
    initScrollSpy,
    initSkipToContent,
} from "./navigation.js";

import {
    initFadeAnimations,
    initLazyImages,
    initAccordions,
    initBackToTop,
    initExportToPdf,
    initLightbox,
    initCriticsCorner,
    initLaymansTermsToggle,
    initCriticsCommentsToggle,
} from "./ui-components.js";

import { updateHistorySidebar, initArticleHistory } from "./history.js";

import {
    initEmailCopy,
    initResponsiveTables,
    initCodeCopy,
    initFormAccessibility,
    initAutoGrowTextareas,
    initContactFormFeedback,
} from "./forms.js";

import {
    initSecureExternalLinks,
    initRepoLinks,
    initAriaLabels,
    initReadingTime,
} from "./accessibility.js";

import { initPDFDownload } from "./pdf.js";

// Main initialization
runOnDomReady(function () {
    // Update offset values from CSS
    updateOffsets();

    // --- Core Navigation ---
    initSmoothScroll();
    initNavbarCollapse();
    generateTableOfContents();
    initAnchorLinks();
    initScrollSpy();
    initSkipToContent();

    // --- Animations & Lazy Loading ---
    initFadeAnimations();
    initLazyImages();

    // --- UI Components ---
    initAccordions();
    initBackToTop();
    initExportToPdf();
    initLightbox();

    // --- External Links ---
    initRepoLinks();
    initSecureExternalLinks();

    // --- Toggle Components ---
    initCriticsCorner();
    initLaymansTermsToggle();
    initCriticsCommentsToggle();

    // --- Forms ---
    initContactFormFeedback();

    // --- Reading Time (articles only) ---
    initReadingTime();

    // --- PDF Download ---
    initPDFDownload();

    // --- Deferred Initialization (non-critical) ---
    runWhenIdle(updateHistorySidebar);
    runWhenIdle(initArticleHistory);
    runWhenIdle(initEmailCopy);
    runWhenIdle(initAutoGrowTextareas);

    runWhenIdle(() => {
        initResponsiveTables();
        initCodeCopy();
        initFormAccessibility();
    });
});

// Initialize ARIA labels
runOnDomReady(initAriaLabels);

// Export for potential module use and backwards compatibility
if (typeof module !== "undefined" && module.exports) {
    module.exports = {
        scrollToTop,
        debounce,
        generateUniqueId,
        getScrollOffset,
        runOnDomReady,
        runWhenIdle,
        MAX_ID_GENERATION_ATTEMPTS,
        MATHJAX_RENDER_DELAY_MS,
        CRITICS_CORNER_PADDING_OFFSET,
        initAriaLabels,
    };
}

// Also export to window for non-module usage
if (typeof window !== "undefined") {
    window.AffineDrift = {
        scrollToTop,
        debounce,
        generateUniqueId,
        getScrollOffset,
        runOnDomReady,
        runWhenIdle,
    };
}
