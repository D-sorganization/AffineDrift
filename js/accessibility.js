/**
 * AffineDrift - Accessibility Module
 * Handles all accessibility features and ARIA labels
 */

import { runOnDomReady, debounce } from "./utils.js";
import { registerScrollCallback } from "./ui-components.js";

/**
 * Secure external links with proper attributes
 */
export function initSecureExternalLinks() {
    const currentHostname = window.location.hostname;
    for (const link of document.links) {
        if (
            link.hostname &&
            link.hostname !== currentHostname &&
            link.protocol.startsWith("http")
        ) {
            // ⚡ Bolt Optimization: Use property access and DOMTokenList
            // Avoids O(N) memory allocation from string split/join for every external link
            if (!link.target) {
                link.target = "_blank";
            }

            if (link.relList) {
                link.relList.add("noopener", "noreferrer");
            } else {
                const rel = link.getAttribute("rel") || "";
                const parts = rel.split(" ").filter((p) => p);
                if (!parts.includes("noopener")) parts.push("noopener");
                if (!parts.includes("noreferrer")) parts.push("noreferrer");
                link.setAttribute("rel", parts.join(" "));
            }

            if (
                link.getElementsByTagName("img").length === 0 &&
                link.getElementsByTagName("svg").length === 0 &&
                !link.classList.contains("external-link")
            ) {
                link.classList.add("external-link");
                const icon = document.createElement("span");
                icon.className = "external-link-icon";
                icon.setAttribute("aria-hidden", "true");
                const svgIcon = document.createElementNS("http://www.w3.org/2000/svg", "svg");
                svgIcon.setAttribute("width", "12"); svgIcon.setAttribute("height", "12");
                svgIcon.setAttribute("viewBox", "0 0 24 24"); svgIcon.setAttribute("fill", "none");
                svgIcon.setAttribute("stroke", "currentColor"); svgIcon.setAttribute("stroke-width", "2");
                svgIcon.setAttribute("stroke-linecap", "round"); svgIcon.setAttribute("stroke-linejoin", "round");

                const pathIcon = document.createElementNS("http://www.w3.org/2000/svg", "path");
                pathIcon.setAttribute("d", "M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6");

                const polylineIcon = document.createElementNS("http://www.w3.org/2000/svg", "polyline");
                polylineIcon.setAttribute("points", "15 3 21 3 21 9");

                const lineIcon = document.createElementNS("http://www.w3.org/2000/svg", "line");
                lineIcon.setAttribute("x1", "10"); lineIcon.setAttribute("y1", "14"); lineIcon.setAttribute("x2", "21"); lineIcon.setAttribute("y2", "3");

                svgIcon.append(pathIcon, polylineIcon, lineIcon);
                icon.appendChild(svgIcon);
                link.appendChild(icon);
            }
        }
    }
}

/**
 * Set external links on GitHub repos
 */
export function initRepoLinks() {
    // ⚡ Bolt Optimization: Scope tag lookup to specific container instead of iterating document.links and calling .closest() to prevent excessive JS-to-C++ boundary crossings
    const navbarNavs = document.getElementsByClassName("navbar-nav");
    for (const nav of navbarNavs) {
        const links = nav.getElementsByTagName("a");
        for (const link of links) {
            if (link.href.startsWith("https://github.com")) {
                link.setAttribute("target", "_blank");
            }
        }
    }
}

const NAV_LABEL_RULES = Object.freeze([
    { className: "toc-nav", label: "Table of contents navigation" },
    { className: "history-nav", label: "Recent history navigation" },
    { className: "resources-nav", label: "Resources navigation" },
]);

const SIDEBAR_LABEL_RULES = Object.freeze([
    { className: "left-sidebar", label: "Left sidebar navigation" },
    { className: "right-sidebar", label: "Right sidebar navigation" },
    { className: "home-sidebar", label: "Main navigation sidebar" },
]);

