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
 * Initialize navbar collapse behavior
 */
export function initNavbarCollapse() {
    const navbarCollapse = document.getElementById("navbarCollapse");
    // ⚡ Bolt Optimization: Use document.links (O(1)) instead of querySelectorAll (O(N))
    for (const link of document.links) {
        if (
            link.classList.contains("nav-link") &&
            link.closest(".navbar-nav")
        ) {
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
}

/**
 * Generate Table of Contents from page headings
 */
export function generateTableOfContents() {
    const leftSidebar = document.querySelector(".left-sidebar");
    const sidebar = leftSidebar || document.getElementById("history-sidebar");
    if (!sidebar) return;

    let tocSection;
    if (leftSidebar) {
        tocSection = leftSidebar.querySelector(".sidebar-toc");
        if (!tocSection) {
            tocSection = document.createElement("div");
            tocSection.className = "sidebar-toc";
            tocSection.innerHTML =
                '<h3 class="sidebar-heading">On This Page</h3><ul class="sidebar-links" id="toc-list"></ul>';
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
            tocSection.innerHTML =
                '<h3 class="sidebar-heading">On This Page</h3><ul class="sidebar-links" id="toc-list"></ul>';
            sidebarNav.insertBefore(tocSection, sidebarNav.firstChild);
        }
    }

    const tocList = document.getElementById("toc-list");
    if (!tocList) return;
    tocList.innerHTML = "";

    const sections = [];
    const usedIds = new Set();

    const pageSections = document.querySelectorAll(
        ".page-section[id], section[id]"
    );
    pageSections.forEach((section) => {
        const heading = section.querySelector(".section-heading, h2, h1");
        if (heading && section.id) {
            sections.push({
                id: section.id,
                text: heading.textContent.trim(),
                level: 2,
            });
            usedIds.add(section.id);
        }
    });

    // ⚡ Bolt Optimization: Use getElementsByClassName (O(1) live collection) instead of querySelectorAll (O(N))
    const categories = document.getElementsByClassName("article-category");
    for (const category of categories) {
        const heading = category.querySelector("h3");
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
        sections.forEach((section) => {
            const li = document.createElement("li");
            const a = document.createElement("a");
            a.href = `#${section.id}`;
            a.textContent = section.text;
            a.className = `toc-level-${section.level}`;
            li.appendChild(a);
            fragment.appendChild(li);
        });
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
    const headings = document.querySelectorAll(
        ".main-content-area h2, .main-content-area h3"
    );

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
    anchorIcon.innerHTML =
        '<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>';

    headings.forEach((heading) => {
        if (heading.querySelector(".anchor-link")) return;

        if (!heading.id) {
            heading.id = generateUniqueId(heading.textContent, usedIds);
            usedIds.add(heading.id);
        }

        const anchor = document.createElement("a");
        anchor.className = "anchor-link";
        anchor.href = `#${heading.id}`;
        anchor.setAttribute("aria-label", "Link to this section");
        anchor.appendChild(anchorIcon.cloneNode(true));

        heading.appendChild(anchor);
    });
}

/**
 * Initialize ScrollSpy for Table of Contents
 */
export function initScrollSpy() {
    const tocList = document.getElementById("toc-list");
    if (!tocList) return;
    const tocLinks = tocList.getElementsByTagName("a");
    if (tocLinks.length === 0) return;

    const linkMap = new Map();
    Array.from(tocLinks).forEach((link) => {
        const href = link.getAttribute("href");
        if (href && href.startsWith("#")) {
            linkMap.set(href.substring(1), link);
        }
    });
    let currentActiveLink = null;

    const sections = document.querySelectorAll(
        ".page-section[id], section[id]"
    );

    const sectionIndexMap = new Map();
    sections.forEach((section, index) => {
        sectionIndexMap.set(section.id, index);
    });

    const visibleIndices = new Set();

    const observerOptions = {
        root: null,
        rootMargin: "-100px 0px -60% 0px",
        threshold: 0,
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            const index = sectionIndexMap.get(entry.target.id);
            if (index !== undefined) {
                if (entry.isIntersecting) {
                    visibleIndices.add(index);
                } else {
                    visibleIndices.delete(index);
                }
            }
        });

        let activeId = null;
        if (visibleIndices.size > 0) {
            const firstVisibleIndex = Math.min(...visibleIndices);
            if (firstVisibleIndex >= 0 && firstVisibleIndex < sections.length) {
                activeId = sections[firstVisibleIndex].id;
            }
        }

        if (activeId) {
            const newActiveLink = linkMap.get(activeId);
            if (newActiveLink && newActiveLink !== currentActiveLink) {
                if (currentActiveLink) {
                    currentActiveLink.classList.remove("active");
                    currentActiveLink.removeAttribute("aria-current");
                }
                newActiveLink.classList.add("active");
                newActiveLink.setAttribute("aria-current", "location");
                currentActiveLink = newActiveLink;
            }
        }
    }, observerOptions);

    sections.forEach((section) => {
        if (linkMap.has(section.id)) {
            observer.observe(section);
        }
    });
}

/**
 * Initialize skip to content link for accessibility
 */
export function initSkipToContent() {
    if (document.querySelector(".skip-to-content")) return;

    const skipLink = document.createElement("a");
    skipLink.href = "#quarto-document-content";
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
