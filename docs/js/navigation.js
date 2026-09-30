/**
 * AffineDrift - Navigation Module
 * Handles smooth scrolling, anchor links, navbar, and TOC
 */

import {
    HEADER_OFFSET,
    TOC_SCROLL_OFFSET,
    generateUniqueId,
    runWhenIdle,
} from "./utils.js";

/**
 * Initialize smooth scroll for anchor links
 */
export function initSmoothScroll() {
    document.addEventListener("click", function (e) {
        const link = e.target.closest('a[href^="#"]');
        if (link) {
            const href = link.getAttribute("href");
            if (href && href !== "#" && href.length > 1) {
                if (
                    link.hasAttribute("data-bs-toggle") ||
                    link.hasAttribute("data-toggle")
                )
                    return;

                const targetId = href.substring(1);
                const targetElement = document.getElementById(targetId);

                if (targetElement) {
                    e.preventDefault();
                    const elementPosition = targetElement.getBoundingClientRect().top;
                    const offsetPosition =
                        elementPosition + window.scrollY - HEADER_OFFSET;

                    history.pushState(null, null, href);

                    window.scrollTo({
                        top: offsetPosition,
                        behavior: "smooth",
                    });

                    if (!targetElement.hasAttribute("tabindex")) {
                        targetElement.setAttribute("tabindex", "-1");
                    }
                    targetElement.focus({ preventScroll: true });

                    targetElement.classList.remove("target-highlight");
                    void targetElement.offsetWidth;
                    targetElement.classList.add("target-highlight");
                }
            }
        }
    });
}

/**
 * Initialize navbar collapse behavior with unified mobile navigation
 *
 * UNIFIED MOBILE MENU IMPLEMENTATION
 * This consolidates three separate mobile navigation implementations:
 * 1. Quarto navbar (.navbar-toggler) - PRIMARY
 * 2. Legacy custom nav-toggle - REMOVED
 * 3. Homepage mobile-menu-toggle - CONSOLIDATED
 *
 * All mobile menus now use Quarto's navbar with enhanced keyboard support.
 * Handles: click collapse, keyboard navigation (Escape, arrows), ARIA attributes.
 */
export function initNavbarCollapse() {
    const navbarCollapse = document.getElementById("navbarCollapse");
    const navbarToggler = document.querySelector(".navbar-toggler");

    // ⚡ Bolt Optimization: Use scoped getElementsByTagName instead of iterating document.links and calling .closest() to prevent excessive JS-to-C++ boundary crossings
    const navLinks = [];
    const navbarNavs = document.getElementsByClassName("navbar-nav");
    if (navbarNavs.length > 0) {
        const links = navbarNavs[0].getElementsByTagName("a");
        for (const link of links) {
            if (link.classList.contains("nav-link")) {
                navLinks.push(link);
            }
        }
    }

    // Ensure Quarto navbar has proper ARIA attributes
    if (navbarCollapse) {
        navbarCollapse.setAttribute("role", "navigation");
        if (!navbarCollapse.getAttribute("aria-label")) {
            navbarCollapse.setAttribute("aria-label", "Site navigation");
        }
    }

    if (navbarToggler) {
        // Set initial ARIA state on toggle button
        navbarToggler.setAttribute("aria-controls", "navbarCollapse");
        if (!navbarToggler.getAttribute("aria-label") || navbarToggler.getAttribute("aria-label") === "Toggle navigation menu") {
            navbarToggler.setAttribute("aria-label", "Open navigation menu");
            navbarToggler.setAttribute("title", "Open navigation menu");
        }

        // Update ARIA state when menu state changes
        const updateToggleState = () => {
            const isOpen = navbarCollapse && navbarCollapse.classList.contains("show");
            navbarToggler.setAttribute("aria-expanded", String(isOpen));
            const actionText = isOpen ? "Close navigation menu (Esc)" : "Open navigation menu";
            navbarToggler.setAttribute("aria-label", actionText);
            navbarToggler.setAttribute("title", actionText);
        };

        // Listen for collapse changes and update ARIA
        if (navbarCollapse) {
            navbarCollapse.addEventListener("show.bs.collapse", updateToggleState);
            navbarCollapse.addEventListener("hide.bs.collapse", updateToggleState);
            navbarCollapse.addEventListener("shown.bs.collapse", updateToggleState);
            navbarCollapse.addEventListener("hidden.bs.collapse", updateToggleState);
        }

        // Keyboard navigation: Escape key closes menu
        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape" && navbarCollapse && navbarCollapse.classList.contains("show")) {
                const collapseInstance = window.bootstrap?.Collapse?.getInstance
                    ? window.bootstrap.Collapse.getInstance(navbarCollapse)
                    : null;
                if (collapseInstance) {
                    collapseInstance.hide();
                } else {
                    navbarCollapse.classList.remove("show");
                }
                // Return focus to toggle button for accessibility
                if (navbarToggler) {
                    navbarToggler.focus();
                }
            }
        });

        // Arrow key navigation within menu
        if (navbarCollapse) {
            navbarCollapse.addEventListener("keydown", (e) => {
                if (["ArrowDown", "ArrowUp", "Home", "End"].includes(e.key) && navLinks.length > 0) {
                    e.preventDefault();
                    const focusedIndex = navLinks.findIndex(link => link === document.activeElement);
                    let nextIndex = 0;

                    switch (e.key) {
                        case "ArrowDown":
                            nextIndex = focusedIndex === -1 ? 0 : Math.min(focusedIndex + 1, navLinks.length - 1);
                            break;
                        case "ArrowUp":
                            nextIndex = focusedIndex <= 0 ? navLinks.length - 1 : focusedIndex - 1;
                            break;
                        case "Home":
                            nextIndex = 0;
                            break;
                        case "End":
                            nextIndex = navLinks.length - 1;
                            break;
                    }

                    if (navLinks[nextIndex]) {
                        navLinks[nextIndex].focus();
                    }
                }
            });
        }
    }

    // Close menu when a nav link is clicked (maintains existing behavior)
    for (const link of navLinks) {
        const href = link.getAttribute("href");
        if (href && href.startsWith("#")) {
            link.addEventListener("click", () => {
                if (navbarCollapse && navbarCollapse.classList.contains("show")) {
                    const collapseInstance = window.bootstrap?.Collapse?.getInstance
                        ? window.bootstrap.Collapse.getInstance(navbarCollapse)
                        : null;
                    if (collapseInstance) {
                        collapseInstance.hide();
                    } else {
                        navbarCollapse.classList.remove("show");
                    }
                }
            });
        }
    }
}

