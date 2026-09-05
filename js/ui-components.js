/**
 * AffineDrift - UI Components Module
 * Handles interactive UI elements: accordions, lightbox, back-to-top, etc.
 */

import { debounce, CRITICS_CORNER_PADDING_OFFSET, MATHJAX_RENDER_DELAY_MS } from "./utils.js";

const SCROLL_THRESHOLD = 300;

// ⚡ Bolt Optimization: Batch scroll event listeners to prevent layout thrashing
const scrollCallbacks = new Set();
let isScrollTicking = false;

function handleGlobalScroll() {
    if (!isScrollTicking) {
        window.requestAnimationFrame(processCallbacks);
        isScrollTicking = true;
    }
}

function processCallbacks() {
    const scrollTop = window.scrollY;
    for (const cb of scrollCallbacks) {
        cb(scrollTop);
    }
    isScrollTicking = false;
}

export function registerScrollCallback(callback) {
    if (scrollCallbacks.size === 0) {
        window.addEventListener("scroll", handleGlobalScroll, { passive: true });
    }
    scrollCallbacks.add(callback);
}

export function unregisterScrollCallback(callback) {
    scrollCallbacks.delete(callback);
    if (scrollCallbacks.size === 0) {
        window.removeEventListener("scroll", handleGlobalScroll);
    }
}

function prefersReducedMotion() {
    return (
        typeof window.matchMedia === "function" &&
        window.matchMedia("(prefers-reduced-motion: reduce)").matches
    );
}

/**
 * Initialize fade-in animations for sections
 */
export function initFadeAnimations() {
    const NAV_BREAKPOINT = 768;
    const isMobile = window.innerWidth <= NAV_BREAKPOINT;
    const prefersReducedMotion = window.matchMedia(
        "(prefers-reduced-motion: reduce)"
    ).matches;

    if (!isMobile && !prefersReducedMotion) {
        // Long textbook sections may never fit 10% of their area in a viewport.
        // Reveal on any intersection, including anchors into nested subsections.
        const observerOptions = { threshold: 0, rootMargin: "0px 0px 0px 0px" };
        const observer = new IntersectionObserver(function (entries) {
            for (const entry of entries) {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = "1";
                    entry.target.style.transform = "translateY(0)";
                    observer.unobserve(entry.target);
                }
            }
        }, observerOptions);

        // ⚡ Bolt Optimization: Use getElementsByTagName (O(1)) and manual filtering instead of global querySelectorAll (O(N))
        const allSections = document.getElementsByTagName("section");
        const animationStates = [];

        // ⚡ Bolt Optimization: Batch DOM reads (getBoundingClientRect) and writes (style changes) to prevent Layout Thrashing
        for (const section of allSections) {
            if (!section.classList.contains("page-header") && !section.classList.contains("article-section")) {
                animationStates.push({
                    section,
                    top: section.getBoundingClientRect().top
                });
            }
        }

        const windowHeight = window.innerHeight;
        for (const { section, top } of animationStates) {
            if (top > windowHeight) {
                section.style.opacity = "0";
                section.style.transform = "translateY(20px)";
                section.style.transition = "opacity 0.4s ease, transform 0.4s ease";
                observer.observe(section);
            } else {
                section.style.opacity = "1";
                section.style.transform = "translateY(0)";
            }
        }
    } else {
        // ⚡ Bolt Optimization: Use getElementsByTagName (O(1) live collection) instead of querySelectorAll (O(N))
        const allSections = document.getElementsByTagName("section");
        for (const section of allSections) {
            section.style.opacity = "1";
            section.style.transform = "translateY(0)";
            section.style.visibility = "visible";
        }
    }
}

/**
 * Initialize lazy loading for images
 */