function resolveLabelFromClasses(element, rules, fallbackLabel) {
    for (const rule of rules) {
        if (element.classList.contains(rule.className)) {
            return rule.label;
        }
    }
    return fallbackLabel;
}

function applyDefaultAriaLabel(element, label) {
    if (!element.hasAttribute("aria-label")) {
        element.setAttribute("aria-label", label);
    }
}

function labelCardsFromHeading(cards, prefix) {
    for (const card of cards) {
        if (card.hasAttribute("aria-label")) continue;
        const heading = card.getElementsByTagName("h3")[0];
        if (heading) {
            card.setAttribute("aria-label", `${prefix}: ${heading.textContent.trim()}`);
        }
    }
}

/**
 * Initialize all ARIA labels for accessibility
 */
export function initAriaLabels() {
    // ⚡ Bolt Optimization: Use getElementsByTagName and getElementsByClassName
    // (O(1) Live Collections) instead of querySelectorAll (O(N) Traversal)

    // Navigation elements
    const navElements = document.getElementsByTagName("nav");
    for (const nav of navElements) {
        applyDefaultAriaLabel(
            nav,
            resolveLabelFromClasses(nav, NAV_LABEL_RULES, "Navigation")
        );
    }

    // Sidebar elements
    const sidebars = document.getElementsByTagName("aside");
    for (const sidebar of sidebars) {
        applyDefaultAriaLabel(
            sidebar,
            resolveLabelFromClasses(sidebar, SIDEBAR_LABEL_RULES, "Sidebar")
        );
    }

    // Main content areas
    const mainElements = document.getElementsByTagName("main");
    for (const main of mainElements) {
        if (!main.hasAttribute("aria-label") && !main.hasAttribute("role")) {
            main.setAttribute("role", "main");
            main.setAttribute("aria-label", "Main content");
        }
    }


    // Single pass over all inputs
    const inputs = document.getElementsByTagName("input");
    for (const input of inputs) {
        // Search inputs
        if (input.type === "search" && !input.hasAttribute("aria-label") && !input.id) {
            input.setAttribute("aria-label", "Search");
        }

        // Form inputs without labels
        if (!input.hasAttribute("aria-label") && !input.id) {
            const placeholder = input.getAttribute("placeholder");
            if (placeholder) {
                input.setAttribute("aria-label", placeholder);
            }
        }
    }

    // Social links
    const socialLinks = document.getElementsByClassName("social-link");
    for (const link of socialLinks) {
        const text = link.textContent.trim();
        const labelText = `Visit ${text}`;
        if (!link.hasAttribute("aria-label")) {
            link.setAttribute("aria-label", labelText);
        }
        if (!link.hasAttribute("title")) {
            link.setAttribute("title", labelText);
        }
    }

    // Resource cards
    const resourceCards = document.getElementsByClassName("resource-card");
    labelCardsFromHeading(resourceCards, "Resource");

    // Article cards
    const articleCards = document.getElementsByClassName("article-card");
    labelCardsFromHeading(articleCards, "Article");

    // History lists - live regions
    // ⚡ Bolt Optimization: Use getElementsByTagName (O(1) live collection) and manual filtering instead of querySelectorAll (O(N))
    const uls = document.getElementsByTagName("ul");
    for (const list of uls) {
        if (list.id && list.id.endsWith("-history-list")) {
            if (!list.hasAttribute("aria-live")) {
                list.setAttribute("aria-live", "polite");
                list.setAttribute("aria-atomic", "false");
            }
        }
    }
}

/**
 * Initialize reading time estimate for articles
 */