/**
 * Generate Table of Contents from page headings
 */
export function generateTableOfContents() {
    const leftSidebar = document.querySelector(".left-sidebar");
    const sidebar = leftSidebar || document.getElementById("history-sidebar");
    if (!sidebar) return;
    // Authored TOCs are the page contract. Generating a second list beside
    // one creates duplicate navigation and competing IDs.
    if (leftSidebar?.querySelector(".toc-nav")) return;

    let tocSection;
    if (leftSidebar) {
        tocSection = leftSidebar.querySelector(".sidebar-toc");
        if (!tocSection) {
            tocSection = document.createElement("div");
            tocSection.className = "sidebar-toc";
            const h3 = document.createElement("h3");
            h3.className = "sidebar-heading";
            h3.textContent = "On This Page";
            const ul = document.createElement("ul");
            ul.className = "sidebar-links";
            ul.id = "toc-list";
            tocSection.append(h3, ul);
            const existingTocNav = leftSidebar.querySelector(".toc-nav");
            if (existingTocNav) {
                existingTocNav.insertAdjacentElement("afterend", tocSection);
            } else {
                leftSidebar.insertBefore(tocSection, leftSidebar.firstChild);
            }
        }
    } else {
        const sidebarNav = sidebar.querySelector(".sidebar-nav");
        if (!sidebarNav) return;
        tocSection = sidebar.querySelector(".sidebar-toc");
        if (!tocSection) {
            tocSection = document.createElement("div");
            tocSection.className = "sidebar-section sidebar-toc";
            const h3 = document.createElement("h3");
            h3.className = "sidebar-heading";
            h3.textContent = "On This Page";
            const ul = document.createElement("ul");
            ul.className = "sidebar-links";
            ul.id = "toc-list";
            tocSection.append(h3, ul);
            sidebarNav.insertBefore(tocSection, sidebarNav.firstChild);
        }
    }

    const tocList = document.getElementById("toc-list");
    if (!tocList) return;
    tocList.textContent = "";

    const sections = [];
    const usedIds = new Set();

    // ⚡ Bolt Optimization: Use live collections instead of querySelectorAll for O(1) collection fetching
    const sectionTags = document.getElementsByTagName("section");
    const pageSectionClasses = document.getElementsByClassName("page-section");
    const pageSections = new Set([...sectionTags, ...pageSectionClasses]);
    for (const section of pageSections) {
        if (!section.id) continue;
        const heading = section.querySelector(".section-heading, h2, h1");
        if (heading && section.id) {
            sections.push({
                id: section.id,
                text: heading.textContent.trim(),
                level: 2,
            });
            usedIds.add(section.id);
        }
    }

    // ⚡ Bolt Optimization: Use getElementsByClassName (O(1) live collection) instead of querySelectorAll (O(N))
    const categories = document.getElementsByClassName("article-category");
    for (const category of categories) {
        const heading = category.getElementsByTagName("h3")[0];
        if (heading) {
            let id = category.id;
            if (!id) {
                id = generateUniqueId(heading.textContent, usedIds);
                category.id = id;
            } else if (usedIds.has(id)) {
                id = generateUniqueId(id, usedIds);
                category.id = id;
            }
            usedIds.add(id);
            sections.push({
                id: id,
                text: heading.textContent.trim(),
                level: 2,
            });
        }
    }

    if (sections.length === 0) {
        // ⚡ Bolt Optimization: Use getElementsByTagName (O(1) live collection) instead of querySelectorAll (O(N))
        const h2s = document.getElementsByTagName("h2");
        let index = 0;
        for (const h2 of h2s) {
            let id = h2.id;
            if (!id || usedIds.has(id)) {
                id = generateUniqueId(
                    h2.textContent || `section-${index + 1}`,
                    usedIds
                );
                h2.id = id;
            }
            usedIds.add(id);
            sections.push({
                id: id,
                text: h2.textContent.trim(),
                level: 2,
            });
            index++;
        }
    }

    if (sections.length > 0) {
        const fragment = document.createDocumentFragment();
        for (const section of sections) {
            const li = document.createElement("li");
            const a = document.createElement("a");
            a.href = `#${section.id}`;
            a.textContent = section.text;
            a.className = `toc-level-${section.level}`;
            li.appendChild(a);
            fragment.appendChild(li);
        }
        tocList.appendChild(fragment);
    } else {
        if (tocSection) tocSection.style.display = "none";
        else if (tocList) tocList.style.display = "none";
    }
}