export function initLazyImages() {
    // ⚡ Bolt Optimization: Use document.images (O(1)) instead of querySelectorAll (O(N))
    for (const img of document.images) {
        if (img.getAttribute("loading") === "lazy") {
            if (img.complete) {
                img.classList.add("loaded");
            } else {
                img.addEventListener("load", function () {
                    this.classList.add("loaded");
                });
                img.addEventListener("error", function () {
                    this.classList.add("loaded");
                });
            }
        }
    }

    if ("loading" in HTMLImageElement.prototype) {
        for (const img of document.images) {
            if (img.src && !img.hasAttribute("loading")) {
                img.setAttribute("loading", "lazy");
            }
        }
    }

    if ("loading" in HTMLIFrameElement.prototype) {
        const iframes = document.getElementsByTagName("iframe");
        for (const iframe of iframes) {
            if (iframe.src && !iframe.hasAttribute("loading")) {
                iframe.setAttribute("loading", "lazy");
            }
        }
    }
}

/**
 * Initialize accordion functionality
 */
export function initAccordions() {
    const accordionHeaders = document.getElementsByClassName("accordion-header");

    const updateHeaderAria = (header, isExpanded) => {
        const titleSpan = header.querySelector("span:not(.accordion-icon)");
        const titleText = titleSpan ? titleSpan.textContent.trim() : "content";
        const actionText = isExpanded ? "Collapse" : "Expand";
        header.setAttribute("title", `${actionText} ${titleText}`);
        header.setAttribute("aria-label", `${actionText} ${titleText}`);
    };

    let index = 0;
    for (const header of accordionHeaders) {
        const content = header.nextElementSibling;
        if (content && content.classList.contains("accordion-content")) {
            if (!content.id) {
                content.id = `accordion-content-${index}`;
            }
            header.setAttribute("aria-controls", content.id);
            const isExpanded = header.getAttribute("aria-expanded") === "true";
            content.setAttribute("aria-hidden", String(!isExpanded));
            updateHeaderAria(header, isExpanded);
        }
        index++;
    }

    document.addEventListener("click", (e) => {
        const header = e.target.closest(".accordion-header");
        if (!header) return;

        const content = header.nextElementSibling;
        if (content && content.classList.contains("accordion-content")) {
            const isExpanded = header.getAttribute("aria-expanded") === "true";
            header.setAttribute("aria-expanded", String(!isExpanded));
            content.setAttribute("aria-hidden", String(isExpanded));
            updateHeaderAria(header, !isExpanded);
        }
    });
}

/**
 * Initialize back to top button with progress ring
 */
