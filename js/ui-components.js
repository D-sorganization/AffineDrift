/**
 * AffineDrift - UI Components Module
 * Handles interactive UI elements: accordions, lightbox, back-to-top, etc.
 */

import { debounce, CRITICS_CORNER_PADDING_OFFSET, MATHJAX_RENDER_DELAY_MS } from "./utils.js";

const SCROLL_THRESHOLD = 300;

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
        const observerOptions = { threshold: 0.1, rootMargin: "0px 0px 0px 0px" };
        const observer = new IntersectionObserver(function (entries) {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = "1";
                    entry.target.style.transform = "translateY(0)";
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        // ⚡ Bolt Optimization: Use getElementsByTagName (O(1)) and manual filtering instead of global querySelectorAll (O(N))
        const allSections = document.getElementsByTagName("section");
        const animationStates = [];

        for (const section of allSections) {
            if (!section.classList.contains("page-header") && !section.classList.contains("article-section")) {
                const rect = section.getBoundingClientRect();
                animationStates.push({
                    section,
                    shouldAnimate: rect.top > window.innerHeight,
                });
            }
        }

        animationStates.forEach(({ section, shouldAnimate }) => {
            if (shouldAnimate) {
                section.style.opacity = "0";
                section.style.transform = "translateY(20px)";
                section.style.transition = "opacity 0.4s ease, transform 0.4s ease";
                observer.observe(section);
            } else {
                section.style.opacity = "1";
                section.style.transform = "translateY(0)";
            }
        });
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
    let index = 0;
    for (const header of accordionHeaders) {
        const content = header.nextElementSibling;
        if (content && content.classList.contains("accordion-content")) {
            if (!content.id) {
                content.id = `accordion-content-${index}`;
            }
            header.setAttribute("aria-controls", content.id);
            const isExpanded = header.getAttribute("aria-expanded") === "true";
            content.setAttribute("aria-hidden", !isExpanded);
        }
        index++;
    }

    document.addEventListener("click", (e) => {
        const header = e.target.closest(".accordion-header");
        if (!header) return;

        const content = header.nextElementSibling;
        if (content && content.classList.contains("accordion-content")) {
            const isExpanded = header.getAttribute("aria-expanded") === "true";
            header.setAttribute("aria-expanded", !isExpanded);
            content.setAttribute("aria-hidden", isExpanded);
        }
    });
}

/**
 * Initialize back to top button with progress ring
 */
export function initBackToTop() {
    const backToTopBtn = document.createElement("button");
    backToTopBtn.className = "back-to-top";
    backToTopBtn.setAttribute("aria-label", "Scroll to top");

    const radius = 21;
    const circumference = 2 * Math.PI * radius;

    backToTopBtn.innerHTML = `
    <svg class="progress-ring" width="48" height="48" viewBox="0 0 48 48" aria-hidden="true">
      <circle
        class="progress-ring-circle"
        stroke="white"
        stroke-width="3"
        fill="transparent"
        r="${radius}"
        cx="24"
        cy="24"
        style="stroke-dasharray: ${circumference}; stroke-dashoffset: ${circumference};"
      />
    </svg>
    <svg class="back-to-top-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true">
      <path d="M12 4l-8 8h6v8h4v-8h6z"/>
    </svg>
    <span class="tooltip">Back to top</span>
  `;
    document.body.appendChild(backToTopBtn);

    const progressCircle = backToTopBtn.querySelector(".progress-ring-circle");
    let isScrollTicking = false;
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

    function updateScrollProgress() {
        const scrollTop = window.scrollY;

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

        isScrollTicking = false;
    }

    function onScroll() {
        if (!isScrollTicking) {
            window.requestAnimationFrame(updateScrollProgress);
            isScrollTicking = true;
        }
    }

    window.addEventListener("scroll", onScroll, { passive: true });
    updateScrollProgress();

    backToTopBtn.addEventListener("click", () => {
        window.scrollTo({
            top: 0,
            behavior: "smooth",
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
    exportToPdfBtn.className = "export-to-pdf";
    exportToPdfBtn.setAttribute("aria-label", "Export page to PDF");
    exportToPdfBtn.innerHTML = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
      <polyline points="14 2 14 8 20 8"></polyline>
      <line x1="12" y1="18" x2="12" y2="12"></line>
      <line x1="9" y1="15" x2="15" y2="15"></line>
    </svg>
    <span class="tooltip">Export to PDF</span>
  `;
    document.body.appendChild(exportToPdfBtn);

    function updateExportButtonVisibility() {
        const scrollTop = window.scrollY;
        const shouldBeVisible = scrollTop > SCROLL_THRESHOLD;
        if (shouldBeVisible) {
            exportToPdfBtn.classList.add("visible");
        } else {
            exportToPdfBtn.classList.remove("visible");
        }
    }

    window.addEventListener(
        "scroll",
        debounce(updateExportButtonVisibility, 100),
        { passive: true }
    );
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
    closeBtn.className = "lightbox-close";
    closeBtn.setAttribute("aria-label", "Close zoom");
    closeBtn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>`;

    function closeLightbox() {
        lightbox.classList.remove("active");
        lightbox.setAttribute("aria-hidden", "true");
        lightbox.innerHTML = "";
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

        const focusableSelector =
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';
        const focusableContent = lightbox.querySelectorAll(focusableSelector);

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
        if (img.closest("a") || img.closest("button")) continue;
        img.classList.add("zoomable");
        img.setAttribute("tabindex", "0");
        img.setAttribute("role", "button");
        img.setAttribute("aria-label", "Zoom image");
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

        lightbox.innerHTML = "";
        lightbox.appendChild(clone);
        lightbox.appendChild(closeBtn);

        const figure = img.closest("figure");
        let captionAdded = false;

        if (figure) {
            const figcaption = figure.querySelector("figcaption");
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
    let index = 0;
    for (const corner of criticsCorners) {
        const header = corner.querySelector(".critics-corner-header");
        const content = corner.querySelector(".critics-corner-content");

        if (header && content) {
            if (!content.id) {
                content.id = `critics-corner-content-${index + 1}`;
            }

            header.setAttribute("aria-controls", content.id);

            const isExpandedInitial = header.getAttribute("aria-expanded") === "true";
            content.setAttribute("aria-hidden", String(!isExpandedInitial));

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
                } else {
                    content.style.maxHeight =
                        content.scrollHeight + CRITICS_CORNER_PADDING_OFFSET + "px";
                    content.style.paddingTop = "1rem";
                    content.style.paddingBottom = "1rem";
                    header.setAttribute("aria-expanded", "true");
                    content.setAttribute("aria-hidden", "false");
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
    let index = 0;
    for (const section of laymansSections) {
        const header = section.querySelector(".laymans-terms-header");
        const content = section.querySelector(".laymans-terms-content");

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

        header.addEventListener("click", () => {
            const expanded = header.getAttribute("aria-expanded") === "true";
            header.setAttribute("aria-expanded", String(!expanded));
            content.setAttribute("aria-hidden", String(expanded));
        });
        index++;
    }
}

/**
 * Initialize Critics Comments toggle
 */
export function initCriticsCommentsToggle() {
    const criticsSections = document.getElementsByClassName("critics-comments");
    let index = 0;
    for (const section of criticsSections) {
        const header = section.querySelector(".critics-comments-header");
        const content = section.querySelector(".critics-comments-content");

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

        header.addEventListener("click", () => {
            const expanded = header.getAttribute("aria-expanded") === "true";
            header.setAttribute("aria-expanded", String(!expanded));
            content.setAttribute("aria-hidden", String(expanded));
        });
        index++;
    }
}