/**
 * Initialize anchor links for headings
 */
export function initAnchorLinks() {
    const mainArea = document.querySelector(".main-content-area");
    if (!mainArea) return;
    const h2s = mainArea.getElementsByTagName("h2");
    const h3s = mainArea.getElementsByTagName("h3");
    const headings = [...h2s, ...h3s];

    const usedIds = new Set();

    const anchorIcon = document.createElementNS(
        "http://www.w3.org/2000/svg",
        "svg"
    );
    anchorIcon.setAttribute("aria-hidden", "true");
    anchorIcon.setAttribute("width", "18");
    anchorIcon.setAttribute("height", "18");
    anchorIcon.setAttribute("viewBox", "0 0 24 24");
    anchorIcon.setAttribute("fill", "none");
    anchorIcon.setAttribute("stroke", "currentColor");
    anchorIcon.setAttribute("stroke-width", "2");
    anchorIcon.setAttribute("stroke-linecap", "round");
    anchorIcon.setAttribute("stroke-linejoin", "round");
    const path1 = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path1.setAttribute("d", "M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71");
    const path2 = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path2.setAttribute("d", "M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71");
    anchorIcon.append(path1, path2);

    for (const heading of headings) {
        // ⚡ Bolt Optimization: Replace descendant querySelector with native getElementsByClassName lookup for O(1) evaluation without CSS parsing overhead
        if (heading.getElementsByClassName("anchor-link")[0]) continue;

        if (!heading.id) {
            heading.id = generateUniqueId(heading.textContent, usedIds);
            usedIds.add(heading.id);
        }

        const anchor = document.createElement("a");
        anchor.className = "anchor-link";
        anchor.href = `#${heading.id}`;
        anchor.setAttribute("aria-label", "Link to this section");
        anchor.setAttribute("title", "Link to this section");
        anchor.appendChild(anchorIcon.cloneNode(true));

        heading.appendChild(anchor);
    }
}

/**
 * Calculate the true document-relative top offset of an element.
 * Immune to intermediate positioned offsetParent containers (#4370).
 *
 * @param {HTMLElement} element
 * @returns {number}
 */