export function initBackToTop() {
    const backToTopBtn = document.createElement("button");
    backToTopBtn.type = "button";
    backToTopBtn.className = "back-to-top";
    backToTopBtn.setAttribute("aria-label", "Scroll to top");
    backToTopBtn.setAttribute("title", "Scroll to top");

    const radius = 21;
    const circumference = 2 * Math.PI * radius;

    const svgProgress = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svgProgress.setAttribute("class", "progress-ring");
    svgProgress.setAttribute("width", "48");
    svgProgress.setAttribute("height", "48");
    svgProgress.setAttribute("viewBox", "0 0 48 48");
    svgProgress.setAttribute("aria-hidden", "true");

    const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    circle.setAttribute("class", "progress-ring-circle");
    circle.setAttribute("stroke", "white");
    circle.setAttribute("stroke-width", "3");
    circle.setAttribute("fill", "transparent");
    circle.setAttribute("r", String(radius));
    circle.setAttribute("cx", "24");
    circle.setAttribute("cy", "24");
    circle.style.strokeDasharray = `${circumference}`;
    circle.style.strokeDashoffset = `${circumference}`;
    svgProgress.appendChild(circle);

    const svgArrow = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svgArrow.setAttribute("class", "back-to-top-icon");
    svgArrow.setAttribute("viewBox", "0 0 24 24");
    svgArrow.setAttribute("aria-hidden", "true");

    const pathArrow = document.createElementNS("http://www.w3.org/2000/svg", "path");
    pathArrow.setAttribute("d", "M12 4l-8 8h6v8h4v-8h6z");
    svgArrow.appendChild(pathArrow);

    const spanTooltip = document.createElement("span");
    spanTooltip.className = "tooltip";
    spanTooltip.textContent = "Back to top";

    backToTopBtn.append(svgProgress, svgArrow, spanTooltip);
    document.body.appendChild(backToTopBtn);

    const progressCircle = backToTopBtn.querySelector(".progress-ring-circle");
    let isBackToTopVisible = false;
    let maxScroll = 0;

    const updateGeometry = () => {
        maxScroll = document.documentElement.scrollHeight - window.innerHeight;
    };

    updateGeometry();
    window.addEventListener("resize", debounce(updateGeometry, 250));

    if (typeof ResizeObserver !== "undefined") {
        const resizeObserver = new ResizeObserver(
            debounce(() => {
                updateGeometry();
            }, 250)
        );
        resizeObserver.observe(document.body);
    }

    function updateScrollProgress(scrollTop = window.scrollY) {
        const shouldBeVisible = scrollTop > SCROLL_THRESHOLD;
        if (shouldBeVisible !== isBackToTopVisible) {
            isBackToTopVisible = shouldBeVisible;
            if (shouldBeVisible) {
                backToTopBtn.classList.add("visible");
            } else {
                backToTopBtn.classList.remove("visible");
            }
        }

        if (maxScroll > 0) {
            const scrollPercent = Math.min(scrollTop / maxScroll, 1);
            const offset = circumference - scrollPercent * circumference;
            progressCircle.style.strokeDashoffset = offset;
        }
    }

    registerScrollCallback(updateScrollProgress);
    updateScrollProgress();

    backToTopBtn.addEventListener("click", () => {
        window.scrollTo({
            top: 0,
            behavior: prefersReducedMotion() ? "auto" : "smooth",
        });
        document.body.setAttribute("tabindex", "-1");
        document.body.focus({ preventScroll: true });
        document.body.addEventListener(
            "blur",
            () => {
                document.body.removeAttribute("tabindex");
            },
            { once: true }
        );
    });
}

/**
 * Initialize export to PDF button
 */
export function initExportToPdf() {
    const exportToPdfBtn = document.createElement("button");
    exportToPdfBtn.type = "button";
    exportToPdfBtn.className = "export-to-pdf";
    exportToPdfBtn.setAttribute("aria-label", "Export page to PDF");
    exportToPdfBtn.setAttribute("title", "Export page to PDF");
    const svgExport = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svgExport.setAttribute("viewBox", "0 0 24 24");
    svgExport.setAttribute("fill", "none");
    svgExport.setAttribute("stroke", "currentColor");
    svgExport.setAttribute("stroke-width", "2");
    svgExport.setAttribute("stroke-linecap", "round");
    svgExport.setAttribute("stroke-linejoin", "round");
    svgExport.setAttribute("aria-hidden", "true");

    const pathExport = document.createElementNS("http://www.w3.org/2000/svg", "path");
    pathExport.setAttribute("d", "M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z");

    const polylineExport = document.createElementNS("http://www.w3.org/2000/svg", "polyline");
    polylineExport.setAttribute("points", "14 2 14 8 20 8");

    const line1Export = document.createElementNS("http://www.w3.org/2000/svg", "line");
    line1Export.setAttribute("x1", "12"); line1Export.setAttribute("y1", "18"); line1Export.setAttribute("x2", "12"); line1Export.setAttribute("y2", "12");

    const line2Export = document.createElementNS("http://www.w3.org/2000/svg", "line");
    line2Export.setAttribute("x1", "9"); line2Export.setAttribute("y1", "15"); line2Export.setAttribute("x2", "15"); line2Export.setAttribute("y2", "15");

    svgExport.append(pathExport, polylineExport, line1Export, line2Export);

    const spanExportTooltip = document.createElement("span");
    spanExportTooltip.className = "tooltip";
    spanExportTooltip.textContent = "Export to PDF";

    exportToPdfBtn.append(svgExport, spanExportTooltip);
    document.body.appendChild(exportToPdfBtn);

    let isExportToPdfVisible = false;

    function updateExportButtonVisibility(scrollTop = window.scrollY) {
        const shouldBeVisible = scrollTop > SCROLL_THRESHOLD;
        if (shouldBeVisible !== isExportToPdfVisible) {
            isExportToPdfVisible = shouldBeVisible;
            if (shouldBeVisible) {
                exportToPdfBtn.classList.add("visible");
            } else {
                exportToPdfBtn.classList.remove("visible");
            }
        }
    }

    registerScrollCallback(updateExportButtonVisibility);
    updateExportButtonVisibility();

    exportToPdfBtn.addEventListener("click", () => {
        const mathjaxDelay =
            typeof MathJax !== "undefined" ? MATHJAX_RENDER_DELAY_MS : 0;

        document.body.classList.add("printing");

        setTimeout(() => {
            window.print();
            window.addEventListener(
                "afterprint",
                () => {
                    document.body.classList.remove("printing");
                },
                { once: true }
            );
            setTimeout(() => {
                document.body.classList.remove("printing");
            }, 1000);
        }, mathjaxDelay);
    });
}