export function initReadingTime() {
    if (!window.location.pathname.includes("/articles/")) return;

    const articleContent = document.getElementById("quarto-document-content");
    if (!articleContent) return;

    const text = articleContent.textContent || articleContent.innerText;

    let wordCount = 0;
    let inWord = false;
    const len = text.length;
    for (let i = 0; i < len; i++) {
        const c = text.charCodeAt(i);
        if (
            c === 32 ||
            c === 9 ||
            c === 10 ||
            c === 13 ||
            c === 160 ||
            c === 12
        ) {
            inWord = false;
        } else {
            if (!inWord) wordCount++;
            inWord = true;
        }
    }

    const wordsPerMinute = 225;
    const minutes = Math.ceil(wordCount / wordsPerMinute);

    const timeDiv = document.createElement("div");
    timeDiv.className = "reading-time-estimate";
    const svgClock = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svgClock.setAttribute("width", "16"); svgClock.setAttribute("height", "16");
    svgClock.setAttribute("fill", "currentColor"); svgClock.setAttribute("class", "bi bi-clock");
    svgClock.setAttribute("viewBox", "0 0 16 16"); svgClock.setAttribute("aria-hidden", "true");
    svgClock.style.verticalAlign = "text-bottom"; svgClock.style.marginRight = "5px"; svgClock.style.opacity = "0.8";

    const path1Clock = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path1Clock.setAttribute("d", "M8 3.5a.5.5 0 0 0-1 0V9a.5.5 0 0 0 .252.434l3.5 2a.5.5 0 0 0 .496-.868L8 8.71V3.5z");

    const path2Clock = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path2Clock.setAttribute("d", "M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm7-8A7 7 0 1 1 1 8a7 7 0 0 1 14 0z");

    svgClock.append(path1Clock, path2Clock);

    const spanText = document.createElement("span");
    spanText.textContent = `${minutes} min read`;

    timeDiv.append(svgClock, spanText);

    Object.assign(timeDiv.style, {
        marginBottom: "1.5rem",
        color: "var(--text-light)",
        fontStyle: "italic",
        display: "flex",
        alignItems: "center",
        fontSize: "0.95rem",
        fontWeight: "500",
    });

    timeDiv.setAttribute(
        "aria-label",
        `Estimated reading time: ${minutes} minutes`
    );

    const header =
        articleContent.querySelector(
            ":scope > header.quarto-title-block#title-block-header"
        ) ||
        articleContent.querySelector("header.quarto-title-block#title-block-header");
    const isHeaderVisible = header && header.offsetParent !== null;

    if (isHeaderVisible) {
        const meta = header.querySelector(".quarto-title-meta");
        if (meta) {
            meta.appendChild(timeDiv);
        } else {
            header.appendChild(timeDiv);
        }
    } else {
        articleContent.insertBefore(timeDiv, articleContent.firstChild);
    }
}

/**
 * Reading-progress indicator: a thin fixed bar at the top of the viewport that
 * fills as the reader scrolls an article (issue #3334). Article pages only;
 * skipped when the user prefers reduced motion.
 */
export function initReadingProgress() {
    if (!window.location.pathname.includes("/articles/")) return;

    const article =
        document.getElementById("quarto-document-content") ||
        document.querySelector("main");
    if (!article) return;

    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    const bar = document.createElement("div");
    bar.className = "reading-progress";
    bar.setAttribute("role", "presentation");
    bar.setAttribute("aria-hidden", "true");
    document.body.appendChild(bar);

    let docHeight = 0;
    const updateGeometry = () => {
        docHeight = document.documentElement.scrollHeight - window.innerHeight;
    };
    updateGeometry();

    let lastRatio = -1;
    function update(scrollTop = window.scrollY) {
        const ratio = docHeight > 0 ? scrollTop / docHeight : 0;
        const boundedRatio = Math.min(Math.max(ratio, 0), 1);
        if (boundedRatio !== lastRatio) {
            bar.style.transform = `scaleX(${boundedRatio})`;
            lastRatio = boundedRatio;
        }
    }

    const debouncedUpdateGeometry = debounce(() => {
        updateGeometry();
        window.requestAnimationFrame(() => update());
    }, 250);

    function handleResize() {
        debouncedUpdateGeometry();
    }

    if (typeof ResizeObserver !== "undefined") {
        const resizeObserver = new ResizeObserver(debouncedUpdateGeometry);
        resizeObserver.observe(document.body);
    }

    registerScrollCallback(update);
    window.addEventListener("resize", handleResize, { passive: true });
    update();
}