export function getDocumentOffsetTop(element) {
    if (!element) return 0;
    if (typeof element.getBoundingClientRect === "function") {
        const rect = element.getBoundingClientRect();
        const scrollY =
            window.pageYOffset ||
            window.scrollY ||
            document.documentElement.scrollTop ||
            0;
        const docTop = rect.top + scrollY;
        // In rendered browser contexts, bounding rect reliably returns document position
        if (rect.height > 0 || rect.width > 0 || !element.offsetParent) {
            return docTop;
        }
    }

    // Fallback for headless/JSDOM environments without full CSS layout:
    const rawDescriptor = Object.getOwnPropertyDescriptor(
        HTMLElement.prototype,
        "offsetTop"
    );
    let top = 0;
    let curr = element;
    while (curr) {
        if (curr._rawOffsetTop !== undefined) {
            top += curr._rawOffsetTop;
        } else if (rawDescriptor && rawDescriptor.get) {
            top += rawDescriptor.get.call(curr);
        } else {
            top += curr.offsetTop || 0;
        }
        curr = curr.offsetParent;
    }
    return top;
}

/**
 * Patches offsetTop on target sections so that vendor scripts (such as Quarto's
 * updateActiveLink) that read section.offsetTop directly calculate true
 * document-relative positions rather than parent-relative offsets when sections
 * are nested inside positioned/contained ancestors (#4370).
 *
 * @param {HTMLElement[]} sections
 */
export function patchTocSectionsOffsetTop(sections) {
    const rawDescriptor = Object.getOwnPropertyDescriptor(
        HTMLElement.prototype,
        "offsetTop"
    );
    for (const section of sections) {
        if (!section || section.__hasPatchedOffsetTop) continue;

        if (
            section.offsetTop !== undefined &&
            section._rawOffsetTop === undefined
        ) {
            try {
                section._rawOffsetTop =
                    rawDescriptor && rawDescriptor.get
                        ? rawDescriptor.get.call(section)
                        : section.offsetTop;
            } catch {
                section._rawOffsetTop = 0;
            }
        }

        Object.defineProperty(section, "offsetTop", {
            get() {
                return getDocumentOffsetTop(this);
            },
            configurable: true,
            enumerable: true,
        });
        section.__hasPatchedOffsetTop = true;
    }
}

/**
 * Initialize ScrollSpy for Table of Contents
 * Supports both custom #toc-list and Quarto's #TOC navigation (#4370).
 */