/**
 * Initialize lightbox for article images
 */
export function initLightbox() {
    const articleContainer = document.getElementById("quarto-document-content");
    if (!articleContainer) return;

    const contentImages = articleContainer.getElementsByTagName("img");
    let lastFocusedElement = null;

    const lightbox = document.createElement("div");
    lightbox.className = "lightbox-overlay";
    lightbox.setAttribute("tabindex", "-1");
    lightbox.style.outline = "none";
    lightbox.setAttribute("aria-hidden", "true");
    lightbox.setAttribute("role", "dialog");
    lightbox.setAttribute("aria-modal", "true");
    lightbox.setAttribute("aria-label", "Image zoom");

    const closeBtn = document.createElement("button");
    closeBtn.type = "button";
    closeBtn.className = "lightbox-close";
    closeBtn.setAttribute("aria-label", "Close zoom (Esc)");
    closeBtn.setAttribute("title", "Close zoom (Esc)");
    const svgClose = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svgClose.setAttribute("width", "24"); svgClose.setAttribute("height", "24");
    svgClose.setAttribute("viewBox", "0 0 24 24"); svgClose.setAttribute("fill", "none");
    svgClose.setAttribute("stroke", "currentColor"); svgClose.setAttribute("stroke-width", "2");
    svgClose.setAttribute("stroke-linecap", "round"); svgClose.setAttribute("stroke-linejoin", "round");
    svgClose.setAttribute("aria-hidden", "true");
    const cl1 = document.createElementNS("http://www.w3.org/2000/svg", "line");
    cl1.setAttribute("x1", "18"); cl1.setAttribute("y1", "6"); cl1.setAttribute("x2", "6"); cl1.setAttribute("y2", "18");
    const cl2 = document.createElementNS("http://www.w3.org/2000/svg", "line");
    cl2.setAttribute("x1", "6"); cl2.setAttribute("y1", "6"); cl2.setAttribute("x2", "18"); cl2.setAttribute("y2", "18");
    svgClose.append(cl1, cl2);
    closeBtn.appendChild(svgClose);

    function closeLightbox() {
        lightbox.classList.remove("active");
        lightbox.setAttribute("aria-hidden", "true");
        lightbox.textContent = "";
        if (lastFocusedElement) {
            lastFocusedElement.focus();
            lastFocusedElement = null;
        }
    }

    lightbox.addEventListener("click", (e) => {
        if (e.target !== lightbox) return;
        closeLightbox();
    });

    closeBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        closeLightbox();
    });

    lightbox.addEventListener("keydown", (e) => {
        if (e.key !== "Tab") return;

        // ⚡ Bolt Optimization: Use getElementsByTagName (O(1) live collection) and manual filtering instead of querySelectorAll (O(N))
        const elements = lightbox.getElementsByTagName('*');
        const focusableContent = [];
        for (const el of elements) {
            const tag = el.tagName;
            if (tag === 'BUTTON' || tag === 'INPUT' || tag === 'SELECT' || tag === 'TEXTAREA') {
                if (!el.disabled && el.tabIndex >= 0) focusableContent.push(el);
            } else if (tag === 'A' && el.hasAttribute('href')) {
                if (el.tabIndex >= 0) focusableContent.push(el);
            } else if (el.hasAttribute('tabindex') && el.getAttribute('tabindex') !== '-1') {
                focusableContent.push(el);
            }
        }

        if (focusableContent.length === 0) return;

        const firstFocusable = focusableContent[0];
        const lastFocusable = focusableContent[focusableContent.length - 1];

        if (e.shiftKey) {
            if (document.activeElement === firstFocusable) {
                lastFocusable.focus();
                e.preventDefault();
            }
        } else {
            if (document.activeElement === lastFocusable) {
                firstFocusable.focus();
                e.preventDefault();
            }
        }
    });

    document.body.appendChild(lightbox);

    for (const img of contentImages) {
        if (img.closest("a, button")) continue;
        img.classList.add("zoomable");
        img.setAttribute("tabindex", "0");
        img.setAttribute("role", "button");
        img.setAttribute("aria-label", "Zoom image");
        img.setAttribute("title", "Zoom image");
    }

    const handleLightboxTrigger = (e) => {
        const img = e.target.closest(".zoomable");
        if (!img) return;
        if (!articleContainer.contains(img)) return;
        if (e.type === "keydown" && e.key !== "Enter" && e.key !== " ") return;

        e.preventDefault();
        lastFocusedElement = document.activeElement;

        const clone = img.cloneNode();
        clone.className = "lightbox-img";
        clone.removeAttribute("loading");
        clone.removeAttribute("id");
        clone.removeAttribute("tabindex");
        clone.removeAttribute("role");
        clone.removeAttribute("aria-label");
        clone.classList.remove("zoomable");

        lightbox.textContent = "";
        lightbox.appendChild(clone);
        lightbox.appendChild(closeBtn);

        const figure = img.closest("figure");
        let captionAdded = false;

        if (figure) {
            // ⚡ Bolt Optimization: Replace descendant querySelector with native getElementsByTagName lookup for O(1) evaluation without CSS parsing overhead in interactive path
            const figcaption = figure.getElementsByTagName("figcaption")[0];
            if (figcaption) {
                const captionClone = figcaption.cloneNode(true);
                captionClone.className = "lightbox-caption";
                lightbox.appendChild(captionClone);
                captionAdded = true;
            }
        }

        if (!captionAdded && img.alt) {
            const altCaption = document.createElement("div");
            altCaption.className = "lightbox-caption";
            altCaption.textContent = img.alt;
            lightbox.appendChild(altCaption);
        }

        lightbox.classList.add("active");
        lightbox.setAttribute("aria-hidden", "false");
        closeBtn.focus();
    };

    articleContainer.addEventListener("click", handleLightboxTrigger);
    articleContainer.addEventListener("keydown", handleLightboxTrigger);

    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && lightbox.classList.contains("active")) {
            closeLightbox();
        }
    });
}