/**
 * Accessibility Phase 2: Motion preferences (prefers-reduced-motion)
 */
export function initMotionPreferences() {
    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (prefersReduced) {
        document.documentElement.setAttribute('data-motion-reduced', 'true');
    }

    // Listen for changes
    window.matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change', (e) => {
        if (e.matches) {
            document.documentElement.setAttribute('data-motion-reduced', 'true');
        } else {
            document.documentElement.removeAttribute('data-motion-reduced');
        }
    });
}

/**
 * Accessibility Phase 2: High contrast mode support
 */
export function initHighContrastMode() {
    const prefersContrast = window.matchMedia('(prefers-contrast: more)').matches;

    if (prefersContrast) {
        document.documentElement.setAttribute('data-high-contrast', 'true');
    }

    window.matchMedia('(prefers-contrast: more)').addEventListener('change', (e) => {
        if (e.matches) {
            document.documentElement.setAttribute('data-high-contrast', 'true');
        } else {
            document.documentElement.removeAttribute('data-high-contrast');
        }
    });
}

/**
 * Accessibility Phase 2: Focus management
 * Ensure focus is properly managed and visible
 */
export function initFocusManagement() {
    // Add visual indicator for keyboard navigation
    let isKeyboardUsing = false;

    document.addEventListener('keydown', () => {
        if (!isKeyboardUsing) {
            isKeyboardUsing = true;
            document.body.setAttribute('data-keyboard-active', 'true');
        }
    });

    document.addEventListener('mousedown', () => {
        if (isKeyboardUsing) {
            isKeyboardUsing = false;
            document.body.removeAttribute('data-keyboard-active');
        }
    });

    // Trap focus in modals if any exist
    const modals = document.querySelectorAll('[role="dialog"]');
    for (const modal of modals) {
        // ⚡ Bolt Optimization: Use getElementsByTagName (O(1) live collection) and manual filtering instead of querySelectorAll (O(N))
        const elements = modal.getElementsByTagName('*');
        const focusableElements = [];
        for (const el of elements) {
            const tag = el.tagName;
            if (tag === 'BUTTON' || tag === 'INPUT' || tag === 'SELECT' || tag === 'TEXTAREA') {
                if (!el.disabled && el.tabIndex >= 0) focusableElements.push(el);
            } else if (tag === 'A' && el.hasAttribute('href')) {
                if (el.tabIndex >= 0) focusableElements.push(el);
            } else if (el.hasAttribute('tabindex') && el.getAttribute('tabindex') !== '-1') {
                focusableElements.push(el);
            }
        }

        if (focusableElements.length > 0) {
            const firstElement = focusableElements[0];
            const lastElement = focusableElements[focusableElements.length - 1];

            modal.addEventListener('keydown', (e) => {
                if (e.key === 'Tab') {
                    if (e.shiftKey && document.activeElement === firstElement) {
                        lastElement.focus();
                        e.preventDefault();
                    } else if (!e.shiftKey && document.activeElement === lastElement) {
                        firstElement.focus();
                        e.preventDefault();
                    }
                }
            });
        }
    }
}

/**
 * Screen reader announcement helper
 */
export function announce(message, priority = 'polite') {
    let liveRegion = document.querySelector(`[aria-live="${priority}"]`);

    if (!liveRegion) {
        liveRegion = document.createElement('div');
        liveRegion.setAttribute('aria-live', priority);
        liveRegion.setAttribute('aria-atomic', 'true');
        liveRegion.className = 'sr-only';
        document.body.appendChild(liveRegion);
    }

    liveRegion.textContent = message;
}