export function initScrollSpy() {
    const tocContainer =
        document.getElementById("toc-list") ||
        document.getElementById("TOC") ||
        document.querySelector('nav[role="doc-toc"]');
    if (!tocContainer) return;

    // Collect all links in TOC: both a[data-scroll-target] (Quarto) and a[href^="#"]
    const tocLinks = Array.from(
        tocContainer.querySelectorAll('a[data-scroll-target], a[href^="#"]')
    );
    if (tocLinks.length === 0) return;

    const linkMap = new Map();
    const targetSections = [];
    const seenSectionIds = new Set();

    for (const link of tocLinks) {
        const rawTarget =
            link.getAttribute("data-scroll-target") || link.getAttribute("href");
        if (rawTarget && rawTarget.startsWith("#") && rawTarget.length > 1) {
            let id;
            try {
                id = decodeURI(rawTarget.slice(1));
            } catch {
                id = rawTarget.slice(1);
            }
            linkMap.set(id, link);
            if (!seenSectionIds.has(id)) {
                seenSectionIds.add(id);
                const el = document.getElementById(id);
                if (el) {
                    targetSections.push(el);
                }
            }
        }
    }

    if (targetSections.length === 0) {
        // Fallback: collect sections by tags and classes if direct IDs not in TOC
        const sectionTags = document.getElementsByTagName("section");
        const pageSectionClasses =
            document.getElementsByClassName("page-section");
        const fallbackSections = Array.from(
            new Set([...sectionTags, ...pageSectionClasses])
        ).filter((s) => s.id && linkMap.has(s.id));
        targetSections.push(...fallbackSections);
    }

    if (targetSections.length === 0) return;

    // Patch offsetTop on TOC target sections so Quarto's updateActiveLink calculates true document-relative offsets
    patchTocSectionsOffsetTop(targetSections);

    let currentActiveLink = null;

    const setActiveLink = (newActiveLink) => {
        if (newActiveLink && newActiveLink !== currentActiveLink) {
            if (currentActiveLink) {
                currentActiveLink.classList.remove("active");
                currentActiveLink.removeAttribute("aria-current");
            }
            newActiveLink.classList.add("active");
            newActiveLink.setAttribute("aria-current", "location");
            currentActiveLink = newActiveLink;
        }
    };

    const updateActiveLink = () => {
        const scrollY =
            window.pageYOffset ||
            window.scrollY ||
            document.documentElement.scrollTop ||
            0;
        const scrollHeight = Math.max(
            document.body.scrollHeight || 0,
            document.documentElement.scrollHeight || 0,
            document.body.offsetHeight || 0,
            document.documentElement.offsetHeight || 0
        );
        const windowHeight =
            window.innerHeight || document.documentElement.clientHeight || 800;

        let activeSection = null;
        // If at the very bottom of the page on a scrollable document, activate the last section
        if (
            scrollHeight > windowHeight &&
            windowHeight + scrollY >= scrollHeight - 20 &&
            targetSections.length > 0
        ) {
            activeSection = targetSections[targetSections.length - 1];
        } else {
            const sectionMargin = 200; // Matches Quarto's sectionMargin
            // Find the last section that has scrolled past the margin threshold
            for (let i = targetSections.length - 1; i >= 0; i--) {
                const section = targetSections[i];
                const docTop = getDocumentOffsetTop(section);
                if (scrollY >= docTop - sectionMargin) {
                    activeSection = section;
                    break;
                }
            }
            if (!activeSection && targetSections.length > 0) {
                activeSection = targetSections[0];
            }
        }

        if (activeSection) {
            const link = linkMap.get(activeSection.id);
            if (link) {
                setActiveLink(link);
            }
        }
    };

    // Leading-edge throttled update on scroll and resize (16ms = ~60fps)
    let lastScrollTime = 0;
    let scrollTimer = null;
    const throttledUpdate = () => {
        const now = Date.now();
        const remaining = 16 - (now - lastScrollTime);
        if (remaining <= 0 || remaining > 16) {
            if (scrollTimer) {
                clearTimeout(scrollTimer);
                scrollTimer = null;
            }
            lastScrollTime = now;
            updateActiveLink();
        } else if (!scrollTimer) {
            scrollTimer = setTimeout(() => {
                lastScrollTime = Date.now();
                scrollTimer = null;
                updateActiveLink();
            }, remaining);
        }
    };

    window.addEventListener("scroll", throttledUpdate, { passive: true });
    window.addEventListener("resize", throttledUpdate, { passive: true });

    // Initial update
    updateActiveLink();

    // Preserve IntersectionObserver for platforms that use it
    if (typeof IntersectionObserver === "function") {
        const observer = new IntersectionObserver(() => {
            updateActiveLink();
        }, {
            root: null,
            rootMargin: "-100px 0px -60% 0px",
            threshold: 0,
        });

        for (const section of targetSections) {
            observer.observe(section);
        }
    }
}


/**
 * Initialize skip to content link for accessibility
 */
export function initSkipToContent() {
    if (document.querySelector(".skip-to-content")) return;

    // Resolve the best available main-content target. Standard article pages
    // expose #quarto-document-content, but full-layout pages (e.g. the home
    // page) may not, so fall back to the <main> element or #quarto-content.
    const candidates = ["#quarto-document-content", "main", "#quarto-content"];
    let target = null;
    for (const selector of candidates) {
        const el = document.querySelector(selector);
        if (el) {
            target = el;
            break;
        }
    }
    if (target && !target.id) {
        target.id = "main-content";
    }
    const targetId = target ? target.id : "quarto-document-content";

    const skipLink = document.createElement("a");
    skipLink.href = `#${targetId}`;
    skipLink.className = "skip-to-content";
    skipLink.textContent = "Skip to main content";
    skipLink.setAttribute("aria-label", "Skip to main content");

    skipLink.addEventListener("click", (e) => {
        const targetId = skipLink.getAttribute("href").substring(1);
        const targetElement = document.getElementById(targetId);
        if (targetElement) {
            if (!targetElement.getAttribute("tabindex")) {
                targetElement.setAttribute("tabindex", "-1");
            }
            targetElement.focus({ preventScroll: true });
        }
    });

    if (document.body.firstChild) {
        document.body.insertBefore(skipLink, document.body.firstChild);
    } else {
        document.body.appendChild(skipLink);
    }
}