/**
 * Initialize Critics Corner toggle
 */
export function initCriticsCorner() {
    const criticsCorners = document.getElementsByClassName("critics-corner");

    const updateHeaderAria = (header, isExpanded) => {
        const titleSpan = header.querySelector(".critics-corner-title, span:not(.critics-corner-icon)");
        const titleText = titleSpan ? titleSpan.textContent.trim() : "Critics' Corner";
        const actionText = isExpanded ? "Collapse" : "Expand";
        header.setAttribute("title", `${actionText} ${titleText}`);
        header.setAttribute("aria-label", `${actionText} ${titleText}`);
    };

    let index = 0;
    for (const corner of criticsCorners) {
        const header = corner.getElementsByClassName("critics-corner-header")[0];
        const content = corner.getElementsByClassName("critics-corner-content")[0];

        if (header && content) {
            if (!content.id) {
                content.id = `critics-corner-content-${index + 1}`;
            }

            header.setAttribute("aria-controls", content.id);

            const isExpandedInitial = header.getAttribute("aria-expanded") === "true";
            content.setAttribute("aria-hidden", String(!isExpandedInitial));
            updateHeaderAria(header, isExpandedInitial);

            content.style.maxHeight = "0";
            content.style.overflow = "hidden";
            content.style.transition =
                "max-height 0.4s ease-out, padding 0.4s ease-out";

            header.addEventListener("click", function () {
                const isExpanded = header.getAttribute("aria-expanded") === "true";

                if (isExpanded) {
                    content.style.maxHeight = "0";
                    content.style.paddingTop = "0";
                    content.style.paddingBottom = "0";
                    header.setAttribute("aria-expanded", "false");
                    content.setAttribute("aria-hidden", "true");
                    updateHeaderAria(header, false);
                } else {
                    content.style.maxHeight =
                        content.scrollHeight + CRITICS_CORNER_PADDING_OFFSET + "px";
                    content.style.paddingTop = "1rem";
                    content.style.paddingBottom = "1rem";
                    header.setAttribute("aria-expanded", "true");
                    content.setAttribute("aria-hidden", "false");
                    updateHeaderAria(header, true);
                }
            });
        }
        index++;
    }
}

/**
 * Initialize Layman's Terms toggle
 */
export function initLaymansTermsToggle() {
    const laymansSections = document.getElementsByClassName("laymans-terms");

    const updateHeaderAria = (header, isExpanded) => {
        const titleSpan = header.querySelector(".laymans-terms-header-title");
        const titleText = titleSpan ? titleSpan.textContent.trim() : "In Layman's Terms";
        const actionText = isExpanded ? "Collapse" : "Expand";
        header.setAttribute("title", `${actionText} ${titleText}`);
        header.setAttribute("aria-label", `${actionText} ${titleText}`);
    };

    let index = 0;
    for (const section of laymansSections) {
        const header = section.getElementsByClassName("laymans-terms-header")[0];
        const content = section.getElementsByClassName("laymans-terms-content")[0];

        if (!header || !content) {
            index++;
            continue;
        }

        if (!content.id) {
            content.id = `laymans-terms-content-${index + 1}`;
        }

        header.setAttribute("aria-controls", content.id);
        const isExpanded = header.getAttribute("aria-expanded") === "true";
        content.setAttribute("aria-hidden", String(!isExpanded));
        updateHeaderAria(header, isExpanded);

        header.addEventListener("click", () => {
            const expanded = header.getAttribute("aria-expanded") === "true";
            header.setAttribute("aria-expanded", String(!expanded));
            content.setAttribute("aria-hidden", String(expanded));
            updateHeaderAria(header, !expanded);
        });
        index++;
    }
}

/**
 * Initialize Critics Comments toggle
 */
export function initCriticsCommentsToggle() {
    const criticsSections = document.getElementsByClassName("critics-comments");

    const updateHeaderAria = (header, isExpanded) => {
        const titleSpan = header.querySelector(".critics-comments-header-title");
        const titleText = titleSpan ? titleSpan.textContent.trim() : "Critics' Comments";
        const actionText = isExpanded ? "Collapse" : "Expand";
        header.setAttribute("title", `${actionText} ${titleText}`);
        header.setAttribute("aria-label", `${actionText} ${titleText}`);
    };

    let index = 0;
    for (const section of criticsSections) {
        const header = section.getElementsByClassName("critics-comments-header")[0];
        const content = section.getElementsByClassName("critics-comments-content")[0];

        if (!header || !content) {
            index++;
            continue;
        }

        if (!content.id) {
            content.id = `critics-comments-content-${index + 1}`;
        }

        header.setAttribute("aria-controls", content.id);
        const isExpanded = header.getAttribute("aria-expanded") === "true";
        content.setAttribute("aria-hidden", String(!isExpanded));
        updateHeaderAria(header, isExpanded);

        header.addEventListener("click", () => {
            const expanded = header.getAttribute("aria-expanded") === "true";
            header.setAttribute("aria-expanded", String(!expanded));
            content.setAttribute("aria-hidden", String(expanded));
            updateHeaderAria(header, !expanded);
        });
        index++;
    }
}
